import hashlib
import json
import random
from pathlib import Path

import pytest

from evals.budget import BudgetExceeded, BudgetGuard
from evals.drafter import (
    DraftRejected,
    build_messages,
    check_quotes,
    draft_batch,
    draft_gabarito,
    format_corpus,
    load_corpus,
    main,
    parse_draft,
    write_draft,
)
from evals.ledger import Ledger
from evals.privacy import make_synthetic_cpf

REF = "2027-01-01"
MODEL = "deepseek/deepseek-v4.1-flash-1017"
PROMPT = "PROMPT DE TESTE"
QUESTION = "Desde quando a CBS pode ser cobrada?"

# Corpus sintetico: nenhum texto real do P2 aqui.
CORPUS = [
    {"id": "LC214.art125", "citacao": "Art. 125",
     "texto": "A CBS incide sobre operações com bens.",
     "efeitos_desde": "2027-01-01", "efeitos_ate": None},
    {"id": "ADCT.art126", "citacao": "Art. 126",
     "texto": "A CBS poderá ser cobrada a partir de 2026.",
     "efeitos_desde": "2026-01-01", "efeitos_ate": "2026-12-31"},
    {"id": "ADCT.art126", "citacao": "Art. 126",
     "texto": "A CBS passa a ser cobrada   a partir de\n2027.",
     "efeitos_desde": "2027-01-01", "efeitos_ate": None},
    {"id": "CF.art156-A", "citacao": "Art. 156-A",
     "texto": "Lei complementar instituirá imposto.",
     "efeitos_desde": "2023-12-22", "efeitos_ate": None},
]


def make_case(cid="c01", **over) -> dict:
    base = {
        "case_id": cid,
        "question": QUESTION,
        "hypothesis": ["H4"],
        "split": None,
        "subsets": [],
        "gabarito": {
            "answer_exists": "sim",
            "expected_provisions": ["LC214.art125"],
            "reference_date": REF,
            "disputed": False,
        },
    }
    base.update(over)
    return base


def rascunho(**over) -> dict:
    d = {
        "answer_exists": "sim",
        "expected_provisions": ["LC214.art125"],
        "reference_date": REF,
        "quotes": [{"id": "LC214.art125", "text": "A CBS incide sobre operações com bens."}],
        "justification": "A CBS incide sobre operações com bens, conforme o art. 125.",
    }
    d.update(over)
    return d


class FakeClient:
    """Cliente falso: devolve os textos em ordem; o ultimo se repete."""

    def __init__(self, *textos: str) -> None:
        self.textos = list(textos)
        self.chamadas: list[dict] = []

    def chat(self, messages, model):
        self.chamadas.append({"messages": messages, "model": model})
        if len(self.textos) > 1:
            texto = self.textos.pop(0)
        else:
            texto = self.textos[0]
        return {
            "choices": [{"message": {"content": texto}, "finish_reason": "stop"}],
            "usage": {"cost": 0.001, "prompt_tokens": 10, "completion_tokens": 5},
        }


def ok_tool(name, args):
    return {"encontrado": True, "id": args["id"], "efeitos": {"desde": "2027-01-01"}}


def kw(tmp_path: Path, client, call_tool=ok_tool, limit=10.0, guard=None) -> dict:
    return dict(
        client=client,
        model=MODEL,
        guard=guard or BudgetGuard(limit),
        ledger=Ledger(tmp_path / "ledger.jsonl"),
        traces_dir=tmp_path / "traces",
        call_tool=call_tool,
        prompt=PROMPT,
        reference_date=REF,
        corpus_version="abc123def456",
    )


# --- corpus e mensagens -------------------------------------------------------

def test_load_corpus_returns_the_dispositivos_list(tmp_path: Path):
    p = tmp_path / "dispositivos.json"
    p.write_text(json.dumps({"dispositivos": CORPUS}, ensure_ascii=False), encoding="utf-8")
    assert load_corpus(p) == CORPUS


def test_format_corpus_has_one_line_per_entry_in_order_including_repeated_ids():
    # o texto com espacos repetidos e quebra de linha quebra o split; comparamos por entrada
    esperado = [
        "LC214.art125 | Art. 125 | efeitos 2027-01-01.. | A CBS incide sobre operações com bens.",
        "ADCT.art126 | Art. 126 | efeitos 2026-01-01..2026-12-31 | A CBS poderá ser cobrada a partir de 2026.",
        "ADCT.art126 | Art. 126 | efeitos 2027-01-01.. | A CBS passa a ser cobrada   a partir de\n2027.",
        "CF.art156-A | Art. 156-A | efeitos 2023-12-22.. | Lei complementar instituirá imposto.",
    ]
    assert format_corpus(CORPUS) == "\n".join(esperado)


def test_build_messages_has_prompt_question_date_and_whole_corpus():
    msgs = build_messages(make_case(), CORPUS, reference_date=REF, prompt=PROMPT)
    assert [m["role"] for m in msgs] == ["system", "user"]
    assert msgs[0]["content"] == PROMPT
    user = msgs[1]["content"]
    assert QUESTION in user
    assert f"Data de referencia: {REF}" in user
    assert format_corpus(CORPUS) in user
    # as duas versoes do mesmo id aparecem
    assert user.count("ADCT.art126 |") == 2


def test_build_messages_receives_only_the_question_from_the_case():
    marcador = "MARCADOR_GABARITO_INTERNO_42"
    caso = make_case(gabarito={"answer_exists": "sim", "expected_provisions": [],
                               "reference_date": REF, "disputed": False,
                               "nota": marcador})
    msgs = build_messages(caso, CORPUS, reference_date=REF, prompt=PROMPT)
    assert marcador not in json.dumps(msgs, ensure_ascii=False)


# --- parse_draft --------------------------------------------------------------

def test_parse_draft_accepts_plain_json():
    assert parse_draft(json.dumps(rascunho())) == rascunho()


def test_parse_draft_accepts_json_inside_json_fence():
    texto = "```json\n" + json.dumps(rascunho(), ensure_ascii=False) + "\n```"
    assert parse_draft(texto) == rascunho()


@pytest.mark.parametrize("texto", [
    "Não consigo responder com o corpus.",
    '{"answer_exists": "sim",',
    '["sim", "nao"]',
    json.dumps({k: v for k, v in rascunho().items() if k != "quotes"}),
    json.dumps(rascunho(answer_exists=1)),
    json.dumps(rascunho(quotes=["A CBS incide"])),
])
def test_parse_draft_rejects_bad_responses(texto):
    with pytest.raises(DraftRejected) as exc:
        parse_draft(texto)
    assert exc.value.reasons


# --- check_quotes -------------------------------------------------------------

def test_check_quotes_unknown_id_is_an_error():
    d = rascunho(expected_provisions=["XX.art1"],
                 quotes=[{"id": "XX.art1", "text": "A CBS incide"}])
    assert any("XX.art1" in e for e in check_quotes(d, CORPUS))


def test_check_quotes_changed_word_is_an_error():
    d = rascunho(quotes=[{"id": "LC214.art125", "text": "A CBS incide sobre operações com serviços."}])
    assert check_quotes(d, CORPUS)


def test_check_quotes_whitespace_difference_is_accepted():
    d = rascunho(expected_provisions=["ADCT.art126"],
                 quotes=[{"id": "ADCT.art126", "text": "A CBS passa a ser cobrada a partir de 2027."}])
    assert check_quotes(d, CORPUS) == []


def test_check_quotes_matches_the_other_version_of_a_repeated_id():
    d = rascunho(expected_provisions=["ADCT.art126"],
                 quotes=[{"id": "ADCT.art126", "text": "A CBS poderá ser cobrada a partir de 2026."}])
    assert check_quotes(d, CORPUS) == []


def test_check_quotes_expected_id_without_quote_is_an_error():
    d = rascunho(expected_provisions=["LC214.art125", "CF.art156-A"])
    assert any("CF.art156-A" in e for e in check_quotes(d, CORPUS))


def test_check_quotes_empty_text_is_an_error():
    d = rascunho(quotes=[{"id": "LC214.art125", "text": "   "}])
    assert check_quotes(d, CORPUS)


# --- draft_gabarito e draft_batch ----------------------------------------------

def test_valid_draft_is_returned_and_written(tmp_path: Path):
    client = FakeClient(json.dumps(rascunho()))
    res = draft_batch([make_case()], CORPUS, drafts_dir=tmp_path / "drafts", **kw(tmp_path, client))
    caminho = tmp_path / "drafts" / "cases" / "c01.v1.json"
    assert res["written"] == [caminho]
    assert res["rejected"] == []
    conteudo = json.loads(caminho.read_text(encoding="utf-8"))
    assert conteudo["case_id"] == "c01"
    assert conteudo["model"] == MODEL
    assert conteudo["answer_exists"] == "sim"
    assert conteudo["expected_provisions"] == ["LC214.art125"]
    assert conteudo["reference_date"] == REF
    assert conteudo["quotes"] == rascunho()["quotes"]
    assert conteudo["justification"] == rascunho()["justification"]
    assert conteudo["disputed"] is False


def test_nao_draft_is_accepted_and_p2_is_never_consulted(tmp_path: Path):
    client = FakeClient(json.dumps(rascunho(answer_exists="nao", expected_provisions=[], quotes=[])))
    visto = []

    def registra(name, args):
        visto.append(args)
        return ok_tool(name, args)

    rec = draft_gabarito(make_case(), CORPUS, **kw(tmp_path, client, call_tool=registra))
    assert rec["answer_exists"] == "nao"
    assert rec["expected_provisions"] == []
    assert visto == []


def test_existing_trace_blocks_before_any_model_call(tmp_path: Path):
    (tmp_path / "traces" / "sub").mkdir(parents=True)
    (tmp_path / "traces" / "sub" / "c01-abcd1234.json").write_text("{}", encoding="utf-8")
    client = FakeClient(json.dumps(rascunho()))
    with pytest.raises(DraftRejected):
        draft_gabarito(make_case("c01"), CORPUS, **kw(tmp_path, client))
    assert client.chamadas == []


@pytest.mark.parametrize("trace_name, case_id", [
    ("c010-abcd1234.json", "c01"),
    ("c10-aaaa1111.json", "c1"),
    ("xc01-abcd1234.json", "c01"),  # o id do caso contido no fim do nome de outro caso
])
def test_trace_of_a_longer_case_id_does_not_block(tmp_path: Path, trace_name, case_id):
    (tmp_path / "traces").mkdir()
    (tmp_path / "traces" / trace_name).write_text("{}", encoding="utf-8")
    client = FakeClient(json.dumps(rascunho()))
    rec = draft_gabarito(make_case(case_id), CORPUS, **kw(tmp_path, client))
    assert rec["case_id"] == case_id
    assert len(client.chamadas) == 1


def test_expected_id_unknown_to_p2_is_rejected_and_named(tmp_path: Path):
    def nao_existe(name, args):
        return {"encontrado": False, "id": args["id"]}
    client = FakeClient(json.dumps(rascunho()))
    with pytest.raises(DraftRejected) as exc:
        draft_gabarito(make_case(), CORPUS, **kw(tmp_path, client, call_tool=nao_existe))
    assert "LC214.art125" in str(exc.value)


def test_quote_with_one_word_changed_is_rejected(tmp_path: Path):
    client = FakeClient(json.dumps(rascunho(
        quotes=[{"id": "LC214.art125", "text": "A CBS incide sobre operações com serviços."}])))
    with pytest.raises(DraftRejected):
        draft_gabarito(make_case(), CORPUS, **kw(tmp_path, client))


def test_quote_with_only_different_whitespace_is_accepted(tmp_path: Path):
    client = FakeClient(json.dumps(rascunho(
        expected_provisions=["ADCT.art126"],
        quotes=[{"id": "ADCT.art126", "text": "A CBS passa a ser cobrada\n a partir de 2027."}])))
    rec = draft_gabarito(make_case(), CORPUS, **kw(tmp_path, client))
    assert rec["expected_provisions"] == ["ADCT.art126"]


def test_expected_id_without_quote_is_rejected(tmp_path: Path):
    client = FakeClient(json.dumps(rascunho(expected_provisions=["LC214.art125", "CF.art156-A"])))
    with pytest.raises(DraftRejected):
        draft_gabarito(make_case(), CORPUS, **kw(tmp_path, client))


@pytest.mark.parametrize("texto", [
    "Sem JSON aqui.",
    '{"answer_exists": "sim", "expected_provisions": [',
    json.dumps({k: v for k, v in rascunho().items() if k != "quotes"}),
])
def test_bad_model_response_is_rejected(tmp_path: Path, texto):
    client = FakeClient(texto)
    with pytest.raises(DraftRejected):
        draft_gabarito(make_case(), CORPUS, **kw(tmp_path, client))


def test_json_inside_fence_is_accepted(tmp_path: Path):
    client = FakeClient("```json\n" + json.dumps(rascunho()) + "\n```")
    rec = draft_gabarito(make_case(), CORPUS, **kw(tmp_path, client))
    assert rec["answer_exists"] == "sim"


def test_reference_date_different_from_argument_is_rejected(tmp_path: Path):
    client = FakeClient(json.dumps(rascunho(reference_date="2026-06-01")))
    with pytest.raises(DraftRejected):
        draft_gabarito(make_case(), CORPUS, **kw(tmp_path, client))


def test_answer_exists_talvez_is_rejected_by_validate_case(tmp_path: Path):
    client = FakeClient(json.dumps(rascunho(answer_exists="talvez")))
    with pytest.raises(DraftRejected):
        draft_gabarito(make_case(), CORPUS, **kw(tmp_path, client))


def test_all_problems_are_collected_in_one_rejection(tmp_path: Path):
    client = FakeClient(json.dumps(rascunho(
        reference_date="2026-06-01",
        quotes=[{"id": "LC214.art125", "text": "A CBS incide sobre operações com serviços."}])))
    with pytest.raises(DraftRejected) as exc:
        draft_gabarito(make_case(), CORPUS, **kw(tmp_path, client))
    assert len(exc.value.reasons) >= 2


def test_p2_is_not_consulted_when_offline_checks_fail(tmp_path: Path):
    visto = []

    def registra(name, args):
        visto.append(args)
        return ok_tool(name, args)

    client = FakeClient(json.dumps(rascunho(
        quotes=[{"id": "LC214.art125", "text": "texto inventado"}])))
    with pytest.raises(DraftRejected):
        draft_gabarito(make_case(), CORPUS, **kw(tmp_path, client, call_tool=registra))
    assert visto == []


def test_justification_with_synthetic_cpf_is_not_written_in_digits(tmp_path: Path):
    cpf = make_synthetic_cpf(random.Random(1))
    client = FakeClient(json.dumps(rascunho(justification=f"O contribuinte {cpf} declarou a CBS.")))
    res = draft_batch([make_case()], CORPUS, drafts_dir=tmp_path / "drafts", **kw(tmp_path, client))
    texto = res["written"][0].read_text(encoding="utf-8")
    assert cpf not in texto
    assert "[número removido]" in texto


def test_draft_records_corpus_version_and_prompt_hash(tmp_path: Path):
    # Sem isso, um gabarito nao diz contra qual corpus e qual prompt foi rascunhado.
    client = FakeClient(json.dumps(rascunho()))
    rec = draft_gabarito(make_case(), CORPUS, **kw(tmp_path, client))
    assert rec["corpus_version"] == "abc123def456"
    assert rec["prompt_sha"] == hashlib.sha256(PROMPT.encode("utf-8")).hexdigest()[:12]


def test_budget_exceeded_in_batch_lists_files_already_written(tmp_path: Path):
    client = FakeClient(json.dumps(rascunho()))
    with pytest.raises(BudgetExceeded) as exc:
        draft_batch([make_case("c01"), make_case("c02")], CORPUS,
                    drafts_dir=tmp_path / "drafts",
                    **kw(tmp_path, client, guard=BudgetGuard(0.0015)))
    notas = "\n".join(getattr(exc.value, "__notes__", []))
    assert "c01.v1.json" in notas


def test_draft_gabarito_does_not_write_anything(tmp_path: Path):
    client = FakeClient(json.dumps(rascunho()))
    rec = draft_gabarito(make_case(), CORPUS, **kw(tmp_path, client))
    assert rec["disputed"] is False
    assert not (tmp_path / "drafts").exists()


# --- write_draft --------------------------------------------------------------

def test_second_write_gets_v2_and_v1_is_unchanged(tmp_path: Path):
    drafts = tmp_path / "drafts"
    d1 = {"case_id": "c01", "x": 1}
    p1 = write_draft(d1, drafts)
    antes = p1.read_bytes()
    p2 = write_draft({"case_id": "c01", "x": 2}, drafts)
    assert p1.name == "c01.v1.json"
    assert p2.name == "c01.v2.json"
    assert p1.read_bytes() == antes


def test_version_number_is_numeric_not_alphabetic(tmp_path: Path):
    cases = tmp_path / "drafts" / "cases"
    cases.mkdir(parents=True)
    for n in range(1, 11):
        (cases / f"c01.v{n}.json").write_text("{}", encoding="utf-8")
    p = write_draft({"case_id": "c01"}, tmp_path / "drafts")
    assert p.name == "c01.v11.json"


def test_version_after_a_gap_is_one_more_than_the_largest(tmp_path: Path):
    # v1 e v3 (a v2 foi apagada a mao): a proxima e a v4, nunca a v3 de novo.
    cases = tmp_path / "drafts" / "cases"
    cases.mkdir(parents=True)
    for n in (1, 3):
        (cases / f"c01.v{n}.json").write_text("{}", encoding="utf-8")
    p = write_draft({"case_id": "c01"}, tmp_path / "drafts")
    assert p.name == "c01.v4.json"


def test_quote_with_a_document_number_is_redacted_when_written(tmp_path: Path):
    # Defesa em profundidade: o corpus e lei publica e nao traz CPF, mas se trouxesse,
    # o trecho literal nao poderia levar o numero ao arquivo versionado.
    cpf = make_synthetic_cpf(random.Random(2))
    corpus = CORPUS + [{"id": "LC214.art200", "citacao": "Art. 200",
                        "texto": f"Exemplo com o numero {cpf} no texto.",
                        "efeitos_desde": "2027-01-01", "efeitos_ate": None}]
    client = FakeClient(json.dumps(rascunho(
        quotes=rascunho()["quotes"] + [{"id": "LC214.art200", "text": f"numero {cpf} no"}])))
    res = draft_batch([make_case()], corpus, drafts_dir=tmp_path / "drafts", **kw(tmp_path, client))
    assert cpf not in res["written"][0].read_text(encoding="utf-8")


def test_write_draft_does_not_mutate_its_input(tmp_path: Path):
    d = {"case_id": "c01", "quotes": [{"id": "A", "text": "b"}]}
    copia = json.loads(json.dumps(d))
    write_draft(d, tmp_path / "drafts")
    assert d == copia


# --- draft_batch: orcamento e rejeicao -------------------------------------------

def test_budget_stops_batch_and_keeps_files_already_written(tmp_path: Path):
    client = FakeClient(json.dumps(rascunho()))
    # cada chamada custa 0.001; o teto de 0.0015 e atingido na 2a chamada
    guard = BudgetGuard(0.0015)
    with pytest.raises(BudgetExceeded):
        draft_batch([make_case("c01"), make_case("c02"), make_case("c03")], CORPUS,
                    drafts_dir=tmp_path / "drafts",
                    **kw(tmp_path, client, guard=guard))
    arquivos = sorted(p.name for p in (tmp_path / "drafts" / "cases").iterdir())
    assert arquivos == ["c01.v1.json"]
    assert len(client.chamadas) == 2


def test_rejected_case_in_the_middle_does_not_stop_the_batch(tmp_path: Path):
    client = FakeClient(json.dumps(rascunho()), "não é json", json.dumps(rascunho()))
    res = draft_batch([make_case("c01"), make_case("c02"), make_case("c03")], CORPUS,
                      drafts_dir=tmp_path / "drafts", **kw(tmp_path, client))
    assert [p.name for p in res["written"]] == ["c01.v1.json", "c03.v1.json"]
    assert len(res["rejected"]) == 1
    assert res["rejected"][0]["case_id"] == "c02"
    assert res["rejected"][0]["reasons"]


def test_ledger_has_one_line_per_model_call(tmp_path: Path):
    client = FakeClient(json.dumps(rascunho()), "não é json", json.dumps(rascunho()))
    draft_batch([make_case("c01"), make_case("c02"), make_case("c03")], CORPUS,
                drafts_dir=tmp_path / "drafts", **kw(tmp_path, client))
    linhas = (tmp_path / "ledger.jsonl").read_text(encoding="utf-8").splitlines()
    assert len(linhas) == 3
    assert all(json.loads(l)["t"] == "llm" for l in linhas)


# --- main ---------------------------------------------------------------------

def test_main_without_api_key_refuses_without_crashing(tmp_path: Path, monkeypatch, capsys):
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    caso = tmp_path / "caso.json"
    caso.write_text(json.dumps(make_case(), ensure_ascii=False), encoding="utf-8")
    codigo = main([str(caso), "--reference-date", REF, "--model", MODEL,
                   "--p2-dir", str(tmp_path), "--budget-usd", "0.05",
                   "--drafts-dir", str(tmp_path / "drafts")])
    saida = capsys.readouterr()
    assert codigo != 0
    assert "OPENROUTER_API_KEY" in saida.out + saida.err
