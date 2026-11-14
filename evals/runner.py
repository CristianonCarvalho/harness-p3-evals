"""Runner das rodadas (Tarefa 13): roda um caso no Claude Code contra o P2 e grava o trace.

Desenho, com os achados da amostra real de 2026-11-11 (Tarefa 12 do plano):
- Skill ligada ou desligada pelo diretorio de trabalho: uma copia do checkout do P2 na
  tag fixada, com ou sem `.claude/skills/`. O hook (`.claude/settings.json`) fica nas duas.
- Isolamento: `--setting-sources project` deixa de fora `~/.claude`, mas NAO isola
  ferramentas nem servers da conta. Por isso tambem `--strict-mcp-config` com um
  `--mcp-config` so do P2, e `--tools` com o minimo (`Skill` e `ToolSearch`). O adaptador
  recusa o trace se o init mostrar algo alem disso.
- A pergunta vai por stdin: `--allowedTools` aceita varios valores, e uma pergunta no fim
  do argv seria lida como nome de ferramenta.
- A pergunta leva a data de referencia do gabarito; sem ela o modelo usa a data do dia.
- Remoto: URL e token so por variavel de ambiente, nunca escritos no disco.
"""
from __future__ import annotations

import hashlib
import json
import os
import random
import shutil
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

from evals.adapters.claude_code import parse_stream
from evals.budget import BudgetGuard
from evals.privacy import make_synthetic_cnpj, make_synthetic_cpf
from evals.trace import new_trace_id, write_trace

SERVERS = {"local": "taxlaw", "remoto": "taxlaw-remoto"}
BUILTIN_TOOLS = ["Skill", "ToolSearch"]
MCP_CONFIG_NAME = "p3-mcp.json"
REMOTE_ENV = ("TAXLAW_REMOTE_URL", "TAXLAW_HTTP_TOKEN")
DEFAULT_TIMEOUT_S = 900
MAX_ERRORS = 3  # decisao 9 de D2: tres erros seguidos param a repeticao
_IGNORE = shutil.ignore_patterns(".git", ".venv", "traces", "__pycache__", ".pytest_cache")


class RemoteNotConfigured(Exception):
    """Faltam as variaveis de ambiente do server remoto."""


def _server_name(server: str) -> str:
    if server not in SERVERS:
        raise ValueError(f"server invalido: {server!r} (use {sorted(SERVERS)})")
    return SERVERS[server]


def p2_tools(server: str) -> list[str]:
    nome = _server_name(server)
    return [f"mcp__{nome}__buscar_dispositivos", f"mcp__{nome}__obter_dispositivo"]


def build_argv(model: str, *, server: str, max_budget_usd: float, mcp_config: Path) -> list[str]:
    # --include-hook-events: o trace registra se o hook do P2 rodou, em vez de supor.
    return ["claude", "-p", "--output-format", "stream-json", "--verbose",
            "--include-hook-events",
            "--model", model, "--max-budget-usd", str(max_budget_usd),
            "--no-session-persistence", "--setting-sources", "project",
            "--strict-mcp-config", "--mcp-config", str(mcp_config),
            "--tools", ",".join(BUILTIN_TOOLS),
            "--allowedTools", *p2_tools(server)]


def _mcp_config(p2_dir: Path, server: str) -> dict:
    nome = _server_name(server)
    if server == "remoto":
        # O Claude Code expande ${VAR} na hora de conectar: nada secreto vai para o disco.
        cfg = {"type": "http", "url": "${TAXLAW_REMOTE_URL}",
               "headers": {"Authorization": "Bearer ${TAXLAW_HTTP_TOKEN}"}}
    else:
        cfg = json.loads((p2_dir / ".mcp.json").read_text(encoding="utf-8"))["mcpServers"][nome]
    return {"mcpServers": {nome: cfg}}


def prepare_workdir(p2_dir: Path, dest: Path, *, with_skill: bool, server: str) -> Path:
    """Copia o checkout do P2 para `dest`, com ou sem a skill. Nunca reaproveita `dest`
    (o copytree levanta FileExistsError)."""
    config = _mcp_config(p2_dir, server)
    shutil.copytree(p2_dir, dest, ignore=_IGNORE)
    if not with_skill:
        shutil.rmtree(dest / ".claude" / "skills", ignore_errors=True)
    (dest / MCP_CONFIG_NAME).write_text(json.dumps(config, indent=2), encoding="utf-8")
    return dest


def corpus_version(workdir: Path) -> str:
    dados = (workdir / "corpus" / "dispositivos.json").read_bytes()
    return hashlib.sha256(dados).hexdigest()[:12]


def substitute_placeholders(question: str, rng: random.Random) -> tuple[str, list[str]]:
    """Troca cada {CPF}/{CNPJ} por um numero sintetico novo, na ordem em que aparecem."""
    ids: list[str] = []
    partes = question.split("{")
    saida = [partes[0]]
    for parte in partes[1:]:
        for marcador, gerar in (("CPF}", make_synthetic_cpf), ("CNPJ}", make_synthetic_cnpj)):
            if parte.startswith(marcador):
                numero = gerar(rng)
                ids.append(numero)
                saida.append(numero + parte[len(marcador):])
                break
        else:
            saida.append("{" + parte)
    return "".join(saida), ids


def build_prompt(case: dict, rng: random.Random) -> tuple[str, list[str]]:
    pergunta, ids = substitute_placeholders(case["question"], rng)
    data = case["gabarito"]["reference_date"]
    return f"{pergunta}\n\nData de referência: {data}.", ids


def _check_remote_env(server: str) -> None:
    if server == "remoto":
        faltam = [v for v in REMOTE_ENV if not os.environ.get(v)]
        if faltam:
            raise RemoteNotConfigured(
                f"server remoto sem configuracao: defina {', '.join(faltam)} no ambiente")


def run_case(case: dict, *, model: str, server: str, workdir: Path, p2_tag: str,
             traces_dir: Path, guard: BudgetGuard, max_budget_usd: float,
             rng: random.Random, run: Callable = subprocess.run,
             timeout_s: int = DEFAULT_TIMEOUT_S) -> Path:
    """Roda um caso, grava o trace e cobra o custo. Levanta BudgetExceeded depois de gravar."""
    _check_remote_env(server)
    nome = _server_name(server)
    prompt, ids = build_prompt(case, rng)
    argv = build_argv(model, server=server, max_budget_usd=max_budget_usd,
                      mcp_config=(workdir / MCP_CONFIG_NAME).resolve())
    extra_errors: list[str] = []
    try:
        proc = run(argv, input=prompt, capture_output=True, text=True, cwd=workdir,
                   timeout=timeout_s)
        saida, codigo = proc.stdout or "", proc.returncode
        stderr = (proc.stderr or "").strip()
    except subprocess.TimeoutExpired as e:
        stderr = ""
        saida = e.stdout or ""
        if isinstance(saida, bytes):
            saida = saida.decode("utf-8", errors="replace")
        codigo = None
        extra_errors.append(f"tempo maximo de {timeout_s} s atingido")
    conditions = {"skill": (workdir / ".claude" / "skills").exists(),
                  "hook": server == "local" and (workdir / ".claude" / "settings.json").exists(),
                  "server": server, "p2_tag": p2_tag,
                  "corpus_version": corpus_version(workdir)}
    trace = parse_stream(saida.splitlines(), case_id=case["case_id"], question=prompt,
                         conditions=conditions, trace_id=new_trace_id(case["case_id"]),
                         allowed_tools=set(BUILTIN_TOOLS) | set(p2_tools(server)),
                         allowed_servers={nome}, synthetic_ids=ids or None)
    if codigo not in (0, None):
        extra_errors.append(f"claude terminou com codigo de saida {codigo}")
        if stderr:
            # So o fim: e o que diz o motivo, e o stderr do claude nao traz chaves.
            extra_errors.append(f"stderr do claude: {stderr[-300:]}")
    if extra_errors:
        trace["errors"] += extra_errors
        if trace["status"] == "ok":
            trace["status"] = "erro"
    path = write_trace(trace, traces_dir)
    guard.charge(trace["usage"]["cost_usd"])
    return path


@dataclass
class RunResult:
    status: str
    paths: list[Path] = field(default_factory=list)
    investigate: bool = False


def run_with_retries(case: dict, **kwargs) -> RunResult:
    """Repete so o `erro` (infraestrutura). Tres seguidos: para e marca para investigar."""
    result = RunResult(status="erro")
    for _ in range(MAX_ERRORS):
        path = run_case(case, **kwargs)
        result.paths.append(path)
        result.status = json.loads(path.read_text(encoding="utf-8"))["status"]
        if result.status != "erro":
            return result
    result.investigate = True
    return result
