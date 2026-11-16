import json

import pytest

from pipeline.check_budget import check, main, read_result


def _escrever(tmp_path, conteudo):
    caminho = tmp_path / "execucao.json"
    caminho.write_text(json.dumps(conteudo), encoding="utf-8")
    return str(caminho)


def test_dentro_do_teto():
    assert check({"total_cost_usd": 0.5, "num_turns": 4}, 1.0, 10) == []


def test_custo_acima_do_teto():
    assert check({"total_cost_usd": 1.5, "num_turns": 4}, 1.0, 10)


def test_turnos_acima_do_teto():
    assert check({"total_cost_usd": 0.1, "num_turns": 11}, 1.0, 10)


def test_custo_ausente_falha_fechado():
    assert check({"num_turns": 4}, 1.0, 10)


def test_turnos_ausentes_falha_fechado():
    assert check({"total_cost_usd": 0.1}, 1.0, 10)


@pytest.mark.parametrize(
    "custo",
    [float("nan"), float("inf"), -0.5, "0.5", True, None, [0.5]],
)
def test_custo_invalido_falha_fechado(custo):
    # NaN > teto dá falso: sem validar o tipo, NaN passaria como "dentro do teto".
    assert check({"total_cost_usd": custo, "num_turns": 4}, 1.0, 10)


@pytest.mark.parametrize("turnos", [float("nan"), -1, "4", True, 4.5, None])
def test_turnos_invalidos_falham_fechado(turnos):
    assert check({"total_cost_usd": 0.1, "num_turns": turnos}, 1.0, 10)


def test_read_result_pega_a_ultima_mensagem_de_resultado(tmp_path):
    caminho = _escrever(
        tmp_path,
        [
            {"type": "assistant"},
            {"type": "result", "total_cost_usd": 0.2, "num_turns": 3},
        ],
    )
    assert read_result(caminho)["total_cost_usd"] == 0.2


def test_read_result_sem_mensagem_de_resultado(tmp_path):
    caminho = _escrever(tmp_path, [{"type": "assistant"}])
    with pytest.raises(ValueError):
        read_result(caminho)


def test_main_json_invalido_reprova(tmp_path):
    ruim = tmp_path / "ruim.json"
    ruim.write_text("{não é json", encoding="utf-8")
    assert main([str(ruim), "--max-cost", "1", "--max-turns", "10"]) == 1


def test_main_arquivo_inexistente_reprova(tmp_path):
    assert main([str(tmp_path / "nao-existe.json"), "--max-cost", "1", "--max-turns", "10"]) == 1


def test_main_ok(tmp_path):
    caminho = _escrever(tmp_path, [{"type": "result", "total_cost_usd": 0.1, "num_turns": 2}])
    assert main([caminho, "--max-cost", "1", "--max-turns", "10"]) == 0


def test_main_custo_nan_reprova(tmp_path):
    # json.dumps escreve NaN como literal; json.loads o aceita de volta.
    caminho = _escrever(tmp_path, [{"type": "result", "total_cost_usd": float("nan"), "num_turns": 2}])
    assert main([caminho, "--max-cost", "1", "--max-turns", "10"]) == 1
