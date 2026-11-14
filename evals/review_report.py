"""Revisão da anotação: o que o próprio processo de anotação mostra no relatório.

Armazenamento (decisão deste módulo):
- a anotação cega e as correções ficam em `annotations/<trace_id>.v<N>.json`;
  a primeira versão de um trace da amostra cega é a anotação cega original,
  e as versões seguintes são correções;
- a reanotação de consistência usa o MESMO gravador, mas em outra pasta,
  `annotations/consistency/`, para não ser confundida com correção.

Regras de medição:
- juiz (TPR/TNR) só usa anotações cegas da amostra, na última versão;
- o acordo do redator compara o rascunho com a PRIMEIRA versão cega (antes de qualquer correção);
- ancoragem: a pessoa mudou o rascunho em traces revisados, comparado com a taxa de erro do redator;
- sem juiz, as partes que dependem dele ficam None e o motivo vai em `motivos`.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

from evals.annotation import load_annotation, load_history
from evals.annotation_drafter import blind_ids
from evals.cases import load_cases
from evals.metrics import confusion, self_agreement
from evals.report import MIN_CLASSE_CALIBRACAO, _pct
from evals.sampling import load_samples, load_traces

ANCHORING_FACTOR = 0.5
JUDGE_CRITERIA = ("C1", "C2", "C3", "C4")
CRITERIA = ("C1", "C2", "C3", "C4")
MIN_ANOTADAS = 100

_VERSIONADO = re.compile(r"(.+)\.v(\d+)\.json")
_SEM_JUIZ = "Sem juiz ainda."


def _metricas_juiz(humanas: list[dict], judge: dict, disputed_traces: set[str]) -> dict:
    saida = {}
    for crit in JUDGE_CRITERIA:
        # O juiz so decide o que o codigo deixou para ele (D3): trace sem veredito do juiz
        # neste criterio fica fora da conta e e contado a parte, em vez de quebrar o relatorio.
        julgadas = [h for h in humanas
                    if isinstance(judge.get(h["trace_id"]), dict) and crit in judge[h["trace_id"]]]
        m = confusion(julgadas, judge, crit, disputed=frozenset(disputed_traces))
        saida[crit] = {"tpr": m.tpr, "tnr": m.tnr, "n_pos": m.n_pos, "n_neg": m.n_neg,
                       "n_sem_juiz": len(humanas) - len(julgadas)}
    return saida


def build_review(
    *,
    histories: dict[str, list[dict]],
    consistency: dict[str, dict],
    blind: set[str],
    consistency_ids: set[str],
    annotation_drafts: dict[str, dict],
    judge: dict[str, dict] | None,
    disputed_traces: set[str],
    gabarito_drafts: dict[str, dict],
    cases: dict[str, dict],
) -> dict:
    motivos: dict[str, str] = {}
    latest = {tid: h[-1] for tid, h in sorted(histories.items()) if h}

    # 1. Contagem pela última versão
    kinds = [a.get("kind") for a in latest.values()]
    total = len(latest)
    counts = {
        "blind": kinds.count("blind"),
        "revised": kinds.count("revised"),
        "total": total,
        "criterion_2_met": total >= MIN_ANOTADAS
        and all(k in ("blind", "revised") for k in kinds),
    }

    # 2. Acordo do redator: rascunho contra a primeira versão cega
    acordo = {c: {"agree": 0, "total": 0} for c in CRITERIA}
    for tid in sorted(blind):
        hist = histories.get(tid)
        rascunho = annotation_drafts.get(tid)
        if not hist or rascunho is None or hist[0].get("kind") != "blind":
            continue
        for c in CRITERIA:
            redator = rascunho.get("verdicts", {}).get(c)
            humano = hist[0].get("verdicts", {}).get(c)
            if redator == "n/a" and humano == "n/a":
                continue
            acordo[c]["total"] += 1
            if redator == humano:
                acordo[c]["agree"] += 1
    drafter_accuracy = {
        c: {
            "agree": a["agree"],
            "total": a["total"],
            "error_rate": (1 - a["agree"] / a["total"]) if a["total"] else None,
        }
        for c, a in acordo.items()
    }

    # 3. Juiz nas cegas (última versão, só amostra cega com kind blind)
    cegas_latest = [a for tid, a in latest.items()
                    if tid in blind and a.get("kind") == "blind"]
    if judge:
        judge_blind = _metricas_juiz(cegas_latest, judge, disputed_traces)
    else:
        judge_blind = None
        motivos["judge_blind"] = _SEM_JUIZ

    # 4. Ancoragem: traces revisados com rascunho
    revisadas = [(tid, a) for tid, a in latest.items()
                 if a.get("kind") == "revised" and tid in annotation_drafts]
    anchoring = {}
    for c in CRITERIA:
        mudou = total_c = 0
        for tid, a in revisadas:
            humano = a.get("verdicts", {}).get(c)
            redator = annotation_drafts[tid].get("verdicts", {}).get(c)
            if humano == "n/a" and redator == "n/a":
                continue
            total_c += 1
            if humano != redator:
                mudou += 1
        change_rate = mudou / total_c if total_c else None
        err = drafter_accuracy[c]["error_rate"]
        anchoring[c] = {
            "changed": mudou,
            "total": total_c,
            "change_rate": change_rate,
            "drafter_error_rate": err,
            "flag": change_rate is not None and err is not None and err > 0
            and change_rate < ANCHORING_FACTOR * err,
        }

    # 5. Autoconsistência: primeira versão contra a reanotação
    ids = sorted(t for t in consistency_ids if t in consistency and histories.get(t))
    if ids:
        ag = self_agreement([histories[t][0] for t in ids], [consistency[t] for t in ids])
        autoconsistencia = {
            c: {"agree": a.agree, "total": a.total, "n_na": a.n_na, "rate": a.rate}
            for c, a in ag.items()
        }
    else:
        autoconsistencia = None
        motivos["self_agreement"] = "Sem traces com as duas rodadas de anotação cega."

    # 6. Correções: traces cegos com mais de uma versão
    multi = sorted(t for t in blind if histories.get(t) and len(histories[t]) > 1)
    cegas_hist = [histories[t] for t in sorted(blind) if histories.get(t)]
    primeiras_cegas = [h[0] for h in cegas_hist if h[0].get("kind") == "blind"]
    if judge:
        judge_first = _metricas_juiz(primeiras_cegas, judge, disputed_traces)
        judge_latest = _metricas_juiz(cegas_latest, judge, disputed_traces)
    else:
        judge_first = judge_latest = None
        motivos["corrections"] = _SEM_JUIZ
    corrections = {
        "n_corrected": len(multi),
        "traces": multi,
        "judge_first": judge_first,
        "judge_latest": judge_latest,
    }

    # 7. Gabaritos: rascunho mais recente contra o gabarito do caso
    alterados = 0
    for cid, rascunho in gabarito_drafts.items():
        caso = cases.get(cid)
        if caso is None:
            continue
        g = caso.get("gabarito", {})
        antes = (g.get("answer_exists"), set(g.get("expected_provisions", [])),
                 g.get("reference_date"))
        depois = (rascunho.get("answer_exists"), set(rascunho.get("expected_provisions", [])),
                  rascunho.get("reference_date"))
        if antes != depois:
            alterados += 1
    gabaritos = {
        "drafted": len(gabarito_drafts),
        "changed": alterados,
        "disputed": sum(1 for c in cases.values()
                        if c.get("gabarito", {}).get("disputed") is True),
    }

    return {
        "counts": counts,
        "judge_blind": judge_blind,
        "drafter_accuracy": drafter_accuracy,
        "anchoring": anchoring,
        "self_agreement": autoconsistencia,
        "corrections": corrections,
        "gabaritos": gabaritos,
        "motivos": motivos,
    }


def _tabela(cabecalho: list[str], linhas_dados: list[list[str]]) -> list[str]:
    linhas = ["| " + " | ".join(cabecalho) + " |",
              "|" + "---|" * len(cabecalho)]
    linhas += ["| " + " | ".join(d) + " |" for d in linhas_dados]
    return linhas


def render_review_markdown(review: dict) -> list[str]:
    motivos = review.get("motivos", {})
    c = review["counts"]
    situacao = "atendido" if c["criterion_2_met"] else "não atendido"
    linhas = ["## Revisão da anotação", "",
              "### Contagem", "",
              f"- anotações cegas: {c['blind']}",
              f"- anotações revisadas: {c['revised']}",
              f"- total (última versão): {c['total']}",
              f"- critério de conclusão 2 (100 traces anotados com o tipo declarado): {situacao}",
              ""]

    linhas += ["### Juiz nas anotações cegas", ""]
    jb = review["judge_blind"]
    if jb is None:
        linhas += ["_Sem juiz ainda._", ""]
    else:
        dados = []
        for crit, j in jb.items():
            calibrado = (j["n_pos"] >= MIN_CLASSE_CALIBRACAO
                         and j["n_neg"] >= MIN_CLASSE_CALIBRACAO)
            dados.append([crit, _pct(j["tpr"]), _pct(j["tnr"]), str(j["n_pos"]),
                          str(j["n_neg"]), str(j.get("n_sem_juiz", 0)),
                          "calibrado" if calibrado else "não calibrado"])
        linhas += _tabela(["critério", "TPR", "TNR", "n_pos", "n_neg",
                           "sem veredito do juiz", "situação"], dados)
        linhas.append("")

    linhas += ["### Acordo do redator com as anotações cegas", ""]
    dados = [[crit, str(a["agree"]), str(a["total"]), _pct(a["error_rate"])]
             for crit, a in review["drafter_accuracy"].items()]
    linhas += _tabela(["critério", "concordância", "total", "taxa de erro"], dados)
    linhas.append("")

    linhas += ["### Ancoragem (traces revisados com rascunho)", ""]
    dados = []
    for crit, a in review["anchoring"].items():
        alerta = "possível ancoragem" if a["flag"] else "—"
        dados.append([crit, str(a["changed"]), str(a["total"]), _pct(a["change_rate"]),
                      _pct(a["drafter_error_rate"]), alerta])
    linhas += _tabela(["critério", "mudanças", "total", "taxa de mudança",
                       "taxa de erro do redator", "alerta"], dados)
    linhas.append("")

    linhas += ["### Autoconsistência (reanotação de traces cegos)", ""]
    sa = review["self_agreement"]
    if sa is None:
        linhas += [motivos.get("self_agreement", "Sem dados."), ""]
    else:
        dados = [[crit, str(a["agree"]), str(a["total"]), str(a["n_na"]), _pct(a["rate"])]
                 for crit, a in sa.items()]
        linhas += _tabela(["critério", "concordância", "total", "n/a dos dois lados",
                           "taxa"], dados)
        linhas.append("")

    co = review["corrections"]
    linhas += ["### Correções nas anotações cegas", "",
               f"- traces com mais de uma versão: {co['n_corrected']}"]
    if co["traces"]:
        linhas.append(f"- traces: {', '.join(co['traces'])}")
    linhas.append("")
    if co["judge_first"] is None:
        linhas += ["_Sem juiz ainda._", ""]
    else:
        dados = []
        for crit in JUDGE_CRITERIA:
            p, u = co["judge_first"][crit], co["judge_latest"][crit]
            dados.append([crit, _pct(p["tpr"]), _pct(p["tnr"]),
                          _pct(u["tpr"]), _pct(u["tnr"])])
        linhas += _tabela(["critério", "TPR primeira", "TNR primeira",
                           "TPR última", "TNR última"], dados)
        linhas.append("")

    g = review["gabaritos"]
    linhas += ["### Gabaritos", "",
               f"- rascunhados: {g['drafted']}",
               f"- alterados pela pessoa: {g['changed']}",
               f"- marcados como disputados: {g['disputed']}",
               ""]
    return linhas


def _ids_em(pasta: Path) -> set[str]:
    if not pasta.exists():
        return set()
    ids = set()
    for p in pasta.iterdir():
        if p.is_file():
            m = _VERSIONADO.fullmatch(p.name)
            if m:
                ids.add(m.group(1))
    return ids


def collect_review_inputs(
    *,
    annotations_dir: Path,
    drafts_dir: Path,
    samples_path: Path,
    cases_dir: Path,
    traces_dir: Path,
    judgments_dir: Path | None,
) -> dict:
    histories = {tid: load_history(annotations_dir, tid)
                 for tid in sorted(_ids_em(annotations_dir))}

    pasta_cons = annotations_dir / "consistency"
    consistency = {tid: load_annotation(pasta_cons, tid)
                   for tid in sorted(_ids_em(pasta_cons))}

    samples = load_samples(samples_path)
    blind = blind_ids(samples)
    consistency_ids = set(samples.get("consistency", {}).get("trace_ids", []))

    annotation_drafts: dict[str, dict] = {}
    pasta_draft = drafts_dir / "annotations"
    if pasta_draft.exists():
        for p in sorted(pasta_draft.glob("*.json")):
            annotation_drafts[p.stem] = json.loads(p.read_text(encoding="utf-8"))

    ultimo: dict[str, tuple[int, Path]] = {}
    pasta_case = drafts_dir / "cases"
    if pasta_case.exists():
        for p in pasta_case.iterdir():
            m = _VERSIONADO.fullmatch(p.name)
            if m and p.is_file():
                cid, v = m.group(1), int(m.group(2))
                if cid not in ultimo or v > ultimo[cid][0]:
                    ultimo[cid] = (v, p)
    gabarito_drafts = {cid: json.loads(p.read_text(encoding="utf-8"))
                       for cid, (_, p) in ultimo.items()}

    cases = {c["case_id"]: c for c in load_cases(cases_dir)}
    traces = load_traces(traces_dir) if traces_dir.exists() else []
    disputed_traces = {
        t["trace_id"] for t in traces
        if cases.get(t["case_id"], {}).get("gabarito", {}).get("disputed") is True
    }

    judge: dict[str, dict] | None = None
    if judgments_dir is not None and judgments_dir.exists():
        judge = {}
        for p in sorted(judgments_dir.glob("*.json")):
            judge[p.stem] = json.loads(p.read_text(encoding="utf-8"))["verdicts"]

    return {
        "histories": histories,
        "consistency": consistency,
        "blind": blind,
        "consistency_ids": consistency_ids,
        "annotation_drafts": annotation_drafts,
        "judge": judge,
        "disputed_traces": disputed_traces,
        "gabarito_drafts": gabarito_drafts,
        "cases": cases,
    }
