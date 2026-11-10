import json
from pathlib import Path

import pytest

from evals.gabarito import verify_case, make_p2_caller
from tests.test_cases import make_case


def fake_ok(name, args):
    return {"encontrado": True, "id": args["id"], "efeitos": {"desde": "2027-01-01"}}


def test_case_that_matches_passes():
    assert verify_case(make_case(), fake_ok) == []


def test_unknown_expected_id_is_reported():
    def fake(name, args):
        return {"encontrado": False, "id": args["id"]}
    erros = verify_case(make_case(), fake)
    assert erros and "ADCT.art126" in erros[0]


def test_found_without_efeitos_is_reported():
    def fake(name, args):
        return {"encontrado": True, "id": args["id"]}
    assert verify_case(make_case(), fake)


def test_answer_nao_makes_no_calls():
    chamadas = []
    c = make_case()
    c["gabarito"].update(answer_exists="nao", expected_provisions=[])
    verify_case(c, lambda n, a: chamadas.append(n) or {})
    assert chamadas == []


def test_make_p2_caller_builds_the_command_and_parses_json(tmp_path: Path):
    visto = {}

    class Done:
        returncode = 0
        stdout = json.dumps({"encontrado": True})
        stderr = ""

    def fake_run(cmd, cwd, capture_output, text, timeout):
        visto.update(cmd=cmd, cwd=cwd)
        return Done()

    out = make_p2_caller(tmp_path, run=fake_run)(
        "obter_dispositivo", {"id": "LC214.art125", "data_referencia": "2027-01-01"})
    assert out == {"encontrado": True}
    assert visto["cwd"] == tmp_path
    assert visto["cmd"][-3:] == ["LC214.art125", "--data", "2027-01-01"]


def test_not_found_is_reported_even_if_efeitos_are_present():
    # "encontrado: false" e o que decide; efeitos soltos nao salvam o caso.
    def fake(name, args):
        return {"encontrado": False, "efeitos": {"desde": "2027-01-01"}}
    erros = verify_case(make_case(), fake)
    assert erros and "nao existe" in erros[0]


def test_verify_case_asks_the_tool_with_the_right_arguments():
    chamadas = []

    def fake(name, args):
        chamadas.append((name, args))
        return fake_ok(name, args)

    verify_case(make_case(), fake)
    assert chamadas == [("obter_dispositivo", {
        "id": "ADCT.art126", "data_referencia": "2027-01-01", "incluir_filhos": False})]


def _done(returncode, stdout="{}"):
    class Done:
        pass
    d = Done()
    d.returncode, d.stdout, d.stderr = returncode, stdout, ""
    return d


def test_p2_caller_accepts_exit_1_but_fails_on_client_error(tmp_path: Path):
    # Codigo 1 = erro devolvido pelo server (o JSON ainda vem); 2 = erro do cliente.
    ok = make_p2_caller(tmp_path, run=lambda *a, **k: _done(1, '{"encontrado": false}'))
    assert ok("obter_dispositivo", {"id": "X", "data_referencia": "2027-01-01"}) == {"encontrado": False}
    ruim = make_p2_caller(tmp_path, run=lambda *a, **k: _done(2))
    with pytest.raises(RuntimeError):
        ruim("obter_dispositivo", {"id": "X", "data_referencia": "2027-01-01"})


def test_p2_caller_rejects_unsupported_tool(tmp_path: Path):
    with pytest.raises(ValueError):
        make_p2_caller(tmp_path, run=lambda *a, **k: _done(0))("buscar_dispositivos", {})


def test_p2_caller_uses_json_mode_and_a_timeout(tmp_path: Path):
    visto = {}

    def fake_run(cmd, cwd, capture_output, text, timeout):
        visto.update(cmd=cmd, timeout=timeout)
        return _done(0)

    make_p2_caller(tmp_path, run=fake_run)(
        "obter_dispositivo", {"id": "X", "data_referencia": "2027-01-01"})
    cmd = visto["cmd"]
    assert cmd[cmd.index("--json") + 1] == "obter"  # --json vem antes do subcomando
    assert visto["timeout"] and visto["timeout"] > 0  # teste que pode pendurar tem tempo maximo
