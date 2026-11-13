import json
from pathlib import Path

import pytest

from evals.report import build_report, render_markdown
from evals.review_report import (
    CRITERIA,
    build_review,
    collect_review_inputs,
    render_review_markdown,
)

HEADER = {
    "models": ["modelo-a"],
    "judge": {"model": "juiz-x", "version": "2026-01"},
    "p2_tag": "step-16", "corpus_version": "abc", "seed": 7,
    "prices": {"modelo-a": [1.0, 2.0]}, "date": "2026-11-10",
}


def V(c1="pass", c2="pass", c3="pass", c4="n/a"):
    return {"C1": c1, "C2": c2, "C3": c3, "C4": c4}


def J(c2="pass", c3="pass", c4="n/a"):
    return {"C2": c2, "C3": c3, "C4": c4}


def anotacao_cega(tid, verdicts, version=1):
    return {"trace_id": tid, "verdicts": verdicts, "note": "", "uncertain": [],
            "kind": "blind", "version": version, "date": "2026-11-01"}


def anotacao_revisada(tid, verdicts, version=1):
    return {"trace_id": tid, "verdicts": verdicts, "note": "", "uncertain": [],
            "kind": "revised", "draft": f"drafts/annotations/{tid}.json",
            "version": version, "date": "2026-11-02"}


def rascunho(tid, verdicts):
    return {"trace_id": tid, "model": "modelo-a", "verdicts": verdicts,
            "uncertain": [], "note": "", "prompt_sha": "abc123", "blind": True}


def review(**kw):
    args = dict(histories={}, consistency={}, blind=set(), consistency_ids=set(),
                annotation_drafts={}, judge=None, disputed_traces=set(),
                gabarito_drafts={}, cases={})
    args.update(kw)
    return build_review(**args)


# ---- 1. contagem e criterio 2
def _hist(n_blind, n_revised):
    hist = {}
    for i in range(n_blind):
        hist[f"b{i}"] = [anotacao_cega(f"b{i}", V())]
    for i in range(n_revised):
        hist[f"r{i}"] = [anotacao_revisada(f"r{i}", V())]
    return hist


def test_contagem_usa_a_ultima_versao_e_separa_os_tipos():
    hist = _hist(2, 3)
    hist["b0"].append(anotacao_cega("b0", V(c1="fail"), version=2))
    c = review(histories=hist)["counts"]
    assert (c["blind"], c["revised"], c["total"]) == (2, 3, 5)
    assert c["criterion_2_met"] is False


def test_criterio_2_exige_cem_traces_com_tipo_declarado():
    assert review(histories=_hist(99, 0))["counts"]["criterion_2_met"] is False
    assert review(histories=_hist(60, 40))["counts"]["criterion_2_met"] is True
    assert review()["counts"]["criterion_2_met"] is False


# ---- 2. juiz so nas cegas, ultima versao
def test_juiz_usa_so_cegas_na_ultima_versao_sem_excecao():
    hist = {
        "b1": [anotacao_cega("b1", V(c3="pass"))],
        "b2": [anotacao_cega("b2", V(c3="fail"))],
        "b3": [anotacao_cega("b3", V(c3="pass")),
               anotacao_revisada("b3", V(c3="fail"), version=2)],
        "r1": [anotacao_revisada("r1", V(c3="fail"))],
    }
    judge = {t: J() for t in ("b1", "b2", "b3", "r1")}
    judge["b1"] = J(c3="pass")
    judge["b2"] = J(c3="pass")
    r = review(histories=hist, blind={"b1", "b2", "b3"}, judge=judge)
    # b1: tp; b2: fp; b3 ficou revisada na ultima versao, sai da calibracao
    assert r["judge_blind"]["C3"] == {"tpr": 1.0, "tnr": 0.0, "n_pos": 1, "n_neg": 1,
                                      "n_sem_juiz": 0}
    assert set(r["judge_blind"]) == {"C2", "C3", "C4"}


def test_juiz_que_nao_julgou_um_criterio_nao_quebra_o_relatorio():
    # O juiz so decide o que o codigo deixou para ele (D3): em muitos traces nao ha C2 nem C4.
    hist = {
        "b1": [anotacao_cega("b1", V(c2="pass", c3="pass"))],
        "b2": [anotacao_cega("b2", V(c2="fail", c3="fail"))],
        "b3": [anotacao_cega("b3", V(c2="pass", c3="pass"))],
    }
    judge = {"b1": {"C3": "pass"}, "b2": {"C2": "fail", "C3": "fail"}, "b3": {"C3": "fail"}}
    r = review(histories=hist, blind={"b1", "b2", "b3"}, judge=judge)
    assert r["judge_blind"]["C2"] == {"tpr": None, "tnr": 1.0, "n_pos": 0, "n_neg": 1,
                                      "n_sem_juiz": 2}
    assert r["judge_blind"]["C3"]["n_sem_juiz"] == 0
    assert r["judge_blind"]["C4"]["n_sem_juiz"] == 3
    linhas = "\n".join(render_review_markdown(r))
    assert "sem veredito do juiz" in linhas


def test_juiz_none_deixa_as_partes_dependentes_vazias():
    r = review(histories=_hist(1, 0), blind={"b0"}, judge=None)
    assert r["judge_blind"] is None
    assert "judge_blind" in r["motivos"]


# ---- 3. acordo do redator, primeira versao
def test_acordo_do_redator_usa_a_primeira_versao_e_exclui_na_duplo():
    hist = {}
    drafts = {}
    for i in range(4):
        tid = f"b{i}"
        c1 = "pass" if i == 3 else "fail"  # b3 discorda na primeira versao
        hist[tid] = [anotacao_cega(tid, V(c1=c1))]
        drafts[tid] = rascunho(tid, V(c1="fail"))
    # b3 ganha uma correcao que concorda com o redator: a primeira deve prevalecer
    hist["b3"].append(anotacao_cega("b3", V(c1="fail"), version=2))
    r = review(histories=hist, blind=set(hist), annotation_drafts=drafts)
    c1 = r["drafter_accuracy"]["C1"]
    assert (c1["agree"], c1["total"]) == (3, 4)
    assert c1["error_rate"] == pytest.approx(0.25)
    # C4: todos n/a dos dois lados, nenhum par conta
    assert r["drafter_accuracy"]["C4"] == {"agree": 0, "total": 0, "error_rate": None}


# ---- 4. ancoragem
def _cenario_ancoragem(erros_redator, mudancas, n=10):
    hist, drafts, cegas = {}, {}, set()
    for i in range(n):
        tid = f"b{i}"
        c1 = "pass" if i < erros_redator else "fail"
        hist[tid] = [anotacao_cega(tid, V(c1=c1))]
        drafts[tid] = rascunho(tid, V(c1="fail"))
        cegas.add(tid)
    for i in range(n):
        tid = f"r{i}"
        c1 = "pass" if i < mudancas else "fail"
        hist[tid] = [anotacao_revisada(tid, V(c1=c1))]
        drafts[tid] = rascunho(tid, V(c1="fail"))
    return dict(histories=hist, blind=cegas, annotation_drafts=drafts)


def test_ancoragem_marca_quando_muda_menos_que_metade_do_erro():
    r = review(**_cenario_ancoragem(erros_redator=4, mudancas=1))
    a = r["anchoring"]["C1"]
    assert a["drafter_error_rate"] == pytest.approx(0.4)
    assert a["change_rate"] == pytest.approx(0.1)
    assert a["flag"] is True
    md = "\n".join(render_review_markdown(r))
    assert "possível ancoragem" in md


def test_ancoragem_nao_marca_quando_muda_o_suficiente():
    r = review(**_cenario_ancoragem(erros_redator=4, mudancas=3))
    assert r["anchoring"]["C1"]["change_rate"] == pytest.approx(0.3)
    assert r["anchoring"]["C1"]["flag"] is False
    assert "possível ancoragem" not in "\n".join(render_review_markdown(r))


def test_ancoragem_nao_marca_com_erro_zero_ou_sem_base():
    zero = review(**_cenario_ancoragem(erros_redator=0, mudancas=0))
    assert zero["anchoring"]["C1"]["drafter_error_rate"] == 0
    assert zero["anchoring"]["C1"]["flag"] is False
    sem_base = _cenario_ancoragem(erros_redator=4, mudancas=1)
    sem_base["blind"] = set()
    semb = review(**sem_base)
    assert semb["anchoring"]["C1"]["drafter_error_rate"] is None
    assert semb["anchoring"]["C1"]["flag"] is False


# ---- 5. autoconsistencia
def test_autoconsistencia_usa_primeira_versao_contra_reanotacao():
    hist = {
        "b1": [anotacao_cega("b1", V(c1="pass")),
               anotacao_cega("b1", V(c1="fail"), version=2)],
        "b2": [anotacao_cega("b2", V(c1="pass"))],
        "b3": [anotacao_cega("b3", V(c1="pass"))],
    }
    cons = {"b1": anotacao_cega("b1", V(c1="pass")),
            "b2": anotacao_cega("b2", V(c1="fail"))}
    r = review(histories=hist, blind={"b1", "b2", "b3"},
               consistency=cons, consistency_ids={"b1", "b2"})
    c1 = r["self_agreement"]["C1"]
    assert (c1["agree"], c1["total"], c1["rate"]) == (1, 2, 0.5)
    assert r["self_agreement"]["C4"]["n_na"] == 2
    assert r["self_agreement"]["C4"]["rate"] is None


def test_autoconsistencia_sem_reanotacao_e_none_com_motivo():
    r = review(histories=_hist(2, 0), blind={"b0", "b1"}, consistency={},
               consistency_ids=set())
    assert r["self_agreement"] is None
    assert "self_agreement" in r["motivos"]


# ---- 6. correcoes
def test_correcoes_comparam_primeira_e_ultima_versao_com_o_juiz():
    hist = {
        "b1": [anotacao_cega("b1", V(c3="pass")),
               anotacao_cega("b1", V(c3="fail"), version=2)],
        "b2": [anotacao_cega("b2", V(c3="pass"))],
        "b3": [anotacao_cega("b3", V(c2="fail", c3="fail"))],
    }
    judge = {"b1": J(c3="pass"), "b2": J(c3="pass"), "b3": J(c2="fail", c3="fail")}
    r = review(histories=hist, blind={"b1", "b2", "b3"}, judge=judge)
    c = r["corrections"]
    assert c["n_corrected"] == 1
    assert c["traces"] == ["b1"]
    # b1 errava na correcao (juiz pass, humano fail): falso positivo, que afeta o TNR
    assert c["judge_first"]["C3"]["tnr"] == 1.0
    assert c["judge_latest"]["C3"]["tnr"] == 0.5
    assert c["judge_first"]["C3"]["tnr"] != c["judge_latest"]["C3"]["tnr"]


def test_correcoes_sem_juiz_mantem_contagem():
    hist = {"b1": [anotacao_cega("b1", V()), anotacao_cega("b1", V(), version=2)]}
    r = review(histories=hist, blind={"b1"}, judge=None)
    assert r["corrections"]["n_corrected"] == 1
    assert r["corrections"]["judge_first"] is None
    assert r["corrections"]["judge_latest"] is None


# ---- 7. gabaritos
def test_gabaritos_comparam_como_conjunto_e_contam_disputas():
    cases = {
        "c1": {"case_id": "c1", "gabarito": {"answer_exists": "sim",
               "expected_provisions": ["CF.art1", "CF.art2"],
               "reference_date": "2026-01-01", "disputed": False}},
        "c2": {"case_id": "c2", "gabarito": {"answer_exists": "sim",
               "expected_provisions": ["CF.art1"],
               "reference_date": "2026-01-01", "disputed": True}},
        "c3": {"case_id": "c3", "gabarito": {"answer_exists": "nao",
               "expected_provisions": [],
               "reference_date": "2026-01-01", "disputed": False}},
    }
    drafts = {
        "c1": {"case_id": "c1", "answer_exists": "sim",
               "expected_provisions": ["CF.art2", "CF.art1"],
               "reference_date": "2026-01-01", "disputed": False},
        "c2": {"case_id": "c2", "answer_exists": "sim",
               "expected_provisions": ["CF.art1", "CF.art3"],
               "reference_date": "2026-01-01", "disputed": False},
    }
    g = review(cases=cases, gabarito_drafts=drafts)["gabaritos"]
    assert g == {"drafted": 2, "changed": 1, "disputed": 1}


# ---- 8. renderizacao
def test_render_marca_falta_de_juiz_e_nao_calibrado():
    hist = {"b1": [anotacao_cega("b1", V(c3="pass"))]}
    sem = "\n".join(render_review_markdown(review(histories=hist, blind={"b1"}, judge=None)))
    assert "_Sem juiz ainda._" in sem
    com = "\n".join(render_review_markdown(review(
        histories=hist, blind={"b1"}, judge={"b1": J(c3="pass")})))
    assert "não calibrado" in com
    assert "_Sem juiz ainda._" not in com


# ---- 9. collect a partir do disco
def _escreve(p: Path, data) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")


def _monta_arvore(base: Path):
    ann = base / "annotations"
    _escreve(ann / "b1.v1.json", anotacao_cega("b1", V(c3="pass"), version=1))
    _escreve(ann / "b1.v2.json", anotacao_cega("b1", V(c3="fail"), version=2))
    _escreve(ann / "r1.v1.json", anotacao_revisada("r1", V(c1="pass"), version=1))
    _escreve(ann / "consistency" / "b1.v1.json", anotacao_cega("b1", V(c3="pass"), version=1))
    _escreve(ann / "_samples.json", {
        "blind": {"seed": 1, "n": 2, "trace_ids": ["b1", "b2"]},
        "consistency": {"seed": 2, "n": 1, "trace_ids": ["b1"]},
    })
    drafts = base / "drafts"
    _escreve(drafts / "annotations" / "b1.json", rascunho("b1", V(c3="pass")))
    _escreve(drafts / "annotations" / "r1.json", rascunho("r1", V(c1="fail")))
    _escreve(drafts / "cases" / "c1.v1.json", {"case_id": "c1", "answer_exists": "sim",
             "expected_provisions": ["CF.art1"], "reference_date": "2026-01-01", "disputed": False})
    _escreve(drafts / "cases" / "c1.v2.json", {"case_id": "c1", "answer_exists": "sim",
             "expected_provisions": ["CF.art1", "CF.art2"], "reference_date": "2026-01-01",
             "disputed": False})
    cases = base / "cases"
    _escreve(cases / "c1.json", {"case_id": "c1", "question": "Pergunta?", "hypothesis": ["H1"],
             "split": "teste", "gabarito": {"answer_exists": "sim",
             "expected_provisions": ["CF.art1"], "reference_date": "2026-01-01", "disputed": True}})
    _escreve(base / "traces" / "sub" / "c1-abcdef12.json",
             {"trace_id": "c1-abcdef12", "case_id": "c1"})
    _escreve(base / "traces" / "sub" / "anotacoes.json", {"nao": "e trace"})
    _escreve(base / "judgments" / "b1.json", {"verdicts": J(c3="pass")})


def test_collect_le_a_arvore_e_alimenta_build_review(tmp_path: Path):
    _monta_arvore(tmp_path)
    inputs = collect_review_inputs(
        annotations_dir=tmp_path / "annotations",
        drafts_dir=tmp_path / "drafts",
        samples_path=tmp_path / "annotations" / "_samples.json",
        cases_dir=tmp_path / "cases",
        traces_dir=tmp_path / "traces",
        judgments_dir=tmp_path / "judgments",
    )
    assert set(inputs["histories"]) == {"b1", "r1"}
    assert len(inputs["histories"]["b1"]) == 2
    assert inputs["consistency"]["b1"]["trace_id"] == "b1"
    assert inputs["blind"] == {"b1", "b2"}
    assert inputs["consistency_ids"] == {"b1"}
    assert set(inputs["annotation_drafts"]) == {"b1", "r1"}
    assert inputs["gabarito_drafts"]["c1"]["expected_provisions"] == ["CF.art1", "CF.art2"]
    assert inputs["disputed_traces"] == {"c1-abcdef12"}
    assert inputs["judge"] == {"b1": J(c3="pass")}
    assert "c1" in inputs["cases"]

    r = build_review(**inputs)
    assert r["counts"]["total"] == 2
    assert r["gabaritos"] == {"drafted": 1, "changed": 1, "disputed": 1}
    assert r["self_agreement"]["C3"]["total"] == 1
    assert r["self_agreement"]["C3"]["agree"] == 1


def test_collect_sem_juiz_nem_pastas_devolve_none_sem_erro(tmp_path: Path):
    inputs = collect_review_inputs(
        annotations_dir=tmp_path / "annotations",
        drafts_dir=tmp_path / "drafts",
        samples_path=tmp_path / "annotations" / "_samples.json",
        cases_dir=tmp_path / "cases",
        traces_dir=tmp_path / "traces",
        judgments_dir=None,
    )
    assert inputs["judge"] is None
    assert inputs["histories"] == {}
    r = build_review(**inputs)
    assert r["judge_blind"] is None


# ---- 10. hook no relatorio
def test_relatorio_so_ganha_secao_de_revisao_quando_ela_existe():
    rep = build_report(HEADER, [], {})
    assert "## Revisão da anotação" not in render_markdown(rep)
    rep["review"] = review()
    md = render_markdown(rep)
    assert "## Revisão da anotação" in md
    assert md.index("## Revisão da anotação") > md.index("Desenvolvimento")


def test_criterios_do_modulo_sao_os_quatro_da_anotacao():
    assert CRITERIA == ("C1", "C2", "C3", "C4")


def test_ancoragem_na_fronteira_exata_nao_marca():
    # Erro do rascunhador 0,4 e mudanca 0,2: exatamente a metade nao e "menos que a metade".
    r = review(**_cenario_ancoragem(erros_redator=4, mudancas=2))
    a = r["anchoring"]["C1"]
    assert a["change_rate"] == pytest.approx(0.2)
    assert a["flag"] is False
