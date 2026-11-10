import json
import random
from pathlib import Path

from evals.cases import extract_ids, validate_case, load_cases, assign_splits, apply_splits
from evals.privacy import make_synthetic_cpf


def make_case(cid="c01", **over) -> dict:
    base = {
        "case_id": cid, "question": "Desde quando a CBS pode ser cobrada?",
        "hypothesis": ["H4"], "split": None, "subsets": [],
        "gabarito": {"answer_exists": "sim", "expected_provisions": ["ADCT.art126"],
                     "reference_date": "2027-01-01", "disputed": False},
    }
    base.update(over)
    return base


def test_extract_ids_handles_real_shapes():
    texto = ("Veja CF.art156-A.par1.incIX, ADCT.art126.incI.alia, LC214.art125, "
             "EC132.art23 e ADCT.art124.parunico.")
    assert extract_ids(texto) == {
        "CF.art156-A.par1.incIX", "ADCT.art126.incI.alia", "LC214.art125",
        "EC132.art23", "ADCT.art124.parunico"}


def test_extract_ids_does_not_cut_a_longer_id():
    assert extract_ids("CF.art155.par3") == {"CF.art155.par3"}
    assert extract_ids("texto sem id art. 156-A") == set()


def test_valid_case_has_no_errors():
    assert validate_case(make_case()) == []


def test_incoherent_gabarito_is_rejected():
    c = make_case(); c["gabarito"]["answer_exists"] = "nao"
    assert validate_case(c)  # "nao" com dispositivo esperado
    c = make_case(); c["gabarito"]["expected_provisions"] = []
    assert validate_case(c)  # "sim" sem dispositivo esperado


def test_bad_id_hypothesis_date_are_rejected():
    c = make_case(); c["gabarito"]["expected_provisions"] = ["artigo 5"]
    assert validate_case(c)
    assert validate_case(make_case(hypothesis=["H99"]))
    c = make_case(); c["gabarito"]["reference_date"] = "31/12/2027"
    assert validate_case(c)


def test_question_with_taxpayer_number_is_rejected_but_placeholder_is_ok():
    cpf = make_synthetic_cpf(random.Random(1))
    assert validate_case(make_case(question=f"meu cpf {cpf}"))
    assert validate_case(make_case(question="meu cpf {CPF}, qual a aliquota?")) == []


def _many(n=100):
    return [make_case(f"c{i:03d}", hypothesis=[f"H{(i % 14) + 1}"]) for i in range(n)]


def test_split_is_deterministic_and_changes_with_seed():
    cases = _many()
    assert assign_splits(cases, 7) == assign_splits(cases, 7)
    assert assign_splits(cases, 7) != assign_splits(cases, 8)


def test_split_is_stratified_and_close_to_30_percent():
    cases = _many()
    out = assign_splits(cases, 7)
    dev = [c for c in cases if out[c["case_id"]] == "desenvolvimento"]
    assert 25 <= len(dev) <= 35
    hip_dev = {c["hypothesis"][0] for c in dev}
    assert len(hip_dev) >= 12  # quase todas as hipoteses aparecem no desenvolvimento


def test_apply_splits_writes_files_and_seed(tmp_path: Path):
    for c in _many(10):
        (tmp_path / f"{c['case_id']}.json").write_text(json.dumps(c), encoding="utf-8")
    out = apply_splits(tmp_path, seed=3)
    carregados = {c["case_id"]: c["split"] for c in load_cases(tmp_path)}
    assert carregados == out
    assert json.loads((tmp_path / "_split_meta.json").read_text())["seed"] == 3


def test_extract_ids_rejects_an_id_with_a_garbage_suffix():
    # Sem a barreira no fim do padrao, "CF.art155.par3x" viraria "CF.art155.par3".
    assert extract_ids("CF.art155.par3x") == set()


def test_split_keeps_each_hypothesis_proportion():
    # A estratificacao e por hipotese: em cada uma, o desenvolvimento tem ~30%.
    cases = _many()
    out = assign_splits(cases, 7)
    por_hip: dict[str, list[str]] = {}
    for c in cases:
        por_hip.setdefault(c["hypothesis"][0], []).append(out[c["case_id"]])
    for h, splits in por_hip.items():
        assert splits.count("desenvolvimento") == round(len(splits) * 0.3), h
