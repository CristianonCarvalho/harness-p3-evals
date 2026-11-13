"""Relatorio de avaliacao: veredito por criterio, taxas com intervalo, juiz e comparacao.

Regra central: o codigo decide quando pode; o juiz so decide o que o codigo deixou
como needs_judge; sem nenhum dos dois, o veredito e "n/a" (pendente), nunca inventado.
"""
from __future__ import annotations

import json
from pathlib import Path

from evals.checks import CheckResult
from evals.stats import intervals_overlap, wilson_interval

MIN_CLASSE_CALIBRACAO = 10  # minimo de positivos e de negativos para o juiz ser "calibrado"


def resolve_verdict(code: CheckResult | None, judge: str | None) -> tuple[str, str]:
    """Devolve (veredito, quem_decidiu). O codigo tem precedencia sobre o juiz."""
    if code is not None and code.verdict in ("pass", "fail"):
        return code.verdict, "code"
    if judge in ("pass", "fail"):
        return judge, "judge"
    return "n/a", "pendente"


def _stats(vereditos: list[tuple[str, str]]) -> dict:
    """Taxas de um criterio. So pass/fail entram em n; n/a conta em excluded."""
    passes = 0
    n = 0
    decidido = {"code": 0, "judge": 0}
    excluded = 0
    for veredito, quem in vereditos:
        if veredito not in ("pass", "fail"):
            excluded += 1
            continue
        n += 1
        if veredito == "pass":
            passes += 1
        if quem in decidido:
            decidido[quem] += 1
    ci = wilson_interval(passes, n)
    return {
        "n": n,
        "pass": passes,
        "rate": passes / n if n else None,
        "ci": list(ci) if ci is not None else None,
        "decided_by": decidido,
        "excluded": excluded,
    }


def _agrupa(rows: list[dict], split: str) -> dict:
    """{condicao: {criterio: stats}} usando so as linhas do split pedido."""
    por_cond: dict[str, dict[str, list[tuple[str, str]]]] = {}
    for r in rows:
        if r.get("split") != split:
            continue
        criterios = por_cond.setdefault(r["condition"], {})
        for criterio, veredito in r["verdicts"].items():
            criterios.setdefault(criterio, []).append((veredito[0], veredito[1]))
    return {
        cond: {crit: _stats(vs) for crit, vs in sorted(crits.items())}
        for cond, crits in sorted(por_cond.items())
    }


def _juiz(judge_metrics: dict) -> dict:
    saida = {}
    for criterio, m in sorted(judge_metrics.items()):
        tpr, tnr = m.get("tpr"), m.get("tnr")
        n_pos, n_neg = m.get("n_pos", 0), m.get("n_neg", 0)
        saida[criterio] = {
            "tpr": tpr,
            "tnr": tnr,
            "n_pos": n_pos,
            "n_neg": n_neg,
            "calibrated": (
                n_pos >= MIN_CLASSE_CALIBRACAO
                and n_neg >= MIN_CLASSE_CALIBRACAO
                and tpr is not None
                and tnr is not None
            ),
        }
    return saida


def build_report(header: dict, rows: list[dict], judge_metrics: dict,
                 usage: dict | None = None) -> dict:
    return {
        "header": header,
        "rates": _agrupa(rows, "teste"),
        "dev_diagnostic": _agrupa(rows, "desenvolvimento"),
        "judge": _juiz(judge_metrics),
        "usage": usage or {},
    }


def compare(base: dict, new: dict) -> list[dict]:
    """Compara dois relatorios. So entram condicoes e criterios presentes nos dois lados."""
    saida = []
    for cond in sorted(set(base["rates"]) & set(new["rates"])):
        b_crits, n_crits = base["rates"][cond], new["rates"][cond]
        for crit in sorted(set(b_crits) & set(n_crits)):
            b, n = b_crits[crit], n_crits[crit]
            base_rate, new_rate = b["rate"], n["rate"]
            delta = None if base_rate is None or new_rate is None else new_rate - base_rate
            if b["ci"] is None or n["ci"] is None:
                label = "sem dados"
            elif intervals_overlap(tuple(b["ci"]), tuple(n["ci"])):
                label = "dentro do ruído"
            else:
                label = "diferença real"
            saida.append({
                "condition": cond,
                "criterion": crit,
                "base_rate": base_rate,
                "new_rate": new_rate,
                "delta": delta,
                "label": label,
            })
    return saida


def _pct(x: float | None) -> str:
    return "indefinido" if x is None else f"{x * 100:.1f}%"


def _ci(ci: list | None) -> str:
    return "—" if ci is None else f"[{ci[0] * 100:.1f}%, {ci[1] * 100:.1f}%]"


def _tabela_taxas(rates: dict) -> list[str]:
    linhas = []
    if not rates:
        return ["_Sem linhas neste split._", ""]
    for cond, crits in rates.items():
        linhas += [f"### {cond}", "",
                   "| critério | n | aprovação | intervalo 95% | decidido por (código/juiz) | excluídos |",
                   "|---|---|---|---|---|---|"]
        for crit, s in crits.items():
            d = s["decided_by"]
            linhas.append(
                f"| {crit} | {s['n']} | {_pct(s['rate'])} | {_ci(s['ci'])} "
                f"| {d['code']}/{d['judge']} | {s['excluded']} |"
            )
        linhas.append("")
    return linhas


def render_markdown(report: dict) -> str:
    h = report["header"]
    juiz_h = h.get("judge", {})
    linhas = [
        "# Relatório de avaliação",
        "",
        "## Reprodução",
        "",
        f"- modelos: {', '.join(h.get('models', []))}",
        f"- juiz: {juiz_h.get('model', '?')} (versão {juiz_h.get('version', '?')})",
        f"- p2_tag: {h.get('p2_tag', '?')}",
        f"- corpus_version: {h.get('corpus_version', '?')}",
        f"- seed: {h.get('seed', '?')}",
        f"- data: {h.get('date', '?')}",
        "",
        "## Teste",
        "",
    ]
    linhas += _tabela_taxas(report["rates"])

    linhas += ["## Juiz", ""]
    if not report["judge"]:
        linhas += ["_Sem métricas do juiz._", ""]
    for crit, j in report["judge"].items():
        linha = (f"- {crit}: TPR {_pct(j['tpr'])}, TNR {_pct(j['tnr'])}, "
                 f"n_pos {j['n_pos']}, n_neg {j['n_neg']}")
        if not j["calibrated"]:
            linha += " — não calibrado"
        linhas.append(linha)
    if report["judge"]:
        linhas.append("")

    usage = report.get("usage") or {}
    if usage:
        linhas += ["## Custo e tokens", ""]
        if "cost_usd" in usage:
            linhas.append(f"- custo: US$ {usage['cost_usd']:.4f}")
        if "input_tokens" in usage:
            linhas.append(f"- tokens de entrada: {usage['input_tokens']}")
        if "output_tokens" in usage:
            linhas.append(f"- tokens de saída: {usage['output_tokens']}")
        linhas.append("")

    linhas += ["## Desenvolvimento (diagnóstico)", "",
               "Não entra nas taxas principais; serve só para diagnóstico.", ""]
    linhas += _tabela_taxas(report["dev_diagnostic"])
    if report.get("review"):
        from evals.review_report import render_review_markdown  # import tardio: evita ciclo
        linhas += [""] + render_review_markdown(report["review"])
    return "\n".join(linhas)


def write_report(report: dict, path: Path) -> None:
    path.write_text(
        json.dumps(report, sort_keys=True, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def load_report(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))
