"""Testes do rascunhador de anotações (evals/annotation_drafter.py). Nada aqui chama modelo ou rede; tudo fica em tmp_path."""
import hashlib
import json
import random
from pathlib import Path

import pytest

from evals.annotation import load_annotation, write_annotation
from evals.annotation_drafter import (
    blind_ids,
    draft_annotation,
    draft_annotations_batch,
    main,
    parse_annotation_draft,
    write_annotation_draft,
)
from evals.budget import BudgetExceeded, BudgetGuard
from evals.dossier import build_dossier
from evals.drafter import DraftRejected
from evals.ledger import Ledger
from evals.privacy import make_synthetic_cpf

MODEL = "deepseek/deepseek-v4.1-flash-1017"
PROMPT = "PROMPT DE TESTE DO ANOTADOR"
TID = "c01-aaaa1111"
TIDS = ["c01-aaaa1111", "c02-bbbb2222", "c03-cccc3333"]
DATA = "2026-11-12"
VERDICTOS_OK = {"C1": "pass", "C2": "pass", "C3": "pass", "C4": "n/a"}


def make_trace(trace_id=TID, case_id="c01", **over) -> dict:
    base = {
        "trace_id": trace_id, "case_id": case_id, "status": "ok",
        "source": {"harness": "claude-code", "version": "x"},
        "model": "modelo-x",
        "conditions": {"skill": True, "hook": True, "server": "local",
                       "p2_tag": "step-16", "corpus_version": "abc"},
        "question": "Desde quando a CBS pode ser cobrada?",
        "events": [],
        "final_answer": "Resposta sem citações.",
        "usage": {"input_tokens": 1, "output_tokens": 2, "cost_usd": 0.0, "duration_ms": 10},
    }
    base.update(over)
    return base


def make_case(case_id="c01", hypothesis=("H4",)) -> dict:
    return {
        "case_id": case_id, "question": "Desde quando a CBS pode ser cobrada?",
        "hypothesis": list(hypothesis), "split": "teste", "subsets": [],
        "gabarito": {"answer_exists": "sim", "expected_provisions": ["ADCT.art126"],
                     "reference_date": "2027-01-01", "disputed": False},
    }


def resposta(verdicts=None, uncertain=None, note="") -> str:
    """Texto JSON que o modelo devolveria no formato do prompt."""
    return json.dumps({
        "verdicts": dict(VERDICTOS_OK) if verdicts is None else verdicts,
        "uncertain": [] if uncertain is None else uncertain,
        "note": note,
    }, ensure_ascii=False)


class FakeClient:
    """Cliente falso: devolve os textos em ordem; o ultimo se repete. Grava as mensagens recebidas."""

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


def kw(tmp_path: Path, client, *, limit=10.0, guard=None, blind=()) -> dict:
    return dict(
        client=client,
        model=MODEL,
        guard=guard or BudgetGuard(limit),
        ledger=Ledger(tmp_path / "ledger.jsonl"),
        blind=set(blind),
        annotations_dir=tmp_path / "annotations",
        drafts_dir=tmp_path / "drafts",
        prompt=PROMPT,
    )


def grava_anotacao_cega(tmp_path: Path, trace: dict, case: dict, *, verdicts=None, note="") -> Path:
    ann = {
        "trace_id": trace["trace_id"],
        "verdicts": dict(VERDICTOS_OK) if verdicts is None else verdicts,
        "uncertain": [],
        "note": note,
        "kind": "blind",
        "draft": None,
    }
    return write_annotation(ann, case, trace, tmp_path / "annotations", date=DATA)


# --- blind_ids ----------------------------------------------------------------

def test_blind_ids_includes_blind_and_every_extension():
    samples = {
        "blind": {"seed": 1, "n": 2, "trace_ids": ["c01-aaaa1111", "c02-bbbb2222"]},
        "extensions": [
            {"seed": 2, "n_more": 1, "trace_ids_added": ["c03-cccc3333"]},
            {"seed": 3, "n_more": 2, "trace_ids_added": ["c04-dddd4444", "c05-eeee5555"]},
        ],
    }
    assert blind_ids(samples) == {"c01-aaaa1111", "c02-bbbb2222", "c03-cccc3333",
                                  "c04-dddd4444", "c05-eeee5555"}


def test_blind_ids_of_empty_samples_is_empty_set():
    assert blind_ids({}) == set()


# --- parse_annotation_draft ----------------------------------------------------

def test_parse_accepts_plain_json_and_returns_the_three_fields():
    texto = json.dumps({"verdicts": dict(VERDICTOS_OK), "uncertain": ["C2"], "note": "dúvida"})
    assert parse_annotation_draft(texto) == {
        "verdicts": dict(VERDICTOS_OK), "uncertain": ["C2"], "note": "dúvida"}


def test_parse_accepts_json_inside_json_fence():
    texto = "```json\n" + resposta() + "\n```"
    assert parse_annotation_draft(texto)["verdicts"] == VERDICTOS_OK


@pytest.mark.parametrize("texto", [
    "Não consigo anotar esta resposta.",
    '{"verdicts": {"C1": "pass",',
    '["pass", "fail"]',
    json.dumps({"uncertain": [], "note": ""}),
    json.dumps({"verdicts": ["pass"], "uncertain": [], "note": ""}),
    json.dumps({"verdicts": {"C1": 1}, "uncertain": [], "note": ""}),
    json.dumps({"verdicts": dict(VERDICTOS_OK), "note": ""}),
    json.dumps({"verdicts": dict(VERDICTOS_OK), "uncertain": "C2", "note": ""}),
    json.dumps({"verdicts": dict(VERDICTOS_OK), "uncertain": [], "note": None}),
    "```\n" + resposta() + "\n```",  # cerca sem a palavra json: fora do formato aceito
])
def test_parse_rejects_anything_else_with_reasons(texto):
    with pytest.raises(DraftRejected) as exc:
        parse_annotation_draft(texto)
    assert exc.value.reasons


# --- draft_annotation: recusas antes do modelo ----------------------------------

def test_blind_trace_without_recorded_annotation_is_refused_before_model_call(tmp_path: Path):
    client = FakeClient(resposta())
    trace, case = make_trace(), make_case()
    with pytest.raises(DraftRejected) as exc:
        draft_annotation(trace, case, **kw(tmp_path, client, blind=[TID]))
    assert "anotação cega" in str(exc.value)
    assert client.chamadas == []


def test_blind_trace_with_recorded_annotation_is_accepted(tmp_path: Path):
    trace, case = make_trace(), make_case()
    grava_anotacao_cega(tmp_path, trace, case)
    client = FakeClient(resposta())
    rec = draft_annotation(trace, case, **kw(tmp_path, client, blind=[TID]))
    assert rec["blind"] is True
    assert len(client.chamadas) == 1


def test_c4_pass_on_case_without_security_hypothesis_is_rejected(tmp_path: Path):
    client = FakeClient(resposta(verdicts={"C1": "pass", "C2": "pass", "C3": "pass", "C4": "pass"}))
    with pytest.raises(DraftRejected) as exc:
        draft_annotation(make_trace(), make_case(), **kw(tmp_path, client))
    assert any("C4" in r for r in exc.value.reasons)
    assert not (tmp_path / "drafts").exists()


def test_c4_na_on_case_with_security_hypothesis_is_rejected(tmp_path: Path):
    client = FakeClient(resposta())
    with pytest.raises(DraftRejected) as exc:
        draft_annotation(make_trace(), make_case(hypothesis=("H4", "H12")), **kw(tmp_path, client))
    assert any("C4" in r for r in exc.value.reasons)


def test_fail_with_empty_note_is_rejected_by_validator(tmp_path: Path):
    client = FakeClient(resposta(verdicts={"C1": "fail", "C2": "pass", "C3": "pass", "C4": "n/a"}, note=""))
    with pytest.raises(DraftRejected) as exc:
        draft_annotation(make_trace(), make_case(), **kw(tmp_path, client))
    assert any("nota" in r for r in exc.value.reasons)


def test_trace_with_status_erro_is_refused_before_model_call(tmp_path: Path):
    client = FakeClient(resposta())
    with pytest.raises(DraftRejected) as exc:
        draft_annotation(make_trace(status="erro"), make_case(), **kw(tmp_path, client))
    assert "status" in str(exc.value)
    assert client.chamadas == []


@pytest.mark.parametrize("status", ["estourou_limite"])
def test_other_non_ok_statuses_are_refused_too(tmp_path: Path, status):
    client = FakeClient(resposta())
    with pytest.raises(DraftRejected):
        draft_annotation(make_trace(status=status), make_case(), **kw(tmp_path, client))
    assert client.chamadas == []


# --- draft_annotation: registro devolvido e mensagens ---------------------------

def test_user_message_is_exactly_the_blind_dossier_and_has_no_annotation(tmp_path: Path):
    marcador = "NOTA_HUMANA_DISTINTIVA_731"
    trace, case = make_trace(), make_case()
    grava_anotacao_cega(tmp_path, trace, case, verdicts={"C1": "fail", "C2": "pass", "C3": "pass", "C4": "n/a"},
                        note=marcador)
    client = FakeClient(resposta())
    draft_annotation(trace, case, **kw(tmp_path, client, blind=[TID]))
    msgs = client.chamadas[0]["messages"]
    assert msgs[0] == {"role": "system", "content": PROMPT}
    assert msgs[1] == {"role": "user", "content": build_dossier(trace, case, mode="cega")}
    assert marcador not in json.dumps(msgs, ensure_ascii=False)


def test_draft_record_has_the_expected_fields_and_prompt_hash(tmp_path: Path):
    client = FakeClient(resposta(uncertain=["C2"], note="Dúvida sobre a data de efeitos."))
    rec = draft_annotation(make_trace(), make_case(), **kw(tmp_path, client))
    assert rec == {
        "trace_id": TID,
        "model": MODEL,
        "verdicts": dict(VERDICTOS_OK),
        "uncertain": ["C2"],
        "note": "Dúvida sobre a data de efeitos.",
        "prompt_sha": hashlib.sha256(PROMPT.encode("utf-8")).hexdigest()[:12],
        "blind": False,
    }
    assert not (tmp_path / "drafts").exists()


def test_note_with_synthetic_document_number_never_reaches_the_file(tmp_path: Path):
    cpf = make_synthetic_cpf(random.Random(9))
    formatado = f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"
    for n, numero in enumerate((cpf, formatado)):
        pasta = tmp_path / f"execucao{n}"
        client = FakeClient(resposta(verdicts={"C1": "fail", "C2": "pass", "C3": "pass", "C4": "n/a"},
                                     note=f"O documento {numero} aparece na resposta."))
        res = draft_annotations_batch([(make_trace(), make_case())], **kw(pasta, client))
        texto = res["written"][0].read_text(encoding="utf-8")
        assert cpf not in texto
        assert formatado not in texto
        assert "[número removido]" in texto


# --- draft_annotation: resposta do modelo ruim ----------------------------------

@pytest.mark.parametrize("texto", [
    "Sem JSON aqui.",
    '{"verdicts": {"C1": "pass",',
    json.dumps({"uncertain": [], "note": ""}),
    json.dumps({"verdicts": ["pass"], "uncertain": [], "note": ""}),
    "```\n" + resposta() + "\n```",
])
def test_bad_model_response_is_rejected_and_nothing_is_written(tmp_path: Path, texto):
    client = FakeClient(texto)
    with pytest.raises(DraftRejected) as exc:
        draft_annotation(make_trace(), make_case(), **kw(tmp_path, client))
    assert exc.value.reasons
    assert not (tmp_path / "drafts").exists()


def test_json_inside_fence_is_accepted(tmp_path: Path):
    client = FakeClient("```json\n" + resposta() + "\n```")
    rec = draft_annotation(make_trace(), make_case(), **kw(tmp_path, client))
    assert rec["verdicts"] == VERDICTOS_OK


# --- um rascunho por trace --------------------------------------------------------

def test_second_draft_for_the_same_trace_is_refused_before_model_call(tmp_path: Path):
    client = FakeClient(resposta())
    kwargs = kw(tmp_path, client)
    draft_annotations_batch([(make_trace(), make_case())], **kwargs)
    with pytest.raises(DraftRejected) as exc:
        draft_annotation(make_trace(), make_case(), **kwargs)
    assert "já existe" in str(exc.value)
    assert len(client.chamadas) == 1


def test_write_annotation_draft_never_overwrites_an_existing_file(tmp_path: Path):
    drafts = tmp_path / "drafts"
    rec = draft_annotation(make_trace(), make_case(), **kw(tmp_path, FakeClient(resposta())))
    caminho = write_annotation_draft(rec, drafts)
    antes = caminho.read_bytes()
    outro = dict(rec, note="outra nota")
    with pytest.raises(FileExistsError):
        write_annotation_draft(outro, drafts)
    assert caminho.read_bytes() == antes


def test_write_annotation_draft_does_not_mutate_its_input(tmp_path: Path):
    rec = {"trace_id": TID, "verdicts": dict(VERDICTOS_OK), "uncertain": [], "note": "ok",
           "model": MODEL, "prompt_sha": "abc", "blind": False}
    copia = json.loads(json.dumps(rec))
    write_annotation_draft(rec, tmp_path / "drafts")
    assert rec == copia


def test_write_annotation_draft_writes_non_ascii_text_as_is(tmp_path: Path):
    rec = {"trace_id": TID, "verdicts": dict(VERDICTOS_OK), "uncertain": [], "note": "não cita o art. 14",
           "model": MODEL, "prompt_sha": "abc", "blind": False}
    caminho = write_annotation_draft(rec, tmp_path / "drafts")
    assert caminho == tmp_path / "drafts" / "annotations" / f"{TID}.json"
    assert "não cita" in caminho.read_text(encoding="utf-8")


@pytest.mark.parametrize("trace_id", ["../fora", "a/b", ""])
def test_write_annotation_draft_refuses_unsafe_trace_ids(tmp_path: Path, trace_id):
    rec = {"trace_id": trace_id, "verdicts": dict(VERDICTOS_OK), "uncertain": [], "note": "",
           "model": MODEL, "prompt_sha": "abc", "blind": False}
    with pytest.raises(ValueError):
        write_annotation_draft(rec, tmp_path / "drafts")
    assert not any(tmp_path.rglob("*.json"))


# --- draft_annotations_batch ------------------------------------------------------------

def _itens(n: int = 3):
    return [(make_trace(tid, f"c0{i + 1}"), make_case(f"c0{i + 1}")) for i, tid in enumerate(TIDS[:n])]


def test_valid_draft_is_written_under_drafts_annotations(tmp_path: Path):
    client = FakeClient(resposta(uncertain=["C2"], note="Dúvida sobre a data de efeitos."))
    res = draft_annotations_batch(_itens(1), **kw(tmp_path, client))
    caminho = tmp_path / "drafts" / "annotations" / f"{TID}.json"
    assert res["written"] == [caminho]
    assert res["rejected"] == []
    gravado = json.loads(caminho.read_text(encoding="utf-8"))
    assert gravado["verdicts"] == VERDICTOS_OK
    assert gravado["uncertain"] == ["C2"]
    assert gravado["note"] == "Dúvida sobre a data de efeitos."
    assert gravado["blind"] is False
    assert gravado["prompt_sha"] == hashlib.sha256(PROMPT.encode("utf-8")).hexdigest()[:12]


def test_rejection_in_the_middle_does_not_stop_the_batch(tmp_path: Path):
    client = FakeClient(resposta(), "não é json", resposta())
    res = draft_annotations_batch(_itens(3), **kw(tmp_path, client))
    assert [p.name for p in res["written"]] == ["c01-aaaa1111.json", "c03-cccc3333.json"]
    assert len(res["rejected"]) == 1
    assert res["rejected"][0]["trace_id"] == "c02-bbbb2222"
    assert res["rejected"][0]["reasons"]


def test_status_erro_in_batch_is_rejected_and_batch_continues(tmp_path: Path):
    itens = _itens(2)
    itens[0] = (make_trace(TIDS[0], "c01", status="erro"), make_case("c01"))
    client = FakeClient(resposta())
    res = draft_annotations_batch(itens, **kw(tmp_path, client))
    assert [p.name for p in res["written"]] == ["c02-bbbb2222.json"]
    assert res["rejected"][0]["trace_id"] == TIDS[0]
    assert len(client.chamadas) == 1


def test_budget_exceeded_stops_batch_and_note_lists_files_written(tmp_path: Path):
    client = FakeClient(resposta())
    # cada chamada custa 0.001; o teto de 0.0015 e atingido na 2a chamada
    with pytest.raises(BudgetExceeded) as exc:
        draft_annotations_batch(_itens(3), **kw(tmp_path, client, guard=BudgetGuard(0.0015)))
    notas = "\n".join(getattr(exc.value, "__notes__", []))
    assert "c01-aaaa1111.json" in notas
    assert len(client.chamadas) == 2
    arquivos = sorted(p.name for p in (tmp_path / "drafts" / "annotations").iterdir())
    assert arquivos == ["c01-aaaa1111.json"]


def test_ledger_has_one_line_per_model_call(tmp_path: Path):
    client = FakeClient(resposta(), "não é json", resposta())
    draft_annotations_batch(_itens(3), **kw(tmp_path, client))
    linhas = (tmp_path / "ledger.jsonl").read_text(encoding="utf-8").splitlines()
    assert len(linhas) == 3
    assert all(json.loads(l)["t"] == "llm" for l in linhas)


# --- main -----------------------------------------------------------------------------

def test_main_without_api_key_refuses_with_exit_2(monkeypatch, capsys):
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    codigo = main([TID, "--model", MODEL, "--budget-usd", "0.05"])
    saida = capsys.readouterr()
    assert codigo == 2
    assert "OPENROUTER_API_KEY" in saida.out + saida.err
