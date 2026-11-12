import pytest

from evals.metrics import Agreement, confusion, self_agreement


def human_ann(tid: str, verdict: str) -> dict:
    return {
        "trace_id": tid,
        "verdicts": {"C1": verdict, "C2": "pass", "C3": "pass", "C4": "n/a"},
        "note": "nota de fail" if verdict == "fail" else "",
        "uncertain": [],
        "kind": "blind",
        "draft": None,
    }


def make_human_sample() -> list[dict]:
    # t01 a t08 são pass; t09 e t10 são fail
    return [human_ann(f"t{i:02d}", "pass") for i in range(1, 9)] + [
        human_ann("t09", "fail"),
        human_ann("t10", "fail"),
    ]


def test_confusion_example_from_plan():
    human = make_human_sample()
    judge = {
        **{f"t{i:02d}": {"C1": "pass"} for i in range(1, 8)},
        "t08": {"C1": "fail"},
        "t09": {"C1": "fail"},
        "t10": {"C1": "pass"},
    }
    m = confusion(human, judge, "C1")
    assert (m.tp, m.fn, m.fp, m.tn) == (7, 1, 1, 1)
    assert m.n_pos == 8
    assert m.n_neg == 2
    assert m.tpr == pytest.approx(0.875)
    assert m.tnr == pytest.approx(0.5)


def test_judge_approving_everything():
    human = make_human_sample()
    judge = {f"t{i:02d}": {"C1": "pass"} for i in range(1, 11)}
    m = confusion(human, judge, "C1")
    assert (m.tp, m.fn, m.fp, m.tn) == (8, 0, 2, 0)
    assert m.n_pos == 8
    assert m.n_neg == 2
    assert m.tpr == pytest.approx(1.0)
    assert m.tnr == pytest.approx(0.0)


def test_judge_rejecting_everything():
    human = make_human_sample()
    judge = {f"t{i:02d}": {"C1": "fail"} for i in range(1, 11)}
    m = confusion(human, judge, "C1")
    assert (m.tp, m.fn, m.fp, m.tn) == (0, 8, 0, 2)
    assert m.n_pos == 8
    assert m.n_neg == 2
    assert m.tpr == pytest.approx(0.0)
    assert m.tnr == pytest.approx(1.0)


def test_judge_perfect_agreement():
    human = make_human_sample()
    judge = {h["trace_id"]: {"C1": h["verdicts"]["C1"]} for h in human}
    m = confusion(human, judge, "C1")
    assert (m.tp, m.fn, m.fp, m.tn) == (8, 0, 0, 2)
    assert m.n_pos == 8
    assert m.n_neg == 2
    assert m.tpr == pytest.approx(1.0)
    assert m.tnr == pytest.approx(1.0)


def test_no_negative_traces_gives_undefined_tnr():
    human = [human_ann(f"t{i:02d}", "pass") for i in range(1, 6)]
    judge = {
        **{f"t{i:02d}": {"C1": "pass"} for i in range(1, 5)},
        "t05": {"C1": "fail"},
    }
    m = confusion(human, judge, "C1")
    assert m.tnr is None
    assert m.n_neg == 0
    assert m.tpr == pytest.approx(0.8)
    assert m.n_pos == 5


def test_no_positive_traces_gives_undefined_tpr():
    human = [human_ann(f"t{i:02d}", "fail") for i in range(1, 6)]
    judge = {
        "t01": {"C1": "fail"},
        "t02": {"C1": "fail"},
        "t03": {"C1": "fail"},
        "t04": {"C1": "pass"},
        "t05": {"C1": "pass"},
    }
    m = confusion(human, judge, "C1")
    assert m.tpr is None
    assert m.n_pos == 0
    assert m.tnr == pytest.approx(0.6)
    assert m.n_neg == 5


def test_missing_trace_in_judge_raises_error():
    human = make_human_sample()
    judge = {h["trace_id"]: {"C1": h["verdicts"]["C1"]} for h in human}
    del judge["t03"]

    with pytest.raises(ValueError) as exc:
        confusion(human, judge, "C1")
    msg = str(exc.value)
    assert "t03" in msg
    assert "C1" in msg


def test_missing_criterion_in_judge_raises_error():
    human = make_human_sample()
    judge = {h["trace_id"]: {"C1": h["verdicts"]["C1"]} for h in human}
    judge["t03"] = {"C2": "pass"}  # tem t03, mas falta C1

    with pytest.raises(ValueError) as exc:
        confusion(human, judge, "C1")
    msg = str(exc.value)
    assert "t03" in msg
    assert "C1" in msg


def test_multiple_missing_traces_in_judge_reported_sorted():
    # Inverte a lista humana para que t07 seja visitado antes de t03
    human = list(reversed(make_human_sample()))
    judge = {h["trace_id"]: {"C1": h["verdicts"]["C1"]} for h in human}
    del judge["t07"]
    del judge["t03"]

    with pytest.raises(ValueError) as exc:
        confusion(human, judge, "C1")
    msg = str(exc.value)
    assert "C1" in msg
    assert "t03, t07" in msg


def test_judge_with_extra_traces_ignored():
    human = make_human_sample()
    judge = {h["trace_id"]: {"C1": h["verdicts"]["C1"]} for h in human}
    judge["t99"] = {"C1": "pass"}

    m = confusion(human, judge, "C1")
    assert (m.tp, m.fn, m.fp, m.tn) == (8, 0, 0, 2)
    assert m.n_pos == 8
    assert m.n_neg == 2
    assert m.tpr == pytest.approx(1.0)
    assert m.tnr == pytest.approx(1.0)


def test_judge_invalid_format_raises_error():
    human = make_human_sample()
    judge = {h["trace_id"]: "pass" for h in human}  # string em vez de dict

    with pytest.raises(ValueError) as exc:
        confusion(human, judge, "C1")
    msg = str(exc.value)
    assert "formato inválido" in msg
    assert "esperado" in msg


def test_duplicate_trace_id_in_human_raises_error():
    human = make_human_sample() + [human_ann("t03", "pass")]
    judge = {h["trace_id"]: {"C1": "pass"} for h in human}

    with pytest.raises(ValueError) as exc:
        confusion(human, judge, "C1")
    msg = str(exc.value)
    assert "duplicado" in msg
    assert "t03" in msg


def test_na_on_human_side_excluded_from_counts():
    human = make_human_sample() + [
        {
            "trace_id": "t11",
            "verdicts": {"C1": "n/a", "C2": "pass", "C3": "pass", "C4": "n/a"},
            "note": "",
            "uncertain": [],
            "kind": "blind",
            "draft": None,
        }
    ]
    judge = {h["trace_id"]: {"C1": h["verdicts"]["C1"]} for h in human}
    judge["t11"] = {"C1": "pass"}

    m = confusion(human, judge, "C1")
    assert (m.tp, m.fn, m.fp, m.tn) == (8, 0, 0, 2)
    assert m.n_pos == 8
    assert m.n_neg == 2
    assert m.n_na == 1
    assert m.n_disputed == 0


def test_na_on_judge_side_excluded_from_counts():
    human = make_human_sample() + [human_ann("t11", "pass")]
    judge = {h["trace_id"]: {"C1": h["verdicts"]["C1"]} for h in human}
    judge["t11"] = {"C1": "n/a"}

    m = confusion(human, judge, "C1")
    assert (m.tp, m.fn, m.fp, m.tn) == (8, 0, 0, 2)
    assert m.n_pos == 8
    assert m.n_neg == 2
    assert m.n_na == 1
    assert m.n_disputed == 0


def test_disputed_trace_excluded_from_counts():
    human = make_human_sample()
    judge = {h["trace_id"]: {"C1": h["verdicts"]["C1"]} for h in human}

    m = confusion(human, judge, "C1", disputed=frozenset({"t09"}))
    assert (m.tp, m.fn, m.fp, m.tn) == (8, 0, 0, 1)
    assert m.n_pos == 8
    assert m.n_neg == 1
    assert m.tpr == pytest.approx(1.0)
    assert m.tnr == pytest.approx(1.0)
    assert m.n_disputed == 1
    assert m.n_na == 0


def test_disputed_trace_does_not_require_judge_verdict():
    human = make_human_sample()
    judge = {h["trace_id"]: {"C1": h["verdicts"]["C1"]} for h in human}
    del judge["t09"]

    m = confusion(human, judge, "C1", disputed=frozenset({"t09"}))
    assert (m.tp, m.fn, m.fp, m.tn) == (8, 0, 0, 1)
    assert m.n_disputed == 1


def test_revised_annotation_is_rejected():
    human = make_human_sample()
    human[4]["kind"] = "revised"  # t05
    judge = {h["trace_id"]: {"C1": h["verdicts"]["C1"]} for h in human}

    with pytest.raises(ValueError) as exc:
        confusion(human, judge, "C1")
    msg = str(exc.value)
    assert "t05" in msg
    assert "cega" in msg.lower() or "blind" in msg.lower()


def test_missing_kind_is_rejected():
    human = make_human_sample()
    del human[4]["kind"]  # t05
    judge = {h["trace_id"]: {"C1": h["verdicts"]["C1"]} for h in human}

    with pytest.raises(ValueError) as exc:
        confusion(human, judge, "C1")
    msg = str(exc.value)
    assert "t05" in msg


def test_multiple_non_blind_annotations_reported_sorted():
    human = make_human_sample()
    human[4]["kind"] = "revised"  # t05
    human[1]["kind"] = "revised"  # t02
    judge = {h["trace_id"]: {"C1": h["verdicts"]["C1"]} for h in human}

    with pytest.raises(ValueError) as exc:
        confusion(human, judge, "C1")
    msg = str(exc.value)
    assert "t02, t05" in msg


@pytest.mark.parametrize(
    ("side", "bad_val"),
    [
        ("human", "sim"),
        ("judge", "aprovado"),
        ("judge", ["pass"]),
    ],
)
def test_invalid_verdict_value_is_rejected(side, bad_val):
    human = make_human_sample()
    judge = {h["trace_id"]: {"C1": h["verdicts"]["C1"]} for h in human}

    if side == "human":
        human[0]["verdicts"]["C1"] = bad_val
    else:
        judge["t01"]["C1"] = bad_val

    with pytest.raises(ValueError) as exc:
        confusion(human, judge, "C1")
    msg = str(exc.value)
    assert "t01" in msg
    assert repr(bad_val) in msg


def test_multiple_invalid_verdict_values_reported_sorted():
    human = list(reversed(make_human_sample()))
    judge = {h["trace_id"]: {"C1": h["verdicts"]["C1"]} for h in human}
    # Invalida t08 e t02 em ordem inversa de id na iteração
    judge["t08"]["C1"] = "sim"
    judge["t02"]["C1"] = "não"

    with pytest.raises(ValueError) as exc:
        confusion(human, judge, "C1")
    msg = str(exc.value)
    assert "t02 (juiz='não'), t08 (juiz='sim')" in msg


def ann(tid: str, **verdicts) -> dict:
    v = {"C1": "pass", "C2": "pass", "C3": "pass", "C4": "n/a"}
    v.update(verdicts)
    has_fail = any(val == "fail" for val in v.values())
    return {
        "trace_id": tid,
        "verdicts": v,
        "note": "nota de fail" if has_fail else "",
        "uncertain": [],
        "kind": "blind",
        "draft": None,
    }


def test_self_agreement_c3_different_on_one_trace():
    first = [ann(f"t{i:02d}") for i in range(1, 11)]
    second = [ann(f"t{i:02d}") for i in range(1, 11)]
    second[4] = ann("t05", C3="fail")

    res = self_agreement(first, second)
    assert res["C3"].agree == 9
    assert res["C3"].total == 10
    assert res["C3"].rate == pytest.approx(0.9)

    assert res["C1"].agree == 10
    assert res["C1"].total == 10
    assert res["C1"].rate == pytest.approx(1.0)

    assert res["C2"].agree == 10
    assert res["C2"].total == 10
    assert res["C2"].rate == pytest.approx(1.0)

    assert res["C4"].agree == 0
    assert res["C4"].total == 0
    assert res["C4"].n_na == 10
    assert res["C4"].rate is None

    # Simetria: inverter as listas dá o mesmo resultado
    res_inv = self_agreement(second, first)
    assert res_inv == res


def test_self_agreement_c4_partial_na():
    first = [ann(f"t{i:02d}") for i in range(1, 8)] + [
        ann(f"t{i:02d}", C4="pass") for i in range(8, 11)
    ]
    second = [ann(f"t{i:02d}") for i in range(1, 8)] + [
        ann(f"t{i:02d}", C4="pass") for i in range(8, 11)
    ]

    res = self_agreement(first, second)
    c4 = res["C4"]
    assert c4.n_na == 7
    assert c4.total == 3
    assert c4.agree == 3
    assert c4.rate == pytest.approx(1.0)


def test_self_agreement_extra_trace_in_second_rejected():
    first = [ann("t01")]
    second = [ann("t01"), ann("t02")]

    with pytest.raises(ValueError) as exc:
        self_agreement(first, second)
    msg = str(exc.value)
    assert "t02" in msg


def test_self_agreement_extra_trace_in_first_rejected():
    first = [ann("t01"), ann("t02")]
    second = [ann("t01")]

    with pytest.raises(ValueError) as exc:
        self_agreement(first, second)
    msg = str(exc.value)
    assert "t02" in msg


def test_self_agreement_non_blind_rejected():
    first = [ann("t01")]
    second = [ann("t01")]
    first[0]["kind"] = "revised"

    with pytest.raises(ValueError) as exc:
        self_agreement(first, second)
    msg = str(exc.value)
    assert "t01" in msg
    assert "cega" in msg.lower() or "blind" in msg.lower()


def test_self_agreement_duplicate_trace_id_rejected():
    first = [ann("t01"), ann("t01")]
    second = [ann("t01")]

    with pytest.raises(ValueError) as exc:
        self_agreement(first, second)
    msg = str(exc.value)
    assert "t01" in msg
    assert "duplicado" in msg


def test_self_agreement_unilateral_na_rejected():
    first = [ann("t01", C4="n/a")]
    second = [ann("t01", C4="pass")]

    with pytest.raises(ValueError) as exc:
        self_agreement(first, second)
    msg = str(exc.value)
    assert "t01" in msg
    assert "C4" in msg
    assert "n/a" in msg


def test_self_agreement_invalid_verdict_rejected():
    first = [ann("t01", C1="sim")]
    second = [ann("t01")]

    with pytest.raises(ValueError) as exc:
        self_agreement(first, second)
    msg = str(exc.value)
    assert "t01" in msg
    assert "'sim'" in msg





