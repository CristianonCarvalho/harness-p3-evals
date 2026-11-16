import json

import pytest

from pipeline.load_case import CASES_DIR, GATES_VALIDOS, load_case, main


@pytest.mark.parametrize(
    "ruim",
    ["", "../x", "01-bom; rm -rf /", "01-bom\n", "1-bom", "01_bom", "01-BOM", "01-", "ab-bom", "01-bom/../02-x"],
)
def test_rejeita_ids_malformados(ruim):
    with pytest.raises(ValueError):
        load_case(ruim)


def test_rejeita_caso_inexistente():
    with pytest.raises(ValueError):
        load_case("99-nao-existe")


def test_carrega_caso_valido(tmp_path):
    (tmp_path / "01-teste.json").write_text(
        json.dumps({"id": "01-teste", "title": "t", "prompt": "p", "expected": {"outcome": "passa", "gates": []}}),
        encoding="utf-8",
    )
    assert load_case("01-teste", tmp_path)["prompt"] == "p"


def test_rejeita_id_interno_diferente_do_arquivo(tmp_path):
    (tmp_path / "01-teste.json").write_text(
        json.dumps({"id": "02-outro", "title": "t", "prompt": "p", "expected": {}}), encoding="utf-8"
    )
    with pytest.raises(ValueError):
        load_case("01-teste", tmp_path)


def test_todos_os_casos_reais_sao_validos():
    ids = sorted(p.stem for p in CASES_DIR.glob("*.json"))
    assert len(ids) == 6
    casos = [load_case(i) for i in ids]
    assert sum(1 for c in casos if c["expected"]["outcome"] == "passa") == 1
    for c in casos:
        assert c["expected"]["outcome"] in ("passa", "barrado")
        assert set(c["expected"]["gates"]) <= GATES_VALIDOS
        if c["expected"]["outcome"] == "barrado":
            assert c["expected"]["gates"], f"{c['id']}: caso barrado precisa dizer qual gate"


def test_main_grava_no_arquivo_de_saida(tmp_path):
    saida = tmp_path / "out.txt"
    assert main(["01-bom", "--output", str(saida)]) == 0
    texto = saida.read_text(encoding="utf-8")
    assert texto.startswith("prompt<<EOF_")
    assert "README.md" in texto


def test_main_id_invalido_retorna_1():
    assert main(["../x"]) == 1
