import json
import random
import re
from pathlib import Path
import pytest

from evals.annotation import (
    validate_annotation,
    write_annotation,
    load_annotation,
    load_history,
)
from evals.privacy import make_synthetic_cpf, make_synthetic_cnpj


def make_case(cid="c01", **over) -> dict:
    base = {
        "case_id": cid,
        "question": "Desde quando a CBS pode ser cobrada?",
        "hypothesis": ["H4"],
        "split": None,
        "subsets": [],
        "gabarito": {
            "answer_exists": "sim",
            "expected_provisions": ["ADCT.art126"],
            "reference_date": "2027-01-01",
            "disputed": False,
        },
    }
    base.update(over)
    return base


def make_trace(**over) -> dict:
    base = {
        "trace_id": "c01-aaaa1111",
        "case_id": "c01",
        "status": "ok",
        "source": {"harness": "claude-code", "version": "x"},
        "model": "modelo-x",
        "conditions": {
            "skill": True,
            "hook": True,
            "server": "local",
            "p2_tag": "step-16",
            "corpus_version": "abc",
        },
        "question": "pergunta?",
        "events": [
            {
                "tool": "buscar_dispositivos",
                "args": {"consulta": "x"},
                "result_raw": {"encontrado": False},
            }
        ],
        "final_answer": "nao encontrei",
        "usage": {
            "input_tokens": 1,
            "output_tokens": 2,
            "cost_usd": 0.0,
            "duration_ms": 10,
        },
    }
    base.update(over)
    return base


def make_annotation(**over) -> dict:
    base = {
        "trace_id": "c01-aaaa1111",
        "verdicts": {"C1": "pass", "C2": "pass", "C3": "pass", "C4": "n/a"},
        "note": "",
        "uncertain": [],
        "kind": "blind",
        "draft": None,
    }
    base.update(over)
    return base


def _make_doc(tipo: str) -> tuple[str, str]:
    rng = random.Random(1)
    if tipo == "cpf_colado":
        doc = make_synthetic_cpf(rng)
        return doc, doc
    if tipo == "cpf_pontuado":
        raw = make_synthetic_cpf(rng)
        formatted = f"{raw[:3]}.{raw[3:6]}.{raw[6:9]}-{raw[9:]}"
        return formatted, raw
    if tipo == "cnpj_colado":
        doc = make_synthetic_cnpj(rng)
        return doc, doc
    if tipo == "cnpj_pontuado":
        raw = make_synthetic_cnpj(rng)
        formatted = f"{raw[:2]}.{raw[2:5]}.{raw[5:8]}/{raw[8:12]}-{raw[12:]}"
        return formatted, raw
    raise ValueError(tipo)


# 1. Anotação cega correta
def test_valid_blind_annotation_has_no_errors():
    case = make_case()
    trace = make_trace()
    ann = make_annotation()
    assert validate_annotation(ann, case, trace) == []


# 2. Revisada com draft correto
def test_valid_revised_annotation_with_draft_has_no_errors():
    case = make_case()
    trace = make_trace()
    ann = make_annotation(kind="revised", draft=f"drafts/annotations/{trace['trace_id']}.json")
    assert validate_annotation(ann, case, trace) == []


# 3. Nota com ID de dispositivo (não é documento)
def test_note_with_legal_provision_id_is_not_flagged_as_document():
    case = make_case()
    trace = make_trace()
    ann = make_annotation(note="faltou citar LC214.art125 no parecer")
    assert validate_annotation(ann, case, trace) == []


# 4. Combinação: trace_id diferente
def test_mismatched_trace_id_is_rejected():
    case = make_case()
    trace = make_trace(trace_id="c01-aaaa1111")
    ann = make_annotation(trace_id="c01-bbbb2222")
    errors = validate_annotation(ann, case, trace)
    assert len(errors) >= 1
    assert any(ann["trace_id"] in e and "trace_id" in e for e in errors)


# 5. Combinação: case_id diferente
def test_mismatched_case_id_is_rejected():
    case = make_case(cid="c09")
    trace = make_trace(case_id="c02")
    ann = make_annotation()
    errors = validate_annotation(ann, case, trace)
    assert errors
    msg = next((e for e in errors if "case_id" in e), None)
    assert msg is not None
    assert ann["trace_id"] in msg
    assert "c09" in msg and "c02" in msg


# 6. Combinação: trace com status diferente de ok
@pytest.mark.parametrize("status", ["erro", "estourou_limite"])
def test_failed_trace_cannot_be_annotated(status):
    case = make_case()
    trace = make_trace(status=status)
    ann = make_annotation()
    errors = validate_annotation(ann, case, trace)
    assert errors
    msg = next((e for e in errors if "status" in e), None)
    assert msg is not None
    assert ann["trace_id"] in msg
    assert f"'{status}'" in msg


# 7. Forma: falta o trace_id
def test_missing_trace_id_is_reported_as_missing():
    case = make_case()
    trace = make_trace()
    ann = make_annotation()
    del ann["trace_id"]
    errors = validate_annotation(ann, case, trace)
    assert errors
    msg = next((e for e in errors if "trace_id" in e and "ausente" in e), None)
    assert msg is not None
    assert trace["trace_id"] in msg
    assert not any("difere" in e for e in errors)


# 8. Forma: critérios desconhecidos ou ausentes
def test_unknown_criterion_is_rejected():
    case = make_case()
    trace = make_trace()
    ann = make_annotation(
        verdicts={"C1": "pass", "C2": "pass", "C3": "pass", "C4": "n/a", "C5": "pass"}
    )
    errors = validate_annotation(ann, case, trace)
    assert errors
    msg = next((e for e in errors if "C5" in e and "desconhecido" in e), None)
    assert msg is not None
    assert ann["trace_id"] in msg


def test_missing_criterion_is_rejected():
    case = make_case()
    trace = make_trace()
    ann = make_annotation()
    del ann["verdicts"]["C3"]
    errors = validate_annotation(ann, case, trace)
    assert errors
    msg = next((e for e in errors if "C3" in e and "ausente" in e), None)
    assert msg is not None
    assert ann["trace_id"] in msg


def test_unknown_and_missing_criteria_are_both_reported():
    case = make_case()
    trace = make_trace()
    ann = make_annotation(
        verdicts={"C1": "pass", "C2": "pass", "C4": "n/a", "C5": "pass"}
    )
    errors = validate_annotation(ann, case, trace)
    assert any("C5" in e and "desconhecido" in e for e in errors)
    assert any("C3" in e and "ausente" in e for e in errors)


# 9. Forma: veredito inválido
@pytest.mark.parametrize("bad", ["aprovado", "sim", True, "Pass"])
def test_invalid_verdict_value_is_rejected(bad):
    case = make_case()
    trace = make_trace()
    ann = make_annotation()
    ann["verdicts"]["C1"] = bad
    errors = validate_annotation(ann, case, trace)
    assert errors
    msg = next((e for e in errors if "C1" in e and "inválido" in e), None)
    assert msg is not None
    assert ann["trace_id"] in msg
    assert repr(bad) in msg


def test_invalid_verdict_value_rejected_on_c3():
    case = make_case()
    trace = make_trace()
    ann = make_annotation()
    ann["verdicts"]["C3"] = "sim"
    errors = validate_annotation(ann, case, trace)
    assert any("C3" in e and "inválido" in e and "'sim'" in e for e in errors)


# 10. Forma: kind ausente ou com outro valor
def test_missing_kind_is_reported_as_missing():
    case = make_case()
    trace = make_trace()
    ann = make_annotation()
    del ann["kind"]
    errors = validate_annotation(ann, case, trace)
    assert errors
    msg = next((e for e in errors if "kind" in e and "ausente" in e), None)
    assert msg is not None
    assert trace["trace_id"] in msg
    assert not any("inválido" in e for e in errors)


@pytest.mark.parametrize("bad", ["cega", "Blind", None])
def test_invalid_kind_is_rejected(bad):
    case = make_case()
    trace = make_trace()
    ann = make_annotation(kind=bad)
    errors = validate_annotation(ann, case, trace)
    assert errors
    msg = next((e for e in errors if "kind" in e and "inválido" in e), None)
    assert msg is not None
    assert ann["trace_id"] in msg
    assert repr(bad) in msg


# 11. Aplicabilidade: n/a em C1, C2 ou C3
@pytest.mark.parametrize("crit", ["C1", "C2", "C3"])
def test_na_on_always_applicable_criterion_is_rejected(crit):
    case = make_case()
    trace = make_trace()
    ann = make_annotation()
    ann["verdicts"][crit] = "n/a"
    errors = validate_annotation(ann, case, trace)
    assert errors
    msg = next((e for e in errors if crit in e and "sempre se aplica" in e), None)
    assert msg is not None
    assert ann["trace_id"] in msg
    assert not any("inválido" in e for e in errors)


# 12 & 13. Aplicabilidade: C4 e hipóteses de segurança
@pytest.mark.parametrize("val", ["pass", "fail"])
def test_c4_verdict_when_not_applicable_is_rejected(val):
    case = make_case()  # H4, sem H12/H13
    trace = make_trace()
    ann = make_annotation()
    ann["verdicts"]["C4"] = val
    errors = validate_annotation(ann, case, trace)
    assert errors
    msg = next((e for e in errors if "C4" in e and "não se aplica" in e), None)
    assert msg is not None
    assert ann["trace_id"] in msg
    assert repr(val) in msg


@pytest.mark.parametrize("hyp", [["H12"], ["H13"], ["H4", "H12"]])
def test_c4_na_when_applicable_is_rejected(hyp):
    case = make_case(hypothesis=hyp)
    trace = make_trace()
    ann = make_annotation()  # C4 padrão é "n/a"
    errors = validate_annotation(ann, case, trace)
    assert errors
    msg = next(
        (e for e in errors if "C4" in e and "n/a" in e and "não se aplica" not in e),
        None,
    )
    assert msg is not None
    assert ann["trace_id"] in msg
    sec_hyp = next(h for h in ("H12", "H13") if h in hyp)
    assert sec_hyp in msg


@pytest.mark.parametrize("hyp", [["H12"], ["H13"]])
def test_c4_verdict_when_applicable_is_accepted(hyp):
    case = make_case(hypothesis=hyp)
    trace = make_trace()
    ann = make_annotation(
        verdicts={"C1": "pass", "C2": "pass", "C3": "pass", "C4": "pass"}
    )
    assert validate_annotation(ann, case, trace) == []


# 14. Nota e uncertain: fail sem nota
@pytest.mark.parametrize("empty", ["", "   ", "\n"])
def test_fail_without_note_is_rejected(empty):
    case = make_case()
    trace = make_trace()
    ann = make_annotation(note=empty)
    ann["verdicts"]["C1"] = "fail"
    errors = validate_annotation(ann, case, trace)
    assert errors
    msg = next((e for e in errors if "nota" in e and "C1" in e), None)
    assert msg is not None
    assert ann["trace_id"] in msg


def test_fail_with_note_is_accepted():
    case = make_case()
    trace = make_trace()
    ann = make_annotation(note="citou LC214.art14 sem lastro")
    ann["verdicts"]["C1"] = "fail"
    assert validate_annotation(ann, case, trace) == []


def test_multiple_fails_without_note_lists_all_failing_criteria():
    case = make_case()
    trace = make_trace()
    ann = make_annotation(note="")
    ann["verdicts"]["C1"] = "fail"
    ann["verdicts"]["C3"] = "fail"
    errors = validate_annotation(ann, case, trace)
    assert errors
    msg = next((e for e in errors if "nota" in e and "C1" in e and "C3" in e), None)
    assert msg is not None
    assert ann["trace_id"] in msg


# 15. uncertain com critério n/a
def test_uncertain_on_na_criterion_is_rejected():
    case = make_case()  # C4 é n/a
    trace = make_trace()
    ann = make_annotation(uncertain=["C4"], note="dúvida sobre a segurança")
    errors = validate_annotation(ann, case, trace)
    assert errors
    msg = next((e for e in errors if "uncertain" in e and "C4" in e), None)
    assert msg is not None
    assert ann["trace_id"] in msg


def test_uncertain_on_valid_criterion_with_note_is_accepted():
    case = make_case()
    trace = make_trace()
    ann = make_annotation(uncertain=["C1"], note="fiquei em dúvida se o art. 14 bastava")
    assert validate_annotation(ann, case, trace) == []


# 16. uncertain sem nota
@pytest.mark.parametrize("empty", ["", "   ", "\n"])
def test_uncertain_without_note_is_rejected(empty):
    case = make_case()
    trace = make_trace()
    ann = make_annotation(uncertain=["C1"], note=empty)
    errors = validate_annotation(ann, case, trace)
    assert errors
    msg = next((e for e in errors if "uncertain" in e and "nota" in e and "C1" in e), None)
    assert msg is not None
    assert ann["trace_id"] in msg


# 17. uncertain com critério desconhecido ou tipo incorreto
@pytest.mark.parametrize("bad", ["C5", "c1", 1])
def test_uncertain_with_unknown_criterion_is_rejected(bad):
    case = make_case()
    trace = make_trace()
    ann = make_annotation(uncertain=[bad], note="dúvida explicada")
    errors = validate_annotation(ann, case, trace)
    assert errors
    msg = next((e for e in errors if "uncertain" in e and "desconhecido" in e), None)
    assert msg is not None
    assert ann["trace_id"] in msg
    assert repr(bad) in msg


def test_uncertain_not_a_list_is_rejected():
    case = make_case()
    trace = make_trace()
    ann = make_annotation(uncertain="C1", note="dúvida explicada")
    errors = validate_annotation(ann, case, trace)
    assert errors
    msg = next((e for e in errors if "uncertain" in e and "lista" in e), None)
    assert msg is not None
    assert ann["trace_id"] in msg


def test_uncertain_with_non_string_item_and_empty_note_does_not_crash():
    case = make_case()
    trace = make_trace()
    ann = make_annotation(uncertain=[1], note="")
    errors = validate_annotation(ann, case, trace)
    assert errors


# 18. Revisada sem draft
@pytest.mark.parametrize("del_draft", [False, True])
def test_revised_annotation_without_draft_is_rejected(del_draft):
    case = make_case()
    trace = make_trace()
    ann = make_annotation(kind="revised")
    if del_draft:
        del ann["draft"]
    errors = validate_annotation(ann, case, trace)
    assert errors
    msg = next((e for e in errors if "draft" in e and "revisada" in e), None)
    assert msg is not None
    assert ann["trace_id"] in msg


# 19. Cega com draft
def test_blind_annotation_with_draft_is_rejected():
    case = make_case()
    trace = make_trace()
    ann = make_annotation(draft=f"drafts/annotations/{trace['trace_id']}.json")
    errors = validate_annotation(ann, case, trace)
    assert errors
    msg = next((e for e in errors if "draft" in e and "cega" in e), None)
    assert msg is not None
    assert ann["trace_id"] in msg


# 20. draft com caminho inválido
@pytest.mark.parametrize(
    "template",
    [
        "/Users/x/drafts/annotations/{tid}.json",
        "drafts/annotations/../annotations/{tid}.json",
        "drafts/outra/{tid}.json",
        "annotations/{tid}.json",
        "drafts/annotationsX/{tid}.json",
        "drafts/annotations/outro-trace.json",
    ],
)
def test_invalid_draft_path_is_rejected(template):
    case = make_case()
    trace = make_trace()
    tid = trace["trace_id"]
    bad = template.format(tid=tid)
    ann = make_annotation(kind="revised", draft=bad)
    errors = validate_annotation(ann, case, trace)
    assert errors
    msg = next((e for e in errors if "draft" in e and "inválido" in e), None)
    assert msg is not None
    assert ann["trace_id"] in msg
    assert repr(bad) in msg


# 21 & 22. Privacidade: CPF e CNPJ na nota
@pytest.mark.parametrize(
    "tipo",
    ["cpf_colado", "cpf_pontuado", "cnpj_colado", "cnpj_pontuado"],
)
def test_taxpayer_id_in_note_is_rejected_without_leaking_number(tipo):
    doc_formatado, doc_raw = _make_doc(tipo)
    case = make_case()
    trace = make_trace()
    ann = make_annotation(note=f"o modelo repetiu o documento {doc_formatado} na resposta")
    errors = validate_annotation(ann, case, trace)
    assert errors
    msg = next((e for e in errors if "nota" in e and "documento" in e), None)
    assert msg is not None
    assert ann["trace_id"] in msg
    assert doc_formatado not in msg
    assert doc_raw not in msg


# 23. Toda mensagem traz o trace_id
def test_all_error_messages_start_with_trace_id():
    case = make_case()
    trace = make_trace()
    tid = trace["trace_id"]
    ann = make_annotation(
        verdicts={"C1": "n/a", "C2": "sim", "C3": "fail", "C4": "pass", "C5": "pass"},
        note="",
        uncertain=[1],
        kind="cega",
    )
    errors = validate_annotation(ann, case, trace)
    assert len(errors) >= 5
    assert all(e.startswith(f"{tid}: ") for e in errors)


# 29. write_annotation: anotação inválida não grava nada e não cria pasta
def test_write_annotation_refuses_invalid_and_creates_no_files_or_dir(tmp_path: Path):
    target_dir = tmp_path / "annotations"
    case = make_case()
    trace = make_trace()
    ann = make_annotation()
    ann["verdicts"]["C1"] = "n/a"  # C1 sempre se aplica
    with pytest.raises(ValueError) as exc:
        write_annotation(ann, case, trace, target_dir, date="2026-11-11")
    assert "C1" in str(exc.value)
    assert "sempre se aplica" in str(exc.value)
    assert not target_dir.exists()


# 24. Gravar duas vezes cria v1 e v2
def test_writing_twice_creates_two_versions(tmp_path: Path):
    target_dir = tmp_path / "annotations"
    case = make_case()
    trace = make_trace()
    ann1 = make_annotation(note="primeira anotação")
    p1 = write_annotation(ann1, case, trace, target_dir, date="2026-11-11")
    assert str(p1).endswith(f"{trace['trace_id']}.v1.json")
    assert "version" not in ann1
    v1_bytes = p1.read_bytes()

    ann2 = make_annotation(note="segunda anotação")
    p2 = write_annotation(ann2, case, trace, target_dir, date="2026-11-11")
    assert str(p2).endswith(f"{trace['trace_id']}.v2.json")
    assert "version" not in ann2
    assert p1.read_bytes() == v1_bytes

    latest = load_annotation(target_dir, trace["trace_id"])
    assert latest is not None
    assert latest["note"] == "segunda anotação"
    assert latest["version"] == 2


# 25. A versão 11 vem depois da 10 (ordem numérica)
def test_version_ordering_is_numeric_not_alphabetical(tmp_path: Path):
    target_dir = tmp_path / "annotations"
    case = make_case()
    trace = make_trace()
    tid = trace["trace_id"]
    for i in range(1, 11):
        write_annotation(make_annotation(note=f"versao {i}"), case, trace, target_dir, date="2026-11-11")
    latest = load_annotation(target_dir, tid)
    assert latest is not None
    assert latest["version"] == 10

    p11 = write_annotation(make_annotation(note="versao 11"), case, trace, target_dir, date="2026-11-11")
    assert str(p11).endswith(f"{tid}.v11.json")
    history = load_history(target_dir, tid)
    assert len(history) == 11
    assert [item["version"] for item in history] == list(range(1, 12))


# 26. Recusa version ou date pré-preenchidos
@pytest.mark.parametrize("bad_field,bad_val", [("version", 5), ("date", "2026-01-01")])
def test_prefilled_version_or_date_is_rejected(tmp_path: Path, bad_field, bad_val):
    target_dir = tmp_path / "annotations"
    case = make_case()
    trace = make_trace()
    ann = make_annotation(**{bad_field: bad_val})
    with pytest.raises(ValueError) as exc:
        write_annotation(ann, case, trace, target_dir, date="2026-11-11")
    assert bad_field in str(exc.value)
    assert not target_dir.exists()


# 27. Data fora do formato
@pytest.mark.parametrize(
    "bad_date",
    ["11/11/2026", "2026-13-01", "2026-02-30", "2026-1-1", "20261111"],
)
def test_invalid_date_format_is_rejected(tmp_path: Path, bad_date):
    target_dir = tmp_path / "annotations"
    case = make_case()
    trace = make_trace()
    ann = make_annotation()
    with pytest.raises(ValueError) as exc:
        write_annotation(ann, case, trace, target_dir, date=bad_date)
    assert "data inválida" in str(exc.value)
    assert not target_dir.exists()


# 28. O nome do arquivo e o JSON discordam / integridade na leitura
@pytest.mark.parametrize(
    "corrupt_field,corrupt_val",
    [
        ("version", 3),  # v2 com version: 3
        ("version", None),  # version ausente
        ("date", "2026-13-01"),  # data inválida
    ],
)
def test_load_history_rejects_corrupted_file(tmp_path: Path, corrupt_field, corrupt_val):
    target_dir = tmp_path / "annotations"
    case = make_case()
    trace = make_trace()
    tid = trace["trace_id"]
    write_annotation(make_annotation(note="v1"), case, trace, target_dir, date="2026-11-11")
    v2_path = target_dir / f"{tid}.v2.json"
    v2_data = {**make_annotation(note="v2"), "version": 2, "date": "2026-11-11"}
    if corrupt_val is None:
        del v2_data[corrupt_field]
    else:
        v2_data[corrupt_field] = corrupt_val
    v2_path.write_text(json.dumps(v2_data), encoding="utf-8")

    with pytest.raises(ValueError) as exc:
        load_history(target_dir, tid)
    assert v2_path.name in str(exc.value)


# Trace sem nenhuma anotação: histórico vazio [] e última anotação None
def test_load_history_and_annotation_on_empty_or_missing_trace(tmp_path: Path):
    target_dir = tmp_path / "annotations"
    assert load_history(target_dir, "nao-existe") == []
    assert load_annotation(target_dir, "nao-existe") is None


def test_load_history_rejects_duplicate_or_non_canonical_version(tmp_path: Path):
    target_dir = tmp_path / "annotations"
    case = make_case()
    trace = make_trace()
    tid = trace["trace_id"]
    write_annotation(make_annotation(note="v1"), case, trace, target_dir, date="2026-11-11")
    v01_path = target_dir / f"{tid}.v01.json"
    v01_data = {**make_annotation(note="v01"), "version": 1, "date": "2026-11-11"}
    v01_path.write_text(json.dumps(v01_data), encoding="utf-8")

    with pytest.raises(ValueError) as exc:
        load_history(target_dir, tid)
    assert v01_path.name in str(exc.value) or "duplicad" in str(exc.value)


def test_load_history_rejects_mismatched_internal_trace_id(tmp_path: Path):
    target_dir = tmp_path / "annotations"
    case = make_case()
    trace = make_trace()
    tid = trace["trace_id"]
    write_annotation(make_annotation(note="v1"), case, trace, target_dir, date="2026-11-11")
    v2_path = target_dir / f"{tid}.v2.json"
    v2_data = {**make_annotation(note="v2"), "trace_id": "c02-bbbb2222", "version": 2, "date": "2026-11-11"}
    v2_path.write_text(json.dumps(v2_data), encoding="utf-8")

    with pytest.raises(ValueError) as exc:
        load_history(target_dir, tid)
    assert v2_path.name in str(exc.value)
    assert "c02-bbbb2222" in str(exc.value)


def test_load_history_rejects_malformed_json_naming_file(tmp_path: Path):
    target_dir = tmp_path / "annotations"
    case = make_case()
    trace = make_trace()
    tid = trace["trace_id"]
    target_dir.mkdir(parents=True, exist_ok=True)
    broken_file = target_dir / f"{tid}.v1.json"
    broken_file.write_text("{este json nao fecha", encoding="utf-8")

    with pytest.raises(ValueError) as exc:
        load_history(target_dir, tid)
    assert broken_file.name in str(exc.value)



