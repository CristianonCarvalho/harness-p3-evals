"""Testes da linha de comando (evals/cli.py): so argumentos e chamadas, sem regra de negocio."""
from __future__ import annotations

import json
import random
from pathlib import Path

import pytest

from evals import cli
from evals.consistency import hash_prompts
from evals.privacy import make_synthetic_cpf


def _escreve(path: Path, dados) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    texto = dados if isinstance(dados, str) else json.dumps(dados, ensure_ascii=False)
    path.write_text(texto, encoding="utf-8")


def _caso(cid="c01", hip=("H1",), split=None, expected=("CF.art1",)):
    return {
        "case_id": cid,
        "question": "Qual e o prazo previsto no artigo?",
        "hypothesis": list(hip),
        "subsets": [],
        "split": split,
        "gabarito": {
            "answer_exists": "sim",
            "expected_provisions": list(expected),
            "reference_date": "2024-01-01",
            "disputed": False,
        },
    }


# check-repo e scan-privacy


def test_check_repo_sai_zero_em_repositorio_limpo(tmp_path, capsys):
    assert cli.main(["check-repo", "--root", str(tmp_path)]) == 0
    assert "aviso: " in capsys.readouterr().out


def test_check_repo_sai_um_com_problema_sem_mostrar_o_numero(tmp_path, capsys):
    cpf = make_synthetic_cpf(random.Random(3))
    _escreve(tmp_path / "docs" / "nota.md", cpf)
    assert cli.main(["check-repo", "--root", str(tmp_path)]) == 1
    erro = capsys.readouterr().err
    assert "problema: docs/nota.md" in erro
    assert cpf not in erro


def test_scan_privacy_sai_um_com_achado(tmp_path, capsys):
    cpf = make_synthetic_cpf(random.Random(4))
    _escreve(tmp_path / "docs" / "nota.md", cpf)
    assert cli.main(["scan-privacy", "--root", str(tmp_path)]) == 1
    assert "problema: docs/nota.md" in capsys.readouterr().err


def test_scan_privacy_sai_zero_sem_achado(tmp_path):
    assert cli.main(["scan-privacy", "--root", str(tmp_path)]) == 0


# hash-prompts


def test_hash_prompts_imprime_o_hash(tmp_path, capsys):
    pasta = tmp_path / "judge_prompts"
    _escreve(pasta / "juiz.md", "texto do juiz")
    assert cli.main(["hash-prompts", "--dir", str(pasta)]) == 0
    assert capsys.readouterr().out.strip() == hash_prompts(pasta)


def test_hash_prompts_sem_pasta_avisa_e_sai_zero(tmp_path, capsys):
    assert cli.main(["hash-prompts", "--dir", str(tmp_path / "nao-existe")]) == 0
    assert capsys.readouterr().out.strip() != ""


# apply-splits


def test_apply_splits_grava_divisao_e_semente(tmp_path):
    cases = tmp_path / "cases"
    for i, hip in enumerate(["H1", "H1", "H1", "H2", "H2"], 1):
        _escreve(cases / f"c{i:02d}.json", _caso(f"c{i:02d}", hip=(hip,)))
    assert cli.main(["apply-splits", "--seed", "7", "--cases-dir", str(cases)]) == 0
    assert json.loads((cases / "_split_meta.json").read_text(encoding="utf-8")) == {"seed": 7}
    for p in cases.glob("c*.json"):
        assert json.loads(p.read_text(encoding="utf-8"))["split"] in {"desenvolvimento", "teste"}


# verify-gabarito (caller do P2 simulado; o P2 real nunca roda aqui)


def test_verify_gabarito_ok_com_caller_simulado(tmp_path, monkeypatch):
    cases = tmp_path / "cases"
    _escreve(cases / "c01.json", _caso("c01", split="teste"))
    p2 = tmp_path / "p2"
    p2.mkdir()
    recebido = {}

    def fake_make_p2_caller(p2_dir):
        recebido["dir"] = p2_dir

        def call(name, args):
            return {"encontrado": True, "efeitos": [{"data": "2024-01-01"}]}
        return call

    monkeypatch.setattr(cli, "make_p2_caller", fake_make_p2_caller)
    assert cli.main(["verify-gabarito", "--p2-dir", str(p2), "--cases-dir", str(cases)]) == 0
    assert recebido["dir"] == p2


def test_verify_gabarito_falha_quando_dispositivo_nao_existe(tmp_path, monkeypatch, capsys):
    cases = tmp_path / "cases"
    _escreve(cases / "c01.json", _caso("c01", split="teste"))
    p2 = tmp_path / "p2"
    p2.mkdir()

    def fake_make_p2_caller(p2_dir):
        def call(name, args):
            return {"encontrado": False, "efeitos": []}
        return call

    monkeypatch.setattr(cli, "make_p2_caller", fake_make_p2_caller)
    assert cli.main(["verify-gabarito", "--p2-dir", str(p2), "--cases-dir", str(cases)]) == 1
    erro = capsys.readouterr().err
    assert "c01" in erro and "nao existe" in erro


def test_verify_gabarito_com_pasta_do_p2_inexistente_sai_um(tmp_path, capsys):
    cases = tmp_path / "cases"
    _escreve(cases / "c01.json", _caso("c01", split="teste"))
    assert cli.main(["verify-gabarito", "--p2-dir", str(tmp_path / "nao"),
                     "--cases-dir", str(cases)]) == 1


# subcomandos delegados e argumentos desconhecidos


def test_subcomando_delegado_repassa_os_argumentos(tmp_path, capsys):
    rc = cli.main(["dossier", "c01-00000000",
                   "--traces-dir", str(tmp_path / "traces"),
                   "--cases-dir", str(tmp_path / "cases")])
    assert rc != 0
    assert "trace não encontrado" in capsys.readouterr().err


def test_subcomando_desconhecido_e_erro_de_uso():
    with pytest.raises(SystemExit):
        cli.main(["nao-existe"])
