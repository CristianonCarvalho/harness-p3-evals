"""Converte o stream-json do `claude -p` para o formato de trace do P3 (D5).

Decisoes que vieram da amostra real de 2026-11-11 (achados na Tarefa 12 do plano):
- `events` guarda so as chamadas ao P2 (`mcp__taxlaw__*`). `Skill` e `ToolSearch`
  vao para `other_tools`, sem resultado: o texto da skill traz ids e daria
  lastro falso ao C1.
- O init tem de mostrar so as ferramentas e os servers permitidos; senao o trace
  e `erro`. `--setting-sources project` nao isola a execucao.
- `input_tokens` soma a entrada sem cache, a escrita e a leitura de cache.
- Tipo de evento desconhecido e ignorado; linha ruim ou stream cortado viram `erro`,
  nunca excecao.
"""
from __future__ import annotations

import json
from typing import Iterable

P2_PREFIX = "mcp__taxlaw__"
P2_SERVER = "taxlaw"
# Subtipos do evento `result` que sao limite atingido (decisao 8 de D2), nao falha.
LIMIT_SUBTYPES = {"error_max_budget_usd", "error_max_turns"}


def _result_raw(content):
    """O resultado pode vir como texto ou como lista de blocos; JSON vira objeto."""
    if isinstance(content, list):
        texto = "".join(b.get("text", "") for b in content if isinstance(b, dict))
    elif isinstance(content, str):
        texto = content
    else:
        return content
    try:
        return json.loads(texto)
    except json.JSONDecodeError:
        return texto


def _usage(ev: dict) -> dict:
    u = ev.get("usage") or {}
    sem_cache = u.get("input_tokens", 0)
    escrita = u.get("cache_creation_input_tokens", 0)
    leitura = u.get("cache_read_input_tokens", 0)
    return {"input_tokens": sem_cache + escrita + leitura,
            "uncached_input_tokens": sem_cache,
            "cache_creation_input_tokens": escrita,
            "cache_read_input_tokens": leitura,
            "output_tokens": u.get("output_tokens", 0),
            "cost_usd": ev.get("total_cost_usd", 0.0),
            "duration_ms": ev.get("duration_ms", 0)}


def _check_init(ev: dict, allowed_tools: set[str], allowed_servers: set[str]) -> list[str]:
    errors = []
    extras = sorted(set(ev.get("tools", [])) - allowed_tools)
    if extras:
        errors.append(f"execucao nao isolada: ferramentas fora da lista: {extras}")
    servers = {s.get("name"): s.get("status") for s in ev.get("mcp_servers", [])}
    extras = sorted(set(servers) - allowed_servers)
    if extras:
        errors.append(f"execucao nao isolada: servers MCP fora da lista: {extras}")
    if servers.get(P2_SERVER) != "connected":
        errors.append(f"server {P2_SERVER} nao conectado: {servers.get(P2_SERVER)!r}")
    return errors


def parse_stream(lines: Iterable[str], *, case_id: str, question: str,
                 conditions: dict, trace_id: str,
                 allowed_tools: set[str], allowed_servers: set[str],
                 synthetic_ids: list[str] | None = None) -> dict:
    """Devolve um trace (D5). Nunca levanta por causa do conteudo do stream."""
    source = {"harness": "claude-code", "version": "", "tools": [], "mcp_servers": []}
    model = "desconhecido"
    pendentes: dict[str, dict] = {}
    events: list[dict] = []
    other_tools: list[dict] = []
    final_answer = ""
    usage = _usage({})
    errors: list[str] = []
    saw_init = saw_result = False
    limit = False
    bad_lines = 0

    for raw in lines:
        raw = raw.strip()
        if not raw:
            continue
        try:
            ev = json.loads(raw)
        except json.JSONDecodeError:
            bad_lines += 1
            continue
        if not isinstance(ev, dict):
            bad_lines += 1
            continue
        tipo = ev.get("type")
        if tipo == "system" and ev.get("subtype") == "init":
            saw_init = True
            model = ev.get("model", model)
            source["version"] = ev.get("claude_code_version", "")
            source["tools"] = list(ev.get("tools", []))
            source["mcp_servers"] = [s.get("name") for s in ev.get("mcp_servers", [])]
            errors += _check_init(ev, allowed_tools, allowed_servers)
        elif tipo == "assistant":
            for b in (ev.get("message") or {}).get("content") or []:
                if not (isinstance(b, dict) and b.get("type") == "tool_use"):
                    continue
                nome, args = b.get("name", ""), b.get("input") or {}
                if nome.startswith(P2_PREFIX):
                    e = {"tool": nome, "args": args, "result_raw": None, "is_error": False}
                    pendentes[b.get("id", "")] = e
                    events.append(e)
                else:
                    other_tools.append({"tool": nome, "args": args})
        elif tipo == "user":
            conteudo = (ev.get("message") or {}).get("content")
            for b in conteudo if isinstance(conteudo, list) else []:
                if isinstance(b, dict) and b.get("type") == "tool_result":
                    alvo = pendentes.get(b.get("tool_use_id", ""))
                    if alvo is not None:
                        alvo["result_raw"] = _result_raw(b.get("content"))
                        alvo["is_error"] = bool(b.get("is_error"))
        elif tipo == "result":
            saw_result = True
            final_answer = ev.get("result") or ""
            usage = _usage(ev)
            subtype = ev.get("subtype", "")
            if subtype in LIMIT_SUBTYPES:
                limit = True
                errors.append(f"limite atingido: {subtype}")
            elif ev.get("is_error"):
                errors.append(f"execucao terminou com erro: {subtype}")

    if not saw_init:
        errors.append("stream sem evento init")
    if bad_lines:
        errors.append(f"{bad_lines} linha(s) que nao sao JSON")
    if not saw_result:
        errors.append("stream sem evento result (cortado?)")
    sem_resultado = sum(e["result_raw"] is None for e in events)
    if sem_resultado and not limit:
        errors.append(f"{sem_resultado} chamada(s) ao P2 sem resultado")

    if limit:
        status = "estourou_limite"
    else:
        status = "erro" if errors else "ok"
    trace = {
        "trace_id": trace_id, "case_id": case_id, "status": status,
        "source": source, "model": model, "conditions": conditions, "question": question,
        "events": events, "other_tools": other_tools, "final_answer": final_answer,
        "usage": usage, "errors": errors,
    }
    if synthetic_ids:
        trace["synthetic_ids"] = synthetic_ids
    return trace
