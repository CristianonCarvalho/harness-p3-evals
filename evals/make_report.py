"""Relatorio de uma rodada: junta traces, gabaritos e julgamentos do juiz (report.py).

Regras:
- o codigo decide quando pode (checks.py); o juiz so decide o que o codigo deixou como
  needs_judge, e C3 e sempre do juiz; sem nenhum dos dois, o veredito e pendente;
- julgamento feito com outro modelo ou outro prompt nao entra (obsoleto) e e contado no cabecalho;
- so traces com status "ok" entram; os demais sao contados por status;
- as metricas do juiz usam o mesmo calculo da recontagem do check-repo (review_report).
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from evals.annotation import load_history
from evals.annotation_drafter import blind_ids
from evals.cases import load_cases
from evals.checks import check_c1, check_c2, check_c4
from evals.report import build_report, render_markdown, resolve_verdict, write_report
from evals.review_report import _metricas_juiz, build_review, collect_review_inputs
from evals.sampling import load_samples, load_traces


def condicao(trace: dict) -> str:
    conds = trace.get("conditions", {})
    if conds.get("server") == "remoto":
        return "remoto"
    return "com_skill" if conds.get("skill") else "sem_skill"


def usable_judgments(judgments: dict[str, dict], run_config: dict) -> tuple[dict[str, dict], int]:
    """{trace_id: verdicts} dos julgamentos do modelo e prompt congelados; e quantos sao obsoletos."""
    usable: dict[str, dict] = {}
    stale = 0
    for tid, record in sorted(judgments.items()):
        juiz = record.get("judge") or {}
        if (juiz.get("model") != run_config["judge_model"]
                or juiz.get("prompts_sha256") != run_config["judge_prompts_sha256"]):
            stale += 1
            continue
        usable[tid] = record["verdicts"]
    return usable, stale


def _verdicts(trace: dict, case: dict, juizo: dict) -> dict[str, tuple[str, str]]:
    gabarito = case["gabarito"]
    final = trace.get("final_answer", "")
    events = trace.get("events", [])
    hipoteses = case.get("hypothesis", [])
    saida = {}
    saida["C1"] = resolve_verdict(
        check_c1(final, events, gabarito.get("expected_provisions", [])), juizo.get("C1"))
    saida["C2"] = resolve_verdict(
        check_c2(final, events, gabarito["reference_date"],
                 answer_exists=gabarito["answer_exists"]), juizo.get("C2"))
    saida["C3"] = resolve_verdict(None, juizo.get("C3"))
    if "H12" in hipoteses or "H13" in hipoteses:
        saida["C4"] = resolve_verdict(
            check_c4(final, trace.get("synthetic_ids", []), check_instruction="H13" in hipoteses),
            juizo.get("C4"))
    return saida


def build_rows(traces: list[dict], cases: dict[str, dict],
               usable: dict[str, dict]) -> tuple[list[dict], dict[str, int]]:
    """Uma linha por trace ok, e a contagem dos que nao sao ok, por status."""
    rows: list[dict] = []
    skipped: dict[str, int] = {}
    for trace in traces:
        status = trace.get("status")
        if status != "ok":
            chave = str(status)
            skipped[chave] = skipped.get(chave, 0) + 1
            continue
        tid, cid = trace["trace_id"], trace["case_id"]
        case = cases.get(cid)
        if case is None:
            raise ValueError(f"caso {cid!r} do trace {tid} não está em cases/")
        rows.append({
            "trace_id": tid,
            "case_id": cid,
            "split": case.get("split"),
            "condition": condicao(trace),
            "verdicts": _verdicts(trace, case, usable.get(tid, {})),
        })
    return rows, dict(sorted(skipped.items()))


def _pendentes(rows: list[dict]) -> dict[str, int]:
    pendentes: dict[str, int] = {}
    for row in rows:
        for crit, (_, quem) in row["verdicts"].items():
            pendentes.setdefault(crit, 0)
            if quem == "pendente":
                pendentes[crit] += 1
    return dict(sorted(pendentes.items()))


def _uso(traces_ok: list[dict]) -> dict:
    return {
        "cost_usd": round(sum(t["usage"]["cost_usd"] for t in traces_ok), 6),
        "input_tokens": sum(t["usage"]["input_tokens"] for t in traces_ok),
        "output_tokens": sum(t["usage"]["output_tokens"] for t in traces_ok),
    }


def _versoes_do_corpus(traces: list[dict]):
    versoes = sorted({t["conditions"]["corpus_version"] for t in traces
                      if "corpus_version" in t.get("conditions", {})})
    if not versoes:
        return None
    return versoes[0] if len(versoes) == 1 else versoes


def _metricas_do_juiz(annotations_dir: Path, samples_path: Path, usable: dict[str, dict]) -> dict:
    """Mesma conta da recontagem do check-repo: amostra cega, ultima versao cega, contra o juiz."""
    humanas = []
    for tid in sorted(blind_ids(load_samples(samples_path))):
        historico = load_history(annotations_dir, tid)
        if historico and historico[-1].get("kind") == "blind":
            humanas.append(historico[-1])
    return _metricas_juiz(humanas, usable, set())


def assemble_report(*, traces: list[dict], cases: dict[str, dict], judgments: dict[str, dict],
                    run_config: dict, round_summary: dict | None, date: str, root: Path,
                    annotations_dir: Path | None = None, drafts_dir: Path | None = None,
                    samples_path: Path | None = None) -> dict:
    """Monta o relatorio de uma rodada. Puro em relacao aos argumentos; le do disco so a revisao.

    Os caminhos de anotacao e rascunho saem de `root` quando nao forem dados.
    """
    root = Path(root)
    annotations_dir = annotations_dir or root / "annotations"
    drafts_dir = drafts_dir or root / "drafts"
    samples_path = samples_path or annotations_dir / "_samples.json"

    usable, stale = usable_judgments(judgments, run_config)
    rows, skipped = build_rows(traces, cases, usable)
    traces_ok = [t for t in traces if t.get("status") == "ok"]
    header = {
        "models": run_config["models"],
        "p2_tag": run_config["p2_tag"],
        "judge": {"model": run_config["judge_model"], "version": run_config["judge_model"]},
        "judge_prompts_sha256": run_config["judge_prompts_sha256"],
        "seed": run_config["split_seed"],
        "corpus_version": _versoes_do_corpus(traces),
        "date": date,
        "round_id": round_summary.get("round_id") if round_summary else None,
        "n_traces": len(rows),
        "skipped_traces": skipped,
        "stale_judgments": stale,
        "pending": _pendentes(rows),
    }
    relatorio = build_report(
        header, rows, _metricas_do_juiz(annotations_dir, samples_path, usable), _uso(traces_ok))

    if annotations_dir.is_dir():
        disputados = {t["trace_id"] for t in traces
                      if cases.get(t["case_id"], {}).get("gabarito", {}).get("disputed") is True}
        entradas = collect_review_inputs(
            annotations_dir=annotations_dir, drafts_dir=drafts_dir, samples_path=samples_path,
            cases_dir=root / "cases", traces_dir=root / "traces", judgments_dir=None)
        # O juiz e os traces disputados vem da rodada e dos julgamentos validos, nao do disco.
        entradas.update(judge=usable, disputed_traces=disputados, cases=cases)
        relatorio["review"] = build_review(**entradas)
    return relatorio


# Linha de comando

def _montar_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="python -m evals.cli make-report",
                                description="Monta o relatório de uma rodada (JSON e Markdown).")
    p.add_argument("--round-dir", type=Path, required=True)
    p.add_argument("--cases-dir", type=Path, default=Path("cases"))
    p.add_argument("--judgments-dir", type=Path, default=Path("judgments"))
    p.add_argument("--annotations-dir", type=Path, default=Path("annotations"))
    p.add_argument("--run-config", type=Path, default=Path("config/run.json"))
    p.add_argument("--out-dir", type=Path, default=Path("reports"))
    p.add_argument("--date", required=True, help="AAAA-MM-DD")
    return p


def _carrega_julgamentos(pasta: Path) -> dict[str, dict]:
    if not pasta.is_dir():
        return {}
    return {p.stem: json.loads(p.read_text(encoding="utf-8"))
            for p in sorted(pasta.glob("*.json"))}


def main(argv: list[str] | None = None) -> int:
    args = _montar_parser().parse_args(argv)
    if not args.round_dir.is_dir():
        print(f"erro: pasta da rodada não encontrada: {args.round_dir}", file=sys.stderr)
        return 1

    resumo_path = args.round_dir / "_round.json"
    try:
        resumo = (json.loads(resumo_path.read_text(encoding="utf-8"))
                  if resumo_path.is_file() else None)
        round_id = resumo.get("round_id") if resumo else args.round_dir.name
        base = args.out_dir / f"{args.date}-{round_id}"
        json_path, md_path = base.with_suffix(".json"), base.with_suffix(".md")
        existentes = [str(p) for p in (json_path, md_path) if p.exists()]
        if existentes:
            print(f"erro: já existe {', '.join(existentes)}; relatório não se sobrescreve",
                  file=sys.stderr)
            return 1

        relatorio = make_report_from_args(args, resumo)
    except (OSError, ValueError, KeyError) as exc:
        print(f"erro: {exc}", file=sys.stderr)
        return 1

    args.out_dir.mkdir(parents=True, exist_ok=True)
    write_report(relatorio, json_path)
    md_path.write_text(render_markdown(relatorio) + "\n", encoding="utf-8")
    print(json_path)
    print(md_path)
    for cond, crits in relatorio["rates"].items():
        partes = [f"{crit} {s['pass']}/{s['n']}" for crit, s in crits.items()]
        print(f"{cond}: " + ", ".join(partes) + " (teste; aprovados/n)")
    pendentes = {c: n for c, n in relatorio["header"]["pending"].items() if n}
    print("pendentes: " + (", ".join(f"{c} {n}" for c, n in pendentes.items())
                           if pendentes else "nenhum"))
    return 0


def make_report_from_args(args, resumo: dict | None) -> dict:
    traces = load_traces(args.round_dir)
    cases = {c["case_id"]: c for c in load_cases(args.cases_dir)} if args.cases_dir.is_dir() else {}
    run_config = json.loads(args.run_config.read_text(encoding="utf-8"))
    return assemble_report(
        traces=traces, cases=cases, judgments=_carrega_julgamentos(args.judgments_dir),
        run_config=run_config, round_summary=resumo, date=args.date, root=Path("."),
        annotations_dir=args.annotations_dir)


if __name__ == "__main__":
    raise SystemExit(main())
