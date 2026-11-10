import json
from pathlib import Path

import pytest

from evals.checks import CheckResult
from evals.report import (
    resolve_verdict, build_report, compare, render_markdown, write_report, load_report,
)

HEADER = {
    "models": ["modelo-a"],
    "judge": {"model": "juiz-x", "version": "2026-01"},
    "p2_tag": "step-16", "corpus_version": "abc", "seed": 7,
    "prices": {"modelo-a": [1.0, 2.0]}, "date": "2026-11-10",
}


def row(trace_id, split, cond, **verdicts):
    return {"trace_id": trace_id, "split": split, "condition": cond, "verdicts": verdicts}


# ---- resolve_verdict
def test_code_decides_when_it_can():
    assert resolve_verdict(CheckResult("fail", ["x"]), "pass") == ("fail", "code")
    assert resolve_verdict(CheckResult("pass"), "fail") == ("pass", "code")


def test_needs_judge_uses_the_judge_verdict():
    assert resolve_verdict(CheckResult("needs_judge"), "pass") == ("pass", "judge")
    assert resolve_verdict(CheckResult("needs_judge"), "fail") == ("fail", "judge")


def test_no_code_check_uses_the_judge():
    assert resolve_verdict(None, "fail") == ("fail", "judge")


def test_needs_judge_without_judge_is_pending_not_invented():
    assert resolve_verdict(CheckResult("needs_judge"), None) == ("n/a", "pendente")
    assert resolve_verdict(None, None) == ("n/a", "pendente")


# ---- build_report
def _rows():
    rows = []
    for i in range(70):  # teste: C1 56 pass / 14 fail por codigo
        rows.append(row(f"t{i}", "teste", "local-skill",
                        C1=("pass" if i < 56 else "fail", "code"),
                        C3=("n/a", "pendente") if i < 10 else ("pass", "judge")))
    for i in range(30):  # desenvolvimento: tudo aprovado
        rows.append(row(f"d{i}", "desenvolvimento", "local-skill", C1=("pass", "code"),
                        C3=("pass", "judge")))
    return rows


def test_main_rates_use_only_the_test_split():
    rep = build_report(HEADER, _rows(), {})
    c1 = rep["rates"]["local-skill"]["C1"]
    assert (c1["n"], c1["pass"]) == (70, 56)
    assert c1["rate"] == pytest.approx(0.8)
    assert c1["ci"][0] == pytest.approx(0.692, abs=0.005)
    assert c1["ci"][1] == pytest.approx(0.877, abs=0.005)
    assert c1["decided_by"] == {"code": 70, "judge": 0}


def test_development_goes_only_to_dev_diagnostic():
    rep = build_report(HEADER, _rows(), {})
    assert rep["dev_diagnostic"]["local-skill"]["C1"]["n"] == 30
    assert rep["dev_diagnostic"]["local-skill"]["C1"]["rate"] == 1.0
    assert rep["rates"]["local-skill"]["C1"]["n"] == 70  # nao misturou


def test_pending_verdicts_are_excluded_and_counted_apart():
    c3 = build_report(HEADER, _rows(), {})["rates"]["local-skill"]["C3"]
    assert c3["n"] == 60 and c3["excluded"] == 10
    assert c3["decided_by"] == {"code": 0, "judge": 60}


def test_conditions_are_never_mixed_in_one_rate():
    rows = [row("a", "teste", "local-skill", C1=("pass", "code")),
            row("b", "teste", "local-sem-skill", C1=("fail", "code"))]
    rep = build_report(HEADER, rows, {})
    assert rep["rates"]["local-skill"]["C1"]["rate"] == 1.0
    assert rep["rates"]["local-sem-skill"]["C1"]["rate"] == 0.0


def test_empty_criterion_has_no_rate_and_no_interval():
    rows = [row("a", "teste", "local-skill", C1=("n/a", "pendente"))]
    c1 = build_report(HEADER, rows, {})["rates"]["local-skill"]["C1"]
    assert c1["n"] == 0 and c1["rate"] is None and c1["ci"] is None


def test_judge_calibration_needs_enough_of_both_classes():  # foco da revisao 4
    metrics = {
        "C3": {"tpr": 0.9, "tnr": 0.8, "n_pos": 20, "n_neg": 12},
        "C2": {"tpr": 0.9, "tnr": None, "n_pos": 20, "n_neg": 0},
        "C4": {"tpr": 0.9, "tnr": 0.5, "n_pos": 20, "n_neg": 9},
        "C1": {"tpr": 0.9, "tnr": 0.5, "n_pos": 9, "n_neg": 20},
    }
    j = build_report(HEADER, [], metrics)["judge"]
    assert j["C3"]["calibrated"] is True
    assert j["C2"]["calibrated"] is False and j["C2"]["tnr"] is None
    assert j["C4"]["calibrated"] is False
    assert j["C1"]["calibrated"] is False


def test_usage_is_carried_into_the_report():
    rep = build_report(HEADER, [], {}, usage={"cost_usd": 1.5, "input_tokens": 10, "output_tokens": 5})
    assert rep["usage"]["cost_usd"] == 1.5


# ---- compare
def _rep(rate_pass, n, cond="local-skill"):
    rows = [row(f"x{i}", "teste", cond, C1=("pass" if i < rate_pass else "fail", "code"))
            for i in range(n)]
    return build_report(HEADER, rows, {})


def test_compare_flags_overlap_as_noise():
    out = compare(_rep(56, 70), _rep(52, 70))  # 80% x 74%: intervalos se sobrepoem
    assert len(out) == 1
    assert out[0]["label"] == "dentro do ruído"
    assert out[0]["delta"] == pytest.approx(52 / 70 - 56 / 70)


def test_compare_flags_separated_intervals_as_real():
    out = compare(_rep(68, 70), _rep(35, 70))
    assert out[0]["label"] == "diferença real"
    assert out[0]["delta"] < 0


def test_compare_skips_conditions_missing_on_one_side():
    assert compare(_rep(56, 70, "local-skill"), _rep(56, 70, "remoto")) == []


def test_compare_without_data_is_labelled_not_invented():
    vazio = build_report(HEADER, [row("a", "teste", "local-skill", C1=("n/a", "pendente"))], {})
    out = compare(vazio, _rep(56, 70))
    assert out[0]["label"] == "sem dados"


# ---- render / write
def test_markdown_has_reproduction_header_and_declares_uncalibrated():
    rep = build_report(HEADER, _rows(), {
        "C3": {"tpr": 0.9, "tnr": None, "n_pos": 20, "n_neg": 0}})
    md = render_markdown(rep)
    assert "step-16" in md and "juiz-x" in md and "2026-01" in md
    assert "não calibrado" in md
    assert "local-skill" in md


def test_markdown_separates_the_development_diagnostic():
    md = render_markdown(build_report(HEADER, _rows(), {}))
    assert md.index("Desenvolvimento") > md.index("Teste")


def test_write_report_is_stable_json(tmp_path: Path):
    rep = build_report(HEADER, _rows(), {})
    p = tmp_path / "r.json"
    write_report(rep, p)
    texto = p.read_text(encoding="utf-8")
    assert texto.endswith("\n")
    assert load_report(p) == rep
    # chaves ordenadas: o diff do git fica legivel
    assert texto == json.dumps(rep, sort_keys=True, indent=2, ensure_ascii=False) + "\n"


def test_incoherent_metrics_with_missing_rate_are_never_calibrated():
    # TNR nulo com muitos reprovados nao devia acontecer; se acontecer, nao e "calibrado".
    j = build_report(HEADER, [], {"C3": {"tpr": 0.9, "tnr": None, "n_pos": 20, "n_neg": 12}})["judge"]
    assert j["C3"]["calibrated"] is False
