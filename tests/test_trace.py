from pathlib import Path

import pytest

from evals.trace import validate_trace, new_trace_id, write_trace, load_trace


def make_trace(**over) -> dict:
    base = {
        "trace_id": "c01-aaaa1111", "case_id": "c01", "status": "ok",
        "source": {"harness": "claude-code", "version": "x"},
        "model": "modelo-x",
        "conditions": {"skill": True, "hook": True, "server": "local",
                       "p2_tag": "step-16", "corpus_version": "abc"},
        "question": "pergunta?",
        "events": [{"tool": "buscar_dispositivos", "args": {"consulta": "x"},
                    "result_raw": {"encontrado": False}}],
        "final_answer": "nao encontrei",
        "usage": {"input_tokens": 1, "output_tokens": 2, "cost_usd": 0.0, "duration_ms": 10},
    }
    base.update(over)
    return base


def test_valid_trace_has_no_errors():
    assert validate_trace(make_trace()) == []


def test_missing_field_is_reported():
    t = make_trace(); del t["question"]
    assert any("question" in e for e in validate_trace(t))


def test_bad_status_and_server():
    assert validate_trace(make_trace(status="talvez"))
    t = make_trace(); t["conditions"]["server"] = "nuvem"
    assert validate_trace(t)


def test_ok_trace_requires_result_raw():
    t = make_trace(events=[{"tool": "obter_dispositivo", "args": {}, "result_raw": None}])
    assert any("result_raw" in e for e in validate_trace(t))


def test_interrupted_trace_may_lack_result_raw():
    t = make_trace(status="erro",
                   events=[{"tool": "obter_dispositivo", "args": {}, "result_raw": None}])
    assert validate_trace(t) == []


def test_new_trace_id_is_unique_and_prefixed():
    a, b = new_trace_id("c01"), new_trace_id("c01")
    assert a != b and a.startswith("c01-")


def test_write_trace_refuses_to_overwrite(tmp_path: Path):
    t = make_trace()
    p = write_trace(t, tmp_path)
    assert load_trace(p) == t
    with pytest.raises(FileExistsError):
        write_trace(t, tmp_path)


def test_write_trace_refuses_invalid(tmp_path: Path):
    t = make_trace(); del t["events"]
    with pytest.raises(ValueError):
        write_trace(t, tmp_path)
    assert list(tmp_path.iterdir()) == []
