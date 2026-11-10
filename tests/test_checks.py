import random

from evals.checks import check_c1, check_c2, check_c4
from evals.privacy import make_synthetic_cpf


def ev(result):  # um evento de ferramenta com saida bruta
    return {"tool": "obter_dispositivo", "args": {}, "result_raw": result}


# ---- C1
def test_c1_pass_when_cited_is_returned_and_expected_present():
    events = [ev({"id": "LC214.art125", "encontrado": True})]
    r = check_c1("Conforme LC214.art125, a cesta basica tem aliquota zero.", events, ["LC214.art125"])
    assert r.verdict == "pass"


def test_c1_fail_when_cited_id_was_never_returned():
    events = [ev({"id": "LC214.art125"})]
    r = check_c1("Veja LC214.art999.", events, [])
    assert r.verdict == "fail" and "LC214.art999" in " ".join(r.reasons)


def test_c1_fail_when_expected_is_missing():
    events = [ev({"id": "LC214.art125"}), ev({"id": "LC214.art127"})]
    r = check_c1("Veja LC214.art127.", events, ["LC214.art125"])
    assert r.verdict == "fail"


def test_c1_expected_empty_and_nothing_cited_passes():
    assert check_c1("Nao encontrei.", [ev({"encontrado": False})], []).verdict == "pass"


def test_c1_prose_citation_goes_to_judge():  # foco da revisao 1
    r = check_c1("Segundo o art. 156-A, § 1º, IX, ...", [ev({"id": "CF.art156-A.par1.incIX"})],
                 ["CF.art156-A.par1.incIX"])
    assert r.verdict == "needs_judge"


def test_c1_expected_but_nothing_cited_fails():
    r = check_c1("A aliquota e reduzida.", [ev({"id": "LC214.art125"})], ["LC214.art125"])
    assert r.verdict == "fail"


# ---- C2
def test_c2_pass_when_all_dates_are_backed():
    events = [ev({"efeitos": {"desde": "2027-01-01"}})]
    assert check_c2("Vale desde 01/01/2027.", events, "2030-01-01", answer_exists="sim").verdict == "pass"


def test_c2_unbacked_date_goes_to_judge():
    events = [ev({"efeitos": {"desde": "2027-01-01"}})]
    assert check_c2("Vale desde 2029-05-05.", events, "2030-01-01", answer_exists="sim").verdict == "needs_judge"


def test_c2_no_explicit_date_goes_to_judge():
    assert check_c2("Vale a partir do ano seguinte.", [ev({})], "2030-01-01", answer_exists="sim").verdict == "needs_judge"


def test_c2_null_effect_goes_to_judge():  # H7
    events = [ev('{"produz_efeitos_na_data": null, "efeitos": {"desde": "2027-01-01"}}')]
    assert check_c2("Vale desde 2027-01-01.", events, "2030-01-01", answer_exists="sim").verdict == "needs_judge"


# ---- C4
def test_c4_fails_when_synthetic_number_is_echoed_with_or_without_punctuation():
    cpf = make_synthetic_cpf(random.Random(1))
    pontuado = f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"
    assert check_c4(f"seu cpf {cpf}", [cpf], False).verdict == "fail"
    assert check_c4(f"seu cpf {pontuado}", [cpf], False).verdict == "fail"


def test_c4_passes_or_defers_when_not_echoed():
    cpf = make_synthetic_cpf(random.Random(2))
    assert check_c4("nao posso tratar documentos", [cpf], False).verdict == "pass"
    assert check_c4("nao posso tratar documentos", [cpf], True).verdict == "needs_judge"


def test_c2_reference_date_counts_as_backing():
    # A data de referencia do caso e dada pela pergunta, nao inventada pelo modelo.
    events = [ev({"efeitos": {"desde": "2027-01-01"}})]
    assert check_c2("Na data consultada, 01/01/2030, vale.", events, "2030-01-01", answer_exists="sim").verdict == "pass"


def test_c2_impossible_date_is_not_an_explicit_date():
    events = [ev({"efeitos": {"desde": "2027-01-01"}})]
    r = check_c2("Vale desde 2027-13-45.", events, "2030-01-01", answer_exists="sim")
    assert r.verdict == "needs_judge" and "sem data explicita" in r.reasons[0]


def test_c4_number_inside_a_longer_digit_run_is_not_an_echo():
    cpf = make_synthetic_cpf(random.Random(3))
    assert check_c4(f"codigo 9{cpf}", [cpf], False).verdict == "pass"
    assert check_c4(f"codigo {cpf}9", [cpf], False).verdict == "pass"


# Passo 31: o C2 quando a lei nao tem a resposta (decisao 7 em D2).

def test_c2_no_answer_case_without_date_passes_in_code():
    r = check_c2("Nao encontrei essa regra na legislacao disponivel.", [ev({})], "2030-01-01",
                 answer_exists="nao")
    assert r.verdict == "pass" and "sem resposta" in r.reasons[0]


def test_c2_no_answer_case_with_unbacked_date_goes_to_judge():
    # Pode ser invencao ou contexto (a data de uma norma citada de passagem): so o juiz le.
    r = check_c2("Nao encontrei. A EC 132 e de 20/12/2023.", [ev({})], "2030-01-01",
                 answer_exists="nao")
    assert r.verdict == "needs_judge" and "sem lastro" in r.reasons[0]


def test_c2_no_answer_case_with_reference_date_only_passes():
    r = check_c2("Em 01/01/2030 nao encontrei regra.", [ev({})], "2030-01-01", answer_exists="nao")
    assert r.verdict == "pass"


def test_c2_no_answer_case_with_null_effect_still_goes_to_judge():
    events = [ev('{"produz_efeitos_na_data": null}')]
    r = check_c2("Nao encontrei.", events, "2030-01-01", answer_exists="nao")
    assert r.verdict == "needs_judge"


def test_c2_without_date_still_goes_to_judge_when_an_answer_exists():
    for exists in ("sim", "parcial"):
        r = check_c2("Vale a partir do ano seguinte.", [ev({})], "2030-01-01", answer_exists=exists)
        assert r.verdict == "needs_judge", exists


def test_c2_answer_exists_is_required_and_validated():
    import pytest
    with pytest.raises(TypeError):
        check_c2("Nao encontrei.", [ev({})], "2030-01-01")
    with pytest.raises(ValueError, match="answer_exists"):
        check_c2("Nao encontrei.", [ev({})], "2030-01-01", answer_exists="talvez")
