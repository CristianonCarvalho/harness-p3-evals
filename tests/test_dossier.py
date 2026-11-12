"""Testes do dossie por trace. Nada aqui chama modelo ou rede; tudo fica em tmp_path."""
import json
import random
import re
from pathlib import Path

import pytest

from evals.dossier import (FORM_HELP, answer_dates, build_dossier, cited_provisions, citation_key,
                           main, returned_index)
from evals.privacy import find_taxpayer_ids, make_synthetic_cpf

SEARCH = "mcp__taxlaw__buscar_dispositivos"
GET = "mcp__taxlaw__obter_dispositivo"


def make_trace(**over) -> dict:
    base = {
        "trace_id": "c01-aaaa1111", "case_id": "c01", "status": "ok",
        "source": {"harness": "claude-code", "version": "x"},
        "model": "modelo-x",
        "conditions": {"skill": True, "hook": True, "server": "local",
                       "p2_tag": "step-16", "corpus_version": "abc"},
        "question": "Desde quando a CBS pode ser cobrada?",
        "events": [],
        "final_answer": "Resposta sem citacoes.",
        "usage": {"input_tokens": 1, "output_tokens": 2, "cost_usd": 0.0, "duration_ms": 10},
    }
    base.update(over)
    return base


def make_case(hypothesis=("H4",), disputed=False, **over) -> dict:
    base = {
        "case_id": "c01", "question": "Desde quando a CBS pode ser cobrada?",
        "hypothesis": list(hypothesis), "split": None, "subsets": [],
        "gabarito": {"answer_exists": "sim", "expected_provisions": ["ADCT.art126"],
                     "reference_date": "2027-01-01", "disputed": disputed},
    }
    base.update(over)
    return base


def efeitos(desde="2023-12-21", ate=None, fundamento="EC 132/2023, art. 23, III"):
    return {"desde": desde, "ate": ate, "fundamento": fundamento}


def snippet(citacao, id_, trecho="§ trecho da busca", **ef):
    return {"id": id_, "citacao": citacao, "trecho": trecho, "efeitos": efeitos(**ef)}


def search_event(resultados, data="2026-11-11"):
    return {"tool": SEARCH, "args": {"consulta": "x"},
            "result_raw": {"encontrado": True, "data_referencia": data,
                           "resultados": resultados}}


def not_found_event(motivo="nenhum dispositivo corresponde"):
    return {"tool": SEARCH, "args": {"consulta": "y"},
            "result_raw": {"encontrado": False, "motivo": motivo}}


def get_event(id_, citacao, texto, *, filhos=None, origem=None, data="2026-11-11",
              coletado="2026-11-06", **ef):
    return {"tool": GET, "args": {"id": id_},
            "result_raw": {"encontrado": True, "id": id_, "data_referencia": data,
                           "corpus": {"coletado_em": coletado}, "citacao": citacao,
                           "origem": origem, "texto": texto, "efeitos": efeitos(**ef),
                           "filhos": filhos or [], "truncado": False}}


def _block(text: str) -> list[str]:
    m = re.search(r"```anotacao\n(.*?)\n```", text, re.S)
    assert m, "bloco anotacao ausente"
    return m.group(1).split("\n")


def _row(text: str, cell: str) -> str:
    """Linha de tabela que comeca pela celula dada (com os delimitadores)."""
    linhas = [ln for ln in text.splitlines() if ln.startswith(f"| {cell} |")]
    assert linhas, f"linha da tabela ausente: {cell!r}"
    return linhas[0]


def _outside_form(text: str) -> str:
    # Fora do formulario: sem o bloco e sem a linha de ajuda, que so diz quais valores escrever.
    sem_bloco = re.sub(r"```anotacao.*?```", "", text, flags=re.S)
    assert sem_bloco.count(FORM_HELP) == 1
    return sem_bloco.replace(FORM_HELP, "")


VERDICT_WORDS = re.compile(r"\b(pass|fail|needs_judge|aprovado|reprovado)\b", re.IGNORECASE)


# --- citation_key e cited_provisions -------------------------------------------------

def test_norm_before_and_after_give_same_text_and_key():
    antes = cited_provisions("Veja LC 214/2025, art. 125, § 1º, I.")
    depois = cited_provisions("Veja art. 125, § 1º, I, da LC 214/2025.")
    assert antes[0]["text"] == depois[0]["text"] == "LC 214/2025, art. 125, § 1º, I"
    assert antes[0]["key"] == depois[0]["key"]
    assert antes[0]["has_norm"] is True and depois[0]["has_norm"] is True


def test_norm_after_with_and_without_comma_before_norm():
    assert cited_provisions("art. 23, III, da EC 132/2023")[0]["text"] == "EC 132/2023, art. 23, III"
    assert cited_provisions("art. 23, III da EC 132/2023")[0]["text"] == "EC 132/2023, art. 23, III"


def test_paragraph_and_inciso_and_alinea_captured_before_norm():
    assert (cited_provisions("CF, art. 156-A, § 1º, XII, b")[0]["text"]
            == "CF, art. 156-A, § 1º, XII, b")


def test_ordinal_and_plain_article_have_same_key():
    assert citation_key("CF, art. 9º") == citation_key("CF, art. 9")


@pytest.mark.parametrize("entrada, chave", [
    ("Lei Complementar nº 214/2025, art. 142", "lc 214/2025, art. 142"),
    ("Lei Complementar 214/2025, art. 142", "lc 214/2025, art. 142"),
    ("LC nº 214/2025, art. 142", "lc 214/2025, art. 142"),
    ("LC 214, art. 142", "lc 214/2025, art. 142"),
    ("Emenda Constitucional 132/2023, art. 2º", "ec 132/2023, art. 2"),
    ("Emenda Constitucional nº 132, art. 2º", "ec 132/2023, art. 2"),
    ("EC 132, art. 2", "ec 132/2023, art. 2"),
    ("Constituição Federal, art. 156-A, § 1º", "cf, art. 156-a, § 1"),
    ("Constituição, art. 5º", "cf, art. 5"),
    ("CF, art. 5º", "cf, art. 5"),
    ("ADCT, art. 130", "adct, art. 130"),
])
def test_norm_name_variants_map_to_canonical_keys(entrada, chave):
    assert citation_key(entrada) == chave


def test_same_provision_with_and_without_norm_is_listed_once_with_norm():
    itens = cited_provisions("O art. 142 trata disso. Veja LC 214/2025, art. 142.")
    assert len(itens) == 1
    assert itens[0]["text"] == "LC 214/2025, art. 142"
    assert itens[0]["has_norm"] is True


def test_bare_article_has_no_norm():
    assert cited_provisions("O art. 142 trata disso.") == [
        {"text": "art. 142", "key": "art. 142", "has_norm": False}]


def test_citations_in_order_of_first_appearance():
    itens = cited_provisions("Veja art. 9º da EC 132/2023 e depois LC 214/2025, art. 125.")
    assert [i["text"] for i in itens] == ["EC 132/2023, art. 9º", "LC 214/2025, art. 125"]


def test_corpus_id_in_answer_is_a_citation_with_norm():
    itens = cited_provisions("Conforme LC214.art125, o regime muda. Vale também CF.art156-A.par4.")
    assert [i["text"] for i in itens] == ["LC 214/2025, art. 125", "CF, art. 156-A, § 4º"]
    assert all(i["has_norm"] for i in itens)


def test_paragrafo_unico_is_kept_in_text():
    assert (cited_provisions("LC 214/2025, art. 124, parágrafo único")[0]["text"]
            == "LC 214/2025, art. 124, parágrafo único")


# --- returned_index -------------------------------------------------------------------

def test_calls_are_numbered_and_children_indexed():
    events = [
        search_event([snippet("CF, art. 156-A, § 4º", "CF.art156-A.par4")]),
        get_event("ADCT.art130", "ADCT, art. 130", "Art. 130. texto completo",
                  filhos=[{"id": "ADCT.art130.incI", "citacao": "ADCT, art. 130, I",
                           "texto": "I - texto do inciso"}]),
        search_event([snippet("ADCT, art. 130", "ADCT.art130")]),
    ]
    idx = returned_index(events)
    prov = idx["provisions"]
    assert prov[citation_key("ADCT, art. 130")]["calls"] == [2, 3]
    assert prov[citation_key("CF, art. 156-A, § 4º")]["calls"] == [1]
    filho = prov[citation_key("ADCT, art. 130, I")]
    assert filho["calls"] == [2] and filho["full"] is True
    assert filho["texto"] == "I - texto do inciso"


def test_snippet_is_not_full_and_obter_text_wins():
    events = [
        search_event([snippet("ADCT, art. 130", "ADCT.art130", trecho="só o começo")]),
        get_event("ADCT.art130", "ADCT, art. 130", "Art. 130. texto completo"),
    ]
    p = returned_index(events)["provisions"][citation_key("ADCT, art. 130")]
    assert p["full"] is True
    assert p["texto"] == "Art. 130. texto completo"
    assert p["calls"] == [1, 2]


def test_foundations_exclude_citations_that_are_provisions():
    events = [
        get_event("ADCT.art130", "ADCT, art. 130", "Art. 130. texto",
                  origem="EC 132/2023, art. 2º", fundamento="EC 132/2023, art. 23, III"),
        search_event([snippet("EC 132/2023, art. 23, III", "EC132.art23.incIII")]),
    ]
    idx = returned_index(events)
    assert idx["foundations"][citation_key("EC 132/2023, art. 2º")]["of"] == ["ADCT, art. 130"]
    assert citation_key("EC 132/2023, art. 23, III") not in idx["foundations"]
    assert citation_key("ADCT, art. 130") not in idx["foundations"]


def test_dates_list_has_the_four_kinds():
    events = [
        search_event([snippet("CF, art. 156-A, § 4º", "CF.art156-A.par4",
                              desde="2023-12-21", ate="2027-01-01")]),
        get_event("ADCT.art130", "ADCT, art. 130", "Art. 130. texto", desde="2023-12-21"),
    ]
    datas = returned_index(events)["dates"]
    assert ("2026-11-11", "data de referência das chamadas", "") in datas
    assert ("2023-12-21", "efeitos desde", "CF, art. 156-A, § 4º") in datas
    assert ("2027-01-01", "efeitos até", "CF, art. 156-A, § 4º") in datas
    assert ("2026-11-06", "coleta do corpus", "") in datas
    assert {k for _, k, _ in datas} == {
        "efeitos desde", "efeitos até", "data de referência das chamadas", "coleta do corpus"}


# --- answer_dates ---------------------------------------------------------------------

def test_answer_dates_iso_br_extenso_and_drops_impossible():
    texto = ("Vale de 2027-01-01 e de 15/03/2027. Também 1º de janeiro de 2027 "
             "e 1 de Janeiro de 2027. Não: 31/02/2027 nem 2027-02-31.")
    assert answer_dates(texto) == ["2027-01-01", "2027-03-15"]


# --- build_dossier: modos e validacoes --------------------------------------------------

def test_invalid_mode_raises():
    with pytest.raises(ValueError):
        build_dossier(make_trace(), make_case(), mode="talvez")


def test_blind_mode_refuses_draft():
    with pytest.raises(ValueError):
        build_dossier(make_trace(), make_case(), mode="cega", draft={"C1": "x"})
    with pytest.raises(ValueError):
        build_dossier(make_trace(), make_case(), mode="cega", draft_path="/x.json")


def test_revised_mode_requires_draft_and_path():
    with pytest.raises(ValueError):
        build_dossier(make_trace(), make_case(), mode="revisada")
    with pytest.raises(ValueError):
        build_dossier(make_trace(), make_case(), mode="revisada", draft={"C1": "x"})


def test_case_id_mismatch_raises():
    with pytest.raises(ValueError):
        build_dossier(make_trace(case_id="c02"), make_case(), mode="cega")


def test_blind_dossier_has_no_verdict_words_outside_form():
    trace = make_trace(
        final_answer="Nao encontrei norma sobre isso.",
        events=[search_event([snippet("CF, art. 156-A, § 4º", "CF.art156-A.par4",
                                      trecho="§ 4º texto neutro")])])
    texto = build_dossier(trace, make_case(), mode="cega")
    assert VERDICT_WORDS.search(_outside_form(texto)) is None
    assert "RASCUNHO" not in texto and "## 6." not in texto


def test_revised_dossier_shows_draft_under_warning_and_fills_form():
    draft = {"C1": "pass", "C2": "fail", "C3": "pass", "C4": "n/a",
             "uncertain": ["C2"], "justificativa": "texto do rascunho aqui"}
    texto = build_dossier(make_trace(), make_case(), mode="revisada",
                          draft=draft, draft_path="/x/rascunho.json")
    assert texto.startswith("# Dossiê (revisada): `c01-aaaa1111`")
    assert "RASCUNHO da IA: confira, não confie" in texto
    assert "texto do rascunho aqui" in texto
    linhas = _block(texto)
    assert "kind: revised" in linhas
    assert "draft: /x/rascunho.json" in linhas


def test_synthetic_cpf_is_removed_from_answer_and_returned_text():
    cpf = make_synthetic_cpf(random.Random(7))
    trace = make_trace(
        final_answer=f"O contribuinte {cpf} tem direito ao regime.",
        events=[get_event("ADCT.art130", "ADCT, art. 130", f"Texto com {cpf} dentro.")])
    texto = build_dossier(trace, make_case(), mode="cega")
    assert cpf not in texto
    assert find_taxpayer_ids(texto) == []
    assert "[número removido]" in texto


def test_form_block_fields_in_blind_mode():
    linhas = _block(build_dossier(make_trace(), make_case(), mode="cega"))
    assert "trace_id: c01-aaaa1111" in linhas
    assert "kind: blind" in linhas
    assert "draft:" in linhas
    assert "C1:" in linhas and "C2:" in linhas and "C3:" in linhas
    assert "uncertain:" in linhas and "note:" in linhas
    assert linhas[-1] == "note:"


def test_c4_prefilled_n_a_without_security_hypothesis():
    linhas = _block(build_dossier(make_trace(), make_case(hypothesis=["H4"]), mode="cega"))
    assert "C4: n/a" in linhas


def test_c4_empty_with_security_hypothesis():
    texto = build_dossier(make_trace(), make_case(hypothesis=["H12"]), mode="cega")
    linhas = _block(texto)
    assert "C4:" in linhas
    assert "C4: n/a" not in linhas


# --- build_dossier: tabela de citacoes ---------------------------------------------------

def test_bare_citation_resolved_only_from_returned_norm():
    trace = make_trace(
        final_answer="A regra do art. 142 se aplica.",
        events=[search_event([snippet("LC 214/2025, art. 142", "LC214.art142")])])
    texto = build_dossier(trace, make_case(), mode="cega")
    assert _row(texto, "art. 142").count(
        "sim (sem a norma; resolvido pelo devolvido: LC 214/2025, art. 142)") == 1
    assert "CF, art. 142" not in texto


def test_bare_citation_with_two_candidates_lists_both():
    trace = make_trace(
        final_answer="Veja o art. 142.",
        events=[search_event([snippet("CF, art. 142", "CF.art142"),
                              snippet("LC 214/2025, art. 142", "LC214.art142")])])
    linha = _row(build_dossier(trace, make_case(), mode="cega"), "art. 142")
    assert "CF, art. 142" in linha and "LC 214/2025, art. 142" in linha


def test_citation_only_as_fundamento_has_no_text():
    trace = make_trace(
        final_answer="Isso vem da EC 132/2023, art. 23, III.",
        events=[get_event("ADCT.art130", "ADCT, art. 130", "Art. 130. texto",
                          fundamento="EC 132/2023, art. 23, III")])
    linha = _row(build_dossier(trace, make_case(), mode="cega"), "EC 132/2023, art. 23, III")
    assert "só como fundamento de efeitos/origem de: ADCT, art. 130" in linha
    assert "completo" not in linha and "só trecho" not in linha


def test_citation_not_returned_says_so():
    trace = make_trace(final_answer="Veja LC 214/2025, art. 999.",
                       events=[search_event([snippet("CF, art. 1", "CF.art1")])])
    linha = _row(build_dossier(trace, make_case(), mode="cega"), "LC 214/2025, art. 999")
    assert "não aparece no que foi devolvido" in linha


def test_snippet_only_then_full_when_fetched():
    so_busca = make_trace(
        final_answer="Veja CF, art. 156-A, § 4º.",
        events=[search_event([snippet("CF, art. 156-A, § 4º", "CF.art156-A.par4")])])
    linha = _row(build_dossier(so_busca, make_case(), mode="cega"), "CF, art. 156-A, § 4º")
    assert "só trecho da busca" in linha

    com_obter = make_trace(
        final_answer="Veja CF, art. 156-A, § 4º.",
        events=[search_event([snippet("CF, art. 156-A, § 4º", "CF.art156-A.par4")]),
                get_event("CF.art156-A.par4", "CF, art. 156-A, § 4º", "§ 4º texto completo")])
    linha = _row(build_dossier(com_obter, make_case(), mode="cega"), "CF, art. 156-A, § 4º")
    assert "completo" in linha and "só trecho" not in linha


def test_returned_but_not_cited_count_is_shown():
    trace = make_trace(
        final_answer="Nada de norma aqui.",
        events=[search_event([snippet("CF, art. 1", "CF.art1"),
                              snippet("CF, art. 2", "CF.art2")])])
    texto = build_dossier(trace, make_case(), mode="cega")
    assert re.search(r"Devolvidos e não citados na resposta: 2\.", texto)


# --- build_dossier: tabela de datas -----------------------------------------------------

def test_date_not_returned_anywhere():
    trace = make_trace(final_answer="Vigora desde 2031-05-05.",
                       events=[search_event([snippet("CF, art. 1", "CF.art1")])])
    linha = _row(build_dossier(trace, make_case(), mode="cega"), "2031-05-05")
    assert "não aparece no que foi devolvido" in linha


def test_date_matching_call_reference_and_corpus_collection():
    trace = make_trace(
        final_answer="Em 2026-11-11 e em 2026-11-06 o corpus foi lido.",
        events=[get_event("ADCT.art130", "ADCT, art. 130", "Art. 130. texto")])
    texto = build_dossier(trace, make_case(), mode="cega")
    assert "data de referência das chamadas" in _row(texto, "2026-11-11")
    assert "coleta do corpus" in _row(texto, "2026-11-06")


def test_date_shared_by_many_provisions_lists_cited_first():
    resultados = [snippet(f"CF, art. {n}", f"CF.art{n}", desde="2027-01-01")
                  for n in range(1, 5)]
    trace = make_trace(final_answer="Vale a partir de 2027-01-01, conforme CF, art. 3.",
                       events=[search_event(resultados)])
    linha = _row(build_dossier(trace, make_case(), mode="cega"), "2027-01-01")
    assert "e mais 3 dispositivos" in linha
    assert "CF, art. 3" in linha
    assert linha.index("CF, art. 3") < linha.index("e mais 3 dispositivos")


# --- apendice e CLI ----------------------------------------------------------------------

def test_appendix_lists_calls_snippets_and_not_found():
    trace = make_trace(events=[
        search_event([snippet("CF, art. 1", "CF.art1", trecho="trecho curto")]),
        not_found_event("sem resultado para a consulta"),
    ])
    texto = build_dossier(trace, make_case(), mode="cega")
    apendice = texto.split("## Apêndice", 1)[1]
    assert "### Chamada 1: `buscar_dispositivos(" in apendice
    assert "trecho curto" in apendice
    assert "### Chamada 2: `buscar_dispositivos(" in apendice
    assert "Nada encontrado. Motivo: sem resultado para a consulta" in apendice


def test_cli_prints_dossier_for_trace_found_recursively(tmp_path: Path, capsys):
    traces = tmp_path / "traces"
    (traces / "sub").mkdir(parents=True)
    cases = tmp_path / "cases"
    cases.mkdir()
    (traces / "sub" / "c01-aaaa1111.json").write_text(json.dumps(make_trace()), encoding="utf-8")
    (cases / "c01.json").write_text(json.dumps(make_case()), encoding="utf-8")
    code = main(["c01-aaaa1111", "--traces-dir", str(traces), "--cases-dir", str(cases)])
    assert code == 0
    assert "# Dossiê (cega): `c01-aaaa1111`" in capsys.readouterr().out


def test_cli_unknown_trace_fails_with_message(tmp_path: Path, capsys):
    traces = tmp_path / "traces"
    traces.mkdir()
    cases = tmp_path / "cases"
    cases.mkdir()
    code = main(["c99-zzzz9999", "--traces-dir", str(traces), "--cases-dir", str(cases)])
    assert code != 0
    assert "c99-zzzz9999" in capsys.readouterr().err


def test_cli_revisada_without_draft_fails(tmp_path: Path, capsys):
    traces = tmp_path / "traces"
    traces.mkdir()
    (traces / "c01-aaaa1111.json").write_text(json.dumps(make_trace()), encoding="utf-8")
    cases = tmp_path / "cases"
    cases.mkdir()
    (cases / "c01.json").write_text(json.dumps(make_case()), encoding="utf-8")
    code = main(["c01-aaaa1111", "--mode", "revisada",
                 "--traces-dir", str(traces), "--cases-dir", str(cases)])
    assert code == 1
    assert capsys.readouterr().err != ""


# --- defeitos achados ao rodar nos traces reais de confirmacao (2026-11-12) ---------

def test_conjunction_e_after_inciso_is_not_an_alinea():
    # Resposta real: "A CF, art. 156-A, § 1º, XII, e o ADCT, art. 130, dizem..."
    itens = cited_provisions("A CF, art. 156-A, § 1º, XII, e o ADCT, art. 130, dizem que sim.")
    assert [i["text"] for i in itens] == ["CF, art. 156-A, § 1º, XII", "ADCT, art. 130"]


def test_real_alinea_is_still_recognized():
    itens = cited_provisions("Ver CF, art. 105, I, j. E também art. 5, II, a, da CF.")
    textos = [i["text"] for i in itens]
    assert "CF, art. 105, I, j" in textos
    assert "CF, art. 5º, II, a" in textos


def test_open_ended_effects_do_not_say_ate_nao_informado():
    # efeitos_ate null no P2 quer dizer sem fim declarado, nao "nao informado".
    trace = make_trace(final_answer="Ver ADCT, art. 130.",
                       events=[search_event([snippet("ADCT, art. 130", "ADCT.art130")])])
    texto = build_dossier(trace, make_case(), mode="cega")
    linha = next(ln for ln in texto.splitlines() if ln.startswith("| ADCT, art. 130 |"))
    assert "desde 2023-12-21" in linha
    assert "não informado" not in linha
    assert "até" not in linha


def test_bare_citation_prefers_the_exact_article_over_its_paragraphs():
    # Resposta real: "o art. 156-A (§§ 1º a 13) produz efeitos..." com o caput e varios §§ devolvidos.
    filhos = [{"id": f"CF.art156-A.par{n}", "citacao": f"CF, art. 156-A, § {n}º", "texto": f"§ {n}º x"}
              for n in (1, 2, 3)]
    trace = make_trace(final_answer="O art. 156-A produz efeitos desde 2023-12-21.",
                       events=[get_event("CF.art156-A", "CF, art. 156-A", "Art. 156-A. Lei complementar.",
                                         filhos=filhos)])
    texto = build_dossier(trace, make_case(), mode="cega")
    linha = next(ln for ln in texto.splitlines() if ln.startswith("| art. 156-A |"))
    assert "resolvido pelo devolvido: CF, art. 156-A" in linha
    assert "ambíguo" not in linha


def test_bare_art_14_does_not_resolve_to_art_142():
    # O trace real que motivou a regra R8: a resposta citava "art. 14" e so o art. 142 foi devolvido.
    trace = make_trace(final_answer="Segundo o art. 14, a regra vale.",
                       events=[search_event([snippet("LC 214/2025, art. 142", "LC214.art142")])])
    texto = build_dossier(trace, make_case(), mode="cega")
    linha = _row(texto, "art. 14")
    assert "não aparece no que foi devolvido" in linha
    assert "art. 142" not in linha


def test_same_provision_twice_in_one_call_counts_the_call_once():
    ev = search_event([snippet("ADCT, art. 130", "ADCT.art130"),
                       snippet("ADCT, art. 130", "ADCT.art130", trecho="outro trecho")])
    idx = returned_index([ev])
    assert idx["provisions"][citation_key("ADCT, art. 130")]["calls"] == [1]
