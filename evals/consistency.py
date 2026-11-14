"""Checagens de consistencia dos dados versionados (rodadas em CI, sem rede, sem modelo).

Confere se os dados commitados no repositorio estao coerentes: nenhum numero de
contribuinte, casos validos, anotacoes validas, metricas do juiz iguais a uma
recontagem, regras da amostra cega e um relatorio novo sempre que muda o P2, o modelo
ou o prompt do juiz.

Decisoes deste modulo:
- a recontagem do juiz nao conhece traces disputados (os traces nao estao no git);
  se um caso for marcado como disputado, a recontagem pode divergir do relatorio;
- traces nao estao no git, entao a checagem de anotacoes monta um trace minimo com
  status "ok" (so traces ok se anotam) e case_id = id do trace sem o sufixo de 8 hex;
- "sem relatorio ainda" so e avisado quando config/run.json existe.
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import re
from dataclasses import dataclass, field
from pathlib import Path

from evals.annotation import load_history, validate_annotation
from evals.annotation_drafter import blind_ids
from evals.cases import validate_case
from evals.metrics import VALID_VERDICTS
from evals.privacy import find_taxpayer_ids
from evals.report import MIN_CLASSE_CALIBRACAO
from evals.review_report import JUDGE_CRITERIA, _metricas_juiz
from evals.sampling import load_samples


@dataclass
class RepoCheck:
    problems: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


# Privacidade: o que e varrido e o que e ignorado (uv.lock tem hashes com longas sequencias de digitos).
EXTENSOES_DE_TEXTO = frozenset({
    ".py", ".md", ".json", ".jsonl", ".yaml", ".yml", ".toml", ".txt", ".cfg", ".ini",
})
PASTAS_IGNORADAS = frozenset({
    ".git", ".venv", "traces", "runs", "results", "workdirs", "__pycache__",
    ".pytest_cache", ".superpowers", "node_modules",
})
ARQUIVOS_IGNORADOS = frozenset({"uv.lock"})

PASTAS_DE_ANOTACAO = ("annotations", "annotations/consistency")
CAMPOS_JUIZ = ("tpr", "tnr", "n_pos", "n_neg")
CAMPOS_RUN = ("p2_tag", "models", "judge_model", "judge_prompts_sha256")
TOLERANCIA = 1e-9
_VERSIONADO = re.compile(r"(.+)\.v(\d+)\.json")
_SUFIXO_DO_TRACE = re.compile(r"-[0-9a-f]{8}$")


# Utilitarios


def _rel(caminho: Path, root: Path) -> str:
    return caminho.relative_to(root).as_posix()


def _le_json(caminho: Path, root: Path, problemas: list[str]):
    """Le um JSON. Se falhar, registra o problema com o nome do arquivo e devolve None."""
    try:
        return json.loads(caminho.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        problemas.append(f"{_rel(caminho, root)}: JSON inválido ({exc})")
        return None


def _numero(v) -> bool:
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def _vazio(v) -> bool:
    return v is None or (isinstance(v, (str, list)) and len(v) == 0)


def _ordenada(v):
    return sorted(str(x) for x in v) if isinstance(v, list) else v


def _iguais(a, b) -> bool:
    if a is None or b is None:
        return a is None and b is None
    if _numero(a) and _numero(b):
        return math.isclose(a, b, rel_tol=0.0, abs_tol=TOLERANCIA)
    return a == b


def _ids_versionados(pasta: Path) -> set[str]:
    if not pasta.is_dir():
        return set()
    ids = set()
    for p in pasta.iterdir():
        if p.is_file():
            m = _VERSIONADO.fullmatch(p.name)
            if m:
                ids.add(m.group(1))
    return ids


# 1. Privacidade


def _arquivos_de_texto(root: Path):
    for atual, pastas, arquivos in os.walk(root):
        pastas[:] = [p for p in pastas if p not in PASTAS_IGNORADAS]
        for nome in sorted(arquivos):
            caminho = Path(atual) / nome
            if caminho.suffix in EXTENSOES_DE_TEXTO and nome not in ARQUIVOS_IGNORADOS:
                yield caminho


def scan_privacy(root: Path) -> list[str]:
    """Problemas de privacidade: arquivos com numeros no formato de CPF/CNPJ. Nunca mostra o numero."""
    problemas = []
    for caminho in _arquivos_de_texto(root):
        try:
            texto = caminho.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        n = len(find_taxpayer_ids(texto))
        if n:
            problemas.append(f"{_rel(caminho, root)}: {n} número(s) com formato de CPF/CNPJ")
    return problemas


# 2. Casos


def _check_cases(root: Path, problemas: list[str]) -> dict[str, dict]:
    pasta = root / "cases"
    casos: dict[str, dict] = {}
    if not pasta.is_dir():
        return casos
    arquivos = sorted(p for p in pasta.glob("*.json") if not p.name.startswith("_"))
    for caminho in arquivos:
        nome = _rel(caminho, root)
        dados = _le_json(caminho, root, problemas)
        if dados is None:
            continue
        if not isinstance(dados, dict):
            problemas.append(f"{nome}: o caso deve ser um objeto JSON")
            continue
        try:
            erros = validate_case(dados)
        except (AttributeError, KeyError, TypeError) as exc:
            erros = [f"estrutura inválida ({type(exc).__name__})"]
        problemas += [f"{nome}: {erro}" for erro in erros]
        if dados.get("split") is None:
            problemas.append(f"{nome}: caso sem split (rode apply-splits)")
        if isinstance(dados.get("case_id"), str):
            casos[dados["case_id"]] = dados
    if arquivos:
        meta = pasta / "_split_meta.json"
        if not meta.is_file():
            problemas.append(f"{_rel(meta, root)} ausente (rode apply-splits)")
        else:
            dados_meta = _le_json(meta, root, problemas)
            if dados_meta is not None and not (isinstance(dados_meta, dict) and "seed" in dados_meta):
                problemas.append(f"{_rel(meta, root)} sem seed")
    return casos


# 3. Anotacoes


def _historicos(root: Path, problemas: list[str]) -> dict[str, dict[str, list[dict]]]:
    """{pasta: {trace_id: historico}}. Arquivo de anotacao invalido vira problema aqui, uma vez."""
    saida: dict[str, dict[str, list[dict]]] = {}
    for rel in PASTAS_DE_ANOTACAO:
        pasta = root / rel
        mapa: dict[str, list[dict]] = {}
        for tid in sorted(_ids_versionados(pasta)):
            try:
                mapa[tid] = load_history(pasta, tid)
            except ValueError as exc:
                problemas.append(f"{rel}/{exc}")
        saida[rel] = mapa
    return saida


def _check_anotacoes(casos: dict[str, dict], historicos: dict, problemas: list[str]) -> None:
    for rel, mapa in historicos.items():
        for tid, historico in mapa.items():
            caso_id = _SUFIXO_DO_TRACE.sub("", tid)
            caso = casos.get(caso_id)
            if caso is None:
                problemas.append(f"{rel}/{tid}: caso {caso_id!r} não encontrado em cases/")
                continue
            # Traces nao estao no git; so traces com status ok se anotam, entao ok e assumido.
            trace = {"trace_id": tid, "case_id": caso_id, "status": "ok"}
            for ann in historico:
                nome = f"{rel}/{tid}.v{ann['version']}.json"
                limpa = {k: v for k, v in ann.items() if k not in ("version", "date")}
                problemas += [f"{nome}: {erro}" for erro in validate_annotation(limpa, caso, trace)]


# 4. Juizos


def _check_juizos(root: Path, problemas: list[str]) -> dict[str, dict]:
    pasta = root / "judgments"
    juizos: dict[str, dict] = {}
    if not pasta.is_dir():
        return juizos
    for caminho in sorted(pasta.glob("*.json")):
        nome = _rel(caminho, root)
        dados = _le_json(caminho, root, problemas)
        if dados is None:
            continue
        erros: list[str] = []
        if not isinstance(dados, dict):
            erros.append("deve ser um objeto JSON")
        else:
            if dados.get("trace_id") != caminho.stem:
                erros.append(f"trace_id {dados.get('trace_id')!r} diverge do nome do arquivo "
                             f"({caminho.stem!r})")
            veredictos = dados.get("verdicts")
            if not isinstance(veredictos, dict):
                erros.append("verdicts deve ser um objeto que liga critérios a vereditos")
            else:
                for crit in sorted(set(veredictos) - set(JUDGE_CRITERIA)):
                    erros.append(f"{crit}: critério fora do juiz (use C1, C2, C3 ou C4)")
                for crit, valor in sorted(veredictos.items()):
                    if crit in JUDGE_CRITERIA and valor not in VALID_VERDICTS:
                        erros.append(f"{crit}: veredito inválido {valor!r}")
        problemas += [f"{nome}: {erro}" for erro in erros]
        if not erros:
            juizos[caminho.stem] = dados["verdicts"]
    return juizos


# Amostra e relatorio


def _amostras(root: Path, problemas: list[str]) -> dict:
    caminho = root / "annotations" / "_samples.json"
    if not caminho.is_file():
        return {}
    try:
        dados = load_samples(caminho)
    except ValueError as exc:
        problemas.append(f"{_rel(caminho, root)}: JSON inválido ({exc})")
        return {}
    if not isinstance(dados, dict):
        problemas.append(f"{_rel(caminho, root)}: deve ser um objeto JSON")
        return {}
    return dados


def _relatorio_recente(root: Path, problemas: list[str]) -> tuple[str | None, dict | None]:
    """Nome e conteudo do relatorio de nome ordenado mais alto (o mais recente)."""
    pasta = root / "reports"
    arquivos = sorted(pasta.glob("*.json")) if pasta.is_dir() else []
    if not arquivos:
        return None, None
    caminho = arquivos[-1]
    nome = _rel(caminho, root)
    dados = _le_json(caminho, root, problemas)
    if dados is None:
        return nome, None
    if not isinstance(dados, dict):
        problemas.append(f"{nome}: o relatório deve ser um objeto JSON")
        return nome, None
    return nome, dados


# 5. Recontagem do juiz


def _check_recontagem(root: Path, nome, relatorio, juizos: dict, historicos: dict,
                      amostras: dict, problemas: list[str]) -> None:
    if nome is None or relatorio is None or not (root / "judgments").is_dir():
        return
    humanas = []
    for tid in sorted(blind_ids(amostras)):
        historico = historicos["annotations"].get(tid)
        if historico and historico[-1].get("kind") == "blind":
            humanas.append(historico[-1])
    try:
        recontagem = _metricas_juiz(humanas, juizos, set())
    except ValueError as exc:
        problemas.append(f"{nome}: não foi possível recontar o juiz ({exc})")
        return
    juiz_relatorio = relatorio.get("judge")
    if not isinstance(juiz_relatorio, dict):
        juiz_relatorio = {}
    for crit in JUDGE_CRITERIA:
        reportado = juiz_relatorio.get(crit)
        if not isinstance(reportado, dict):
            reportado = {}
        recontado = recontagem[crit]
        diferencas = [
            f"{campo} {reportado.get(campo)!r} != {recontado[campo]!r}"
            for campo in CAMPOS_JUIZ
            if not _iguais(reportado.get(campo), recontado[campo])
        ]
        if diferencas:
            problemas.append(f"{nome}: juiz {crit} diverge da recontagem em " + "; ".join(diferencas))


# 6. Rascunhos e regras cegas


def _tem_anotacao_cega(pasta: Path, tid: str) -> bool:
    caminho = pasta / f"{tid}.v1.json"
    if not caminho.is_file():
        return False
    try:
        dados = json.loads(caminho.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return False
    return isinstance(dados, dict) and dados.get("kind") == "blind"


def _check_rascunhos(root: Path, amostras: dict, historicos: dict, problemas: list[str]) -> None:
    pasta_rascunhos = root / "drafts" / "annotations"
    # R8: anotacao revisada so existe com o rascunho que a originou.
    for rel, mapa in historicos.items():
        for tid, historico in mapa.items():
            for ann in historico:
                if ann.get("kind") == "revised" and not (pasta_rascunhos / f"{tid}.json").is_file():
                    problemas.append(f"{rel}/{tid}.v{ann['version']}.json: anotação revisada "
                                     f"sem rascunho em drafts/annotations/{tid}.json")
    # R3: rascunho de trace da amostra cega so com a anotacao cega gravada antes.
    if pasta_rascunhos.is_dir():
        cegas = blind_ids(amostras)
        for caminho in sorted(pasta_rascunhos.glob("*.json")):
            tid = caminho.stem
            if tid in cegas and not _tem_anotacao_cega(root / "annotations", tid):
                problemas.append(
                    f"drafts/annotations/{caminho.name}: rascunho de trace cego sem a anotação cega "
                    f"(annotations/{tid}.v1.json com kind blind)")
    # Gabarito rascunhado precisa do caso correspondente.
    pasta_casos = root / "drafts" / "cases"
    if pasta_casos.is_dir():
        for caminho in sorted(pasta_casos.glob("*.json")):
            m = _VERSIONADO.fullmatch(caminho.name)
            if m and not (root / "cases" / f"{m.group(1)}.json").is_file():
                problemas.append(f"drafts/cases/{caminho.name}: gabarito rascunhado sem caso "
                                 f"em cases/{m.group(1)}.json")


# 7. Limiares


def _calibrado(dados: dict) -> bool:
    n_pos, n_neg = dados.get("n_pos"), dados.get("n_neg")
    return (_numero(n_pos) and _numero(n_neg)
            and n_pos >= MIN_CLASSE_CALIBRACAO and n_neg >= MIN_CLASSE_CALIBRACAO)


def _check_limiares(root: Path, nome, relatorio, problemas: list[str], avisos: list[str]) -> None:
    caminho = root / "config" / "thresholds.json"
    if not caminho.is_file():
        avisos.append("sem limiar definido (config/thresholds.json)")
        return
    limiares = _le_json(caminho, root, problemas)
    if limiares is None:
        return
    if not isinstance(limiares, dict):
        problemas.append("config/thresholds.json: deve ser um objeto indexado por critério")
        return
    if nome is None or relatorio is None:
        return
    juiz = relatorio.get("judge")
    if not isinstance(juiz, dict):
        juiz = {}
    for crit, minimos in sorted(limiares.items()):
        if not isinstance(minimos, dict):
            problemas.append(f"config/thresholds.json: {crit} deve ser um objeto com tpr e/ou tnr")
            continue
        dados = juiz.get(crit)
        if not isinstance(dados, dict) or not _calibrado(dados):
            continue
        for metrica, minimo in sorted(minimos.items()):
            valor = dados.get(metrica)
            if not (_numero(valor) and _numero(minimo)):
                continue
            if valor < minimo:
                problemas.append(f"{nome}: juiz {crit}: {metrica} {valor:.3f} "
                                 f"abaixo do limiar {minimo}")


# 8. run.json: antes e depois


def _check_run(root: Path, nome, relatorio, problemas: list[str], avisos: list[str]) -> None:
    caminho = root / "config" / "run.json"
    if not caminho.is_file():
        avisos.append("config/run.json ausente: antes/depois não é verificado")
        return
    run = _le_json(caminho, root, problemas)
    if run is None:
        return
    if not isinstance(run, dict):
        problemas.append("config/run.json: deve ser um objeto JSON")
        return
    vazios = [c for c in CAMPOS_RUN if _vazio(run.get(c))]
    if vazios:
        avisos.append(f"config/run.json incompleto: {', '.join(vazios)}")
    if nome is None:
        avisos.append("sem relatório ainda (config/run.json existe, mas reports/ não tem relatório)")
        return
    if relatorio is None:
        return
    cabecalho = relatorio.get("header")
    if not isinstance(cabecalho, dict):
        cabecalho = {}
    juiz = cabecalho.get("judge")
    if not isinstance(juiz, dict):
        juiz = {}
    do_relatorio = {
        "p2_tag": cabecalho.get("p2_tag"),
        "models": _ordenada(cabecalho.get("models")),
        "judge_model": juiz.get("model"),
        "judge_prompts_sha256": cabecalho.get("judge_prompts_sha256"),
    }
    do_run = {
        "p2_tag": run.get("p2_tag"),
        "models": _ordenada(run.get("models")),
        "judge_model": run.get("judge_model"),
        "judge_prompts_sha256": run.get("judge_prompts_sha256"),
    }
    diferem = [c for c in CAMPOS_RUN if not _vazio(run.get(c)) and do_run[c] != do_relatorio[c]]
    if diferem:
        problemas.append(
            "config/run.json: mudou prompt, modelo ou tag do P2: falta um relatório novo "
            f"(diferem: {', '.join(diferem)})")


# Entrada principal


def check_repo(root: Path) -> RepoCheck:
    root = Path(root)
    resultado = RepoCheck(problems=scan_privacy(root))
    problemas, avisos = resultado.problems, resultado.warnings
    casos = _check_cases(root, problemas)
    historicos = _historicos(root, problemas)
    _check_anotacoes(casos, historicos, problemas)
    juizos = _check_juizos(root, problemas)
    amostras = _amostras(root, problemas)
    nome, relatorio = _relatorio_recente(root, problemas)
    _check_recontagem(root, nome, relatorio, juizos, historicos, amostras, problemas)
    _check_rascunhos(root, amostras, historicos, problemas)
    _check_limiares(root, nome, relatorio, problemas, avisos)
    _check_run(root, nome, relatorio, problemas, avisos)
    return resultado


def hash_prompts(prompts_dir: Path) -> str | None:
    """sha256 dos *.md da pasta, em ordem de nome (nome + quebra de linha + conteudo). None se nao houver."""
    if not prompts_dir.is_dir():
        return None
    arquivos = sorted((p for p in prompts_dir.glob("*.md") if p.is_file()), key=lambda p: p.name)
    if not arquivos:
        return None
    h = hashlib.sha256()
    for p in arquivos:
        h.update(p.name.encode("utf-8"))
        h.update(b"\n")
        h.update(p.read_bytes())
    return h.hexdigest()
