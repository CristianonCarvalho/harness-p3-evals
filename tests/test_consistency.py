"""Checagens de consistencia do repositorio (evals/consistency.py).

Cada teste monta um repositorio sintetico em tmp_path. Nenhum CPF/CNPJ e escrito
literalmente: os numeros vem de make_synthetic_cpf, em tempo de execucao.
"""
from __future__ import annotations

import json
import random
from pathlib import Path

import pytest

from evals.consistency import check_repo, hash_prompts, scan_privacy
from evals.privacy import make_synthetic_cpf

TID = "c01-0a1b2c3d"
TID2 = "c02-1a2b3c4d"
VEREDITOS_OK = {"C1": "pass", "C2": "pass", "C3": "pass", "C4": "n/a"}
HEADER = {
    "p2_tag": "v1.2.0",
    "models": ["modelo-b", "modelo-a"],
    "judge": {"model": "juiz-x"},
    "judge_prompts_sha256": "abc123",
}


def _escreve(path: Path, dados) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    texto = dados if isinstance(dados, str) else json.dumps(dados, ensure_ascii=False)
    path.write_text(texto, encoding="utf-8")


def _caso(cid="c01", hipoteses=("H1",), split="teste"):
    return {
        "case_id": cid,
        "question": "Qual e o prazo previsto no artigo?",
        "hypothesis": list(hipoteses),
        "subsets": [],
        "split": split,
        "gabarito": {
            "answer_exists": "sim",
            "expected_provisions": ["CF.art1"],
            "reference_date": "2024-01-01",
            "disputed": False,
        },
    }


def _caso_no_repo(root: Path, cid="c01", split="teste") -> None:
    _escreve(root / "cases" / f"{cid}.json", _caso(cid, split=split))
    _escreve(root / "cases" / "_split_meta.json", {"seed": 1})


def _anotacao(tid=TID, *, kind="blind", version=1, verdicts=None, note="", draft=None):
    ann = {
        "trace_id": tid,
        "verdicts": dict(VEREDITOS_OK if verdicts is None else verdicts),
        "note": note,
        "uncertain": [],
        "kind": kind,
        "version": version,
        "date": "2026-01-10",
    }
    if kind == "revised":
        ann["draft"] = draft or f"drafts/annotations/{tid}.json"
    return ann


def _grava_anotacao(root: Path, ann: dict) -> None:
    _escreve(root / "annotations" / f"{ann['trace_id']}.v{ann['version']}.json", ann)


def _juiz_zerado() -> dict:
    return {"tpr": None, "tnr": None, "n_pos": 0, "n_neg": 0, "calibrated": False}


def _relatorio(root: Path, nome: str, judge: dict, header: dict | None = None) -> None:
    _escreve(root / "reports" / f"{nome}.json", {"header": header or {}, "judge": judge})


def _repo_para_recontagem(root: Path, tpr_reportado: float = 1.0) -> None:
    _escreve(root / "cases" / "c01.json", _caso("c01"))
    _escreve(root / "cases" / "c02.json", _caso("c02"))
    _escreve(root / "cases" / "_split_meta.json", {"seed": 1})
    _grava_anotacao(root, _anotacao(TID))
    _grava_anotacao(root, _anotacao(
        TID2, verdicts={"C1": "pass", "C2": "fail", "C3": "pass", "C4": "n/a"},
        note="Prazo errado no dispositivo."))
    _escreve(root / "annotations" / "_samples.json",
             {"blind": {"seed": 1, "n": 2, "trace_ids": [TID, TID2]}})
    _escreve(root / "judgments" / f"{TID}.json", {"trace_id": TID, "verdicts": {"C2": "pass"}})
    _escreve(root / "judgments" / f"{TID2}.json", {"trace_id": TID2, "verdicts": {"C2": "fail"}})
    _relatorio(root, "2026-01-15", {
        "C1": _juiz_zerado(),
        "C2": {"tpr": tpr_reportado, "tnr": 1.0, "n_pos": 1, "n_neg": 1, "calibrated": False},
        "C3": _juiz_zerado(),
        "C4": _juiz_zerado(),
    })


# 1. Repositorio vazio


def test_repositorio_vazio_nao_tem_problemas(tmp_path):
    resultado = check_repo(tmp_path)
    assert resultado.problems == []
    assert any("config/run.json" in w for w in resultado.warnings)


# 2. Privacidade


def test_cpf_em_md_vira_problema_sem_repetir_o_numero(tmp_path):
    cpf = make_synthetic_cpf(random.Random(1))
    _escreve(tmp_path / "docs" / "nota.md", f"Contribuinte {cpf}.")
    problemas = scan_privacy(tmp_path)
    assert len(problemas) == 1
    assert "docs/nota.md" in problemas[0]
    assert "1 número(s) com formato de CPF/CNPJ" in problemas[0]
    assert cpf not in problemas[0]


def test_cpf_em_pastas_ignoradas_e_uv_lock_nao_conta(tmp_path):
    cpf = make_synthetic_cpf(random.Random(2))
    for rel in ("traces/x.json", ".venv/lib/a.py", "uv.lock", "runs/y.md", ".superpowers/z.md"):
        _escreve(tmp_path / rel, f'"{cpf}"')
    assert scan_privacy(tmp_path) == []


# 3. Casos


def test_caso_sem_split_e_problema(tmp_path):
    _escreve(tmp_path / "cases" / "c01.json", _caso(split=None))
    _escreve(tmp_path / "cases" / "_split_meta.json", {"seed": 1})
    problemas = check_repo(tmp_path).problems
    assert any("cases/c01.json" in p and "split" in p for p in problemas)


def test_caso_sem_split_meta_e_problema(tmp_path):
    _escreve(tmp_path / "cases" / "c01.json", _caso())
    problemas = check_repo(tmp_path).problems
    assert any("_split_meta.json" in p for p in problemas)


def test_split_meta_sem_seed_e_problema(tmp_path):
    _escreve(tmp_path / "cases" / "c01.json", _caso())
    _escreve(tmp_path / "cases" / "_split_meta.json", {"outra_coisa": 1})
    problemas = check_repo(tmp_path).problems
    assert any("_split_meta.json" in p and "seed" in p for p in problemas)


def test_caso_invalido_e_problema(tmp_path):
    _escreve(tmp_path / "cases" / "c01.json", _caso(hipoteses=("H99",)))
    _escreve(tmp_path / "cases" / "_split_meta.json", {"seed": 1})
    problemas = check_repo(tmp_path).problems
    assert any("cases/c01.json" in p and "hypothesis" in p for p in problemas)


# 4. Anotacoes


def test_anotacao_cega_valida_passa(tmp_path):
    _caso_no_repo(tmp_path)
    _grava_anotacao(tmp_path, _anotacao(TID))
    assert check_repo(tmp_path).problems == []


def test_fail_sem_nota_e_problema_nomeando_arquivo(tmp_path):
    _caso_no_repo(tmp_path)
    _grava_anotacao(tmp_path, _anotacao(
        TID, verdicts={"C1": "pass", "C2": "fail", "C3": "pass", "C4": "n/a"}, note=""))
    problemas = check_repo(tmp_path).problems
    assert any(f"{TID}.v1.json" in p and "fail exige nota" in p for p in problemas)


def test_versoes_v1_e_v01_do_mesmo_trace_sao_problema(tmp_path):
    _caso_no_repo(tmp_path)
    _grava_anotacao(tmp_path, _anotacao(TID))
    _escreve(tmp_path / "annotations" / f"{TID}.v01.json", _anotacao(TID))
    problemas = check_repo(tmp_path).problems
    assert any("annotations/" in p and TID in p for p in problemas)


def test_anotacao_sem_caso_e_problema(tmp_path):
    tid_sem_caso = "c09-0a1b2c3d"
    _grava_anotacao(tmp_path, _anotacao(tid_sem_caso))
    problemas = check_repo(tmp_path).problems
    assert any("c09" in p for p in problemas)


# 5. Juizos


@pytest.mark.parametrize("payload", [
    {"trace_id": TID, "verdicts": {"C2": "talvez"}},
    {"trace_id": TID, "verdicts": {"C1": "talvez"}},
    {"trace_id": TID, "verdicts": {"C5": "pass"}},
    {"trace_id": "outro-trace-00000000", "verdicts": {"C2": "pass"}},
])
def test_juizo_invalido_e_problema(tmp_path, payload):
    _escreve(tmp_path / "judgments" / f"{TID}.json", payload)
    problemas = check_repo(tmp_path).problems
    assert any(f"judgments/{TID}.json" in p for p in problemas)


def test_juizo_com_c1_pass_e_aceito(tmp_path):
    # O juiz tambem julga C1 (citacao) quando o codigo deixa para ele.
    _escreve(tmp_path / "judgments" / f"{TID}.json", {"trace_id": TID, "verdicts": {"C1": "pass"}})
    problemas = check_repo(tmp_path).problems
    assert not any(f"judgments/{TID}.json" in p for p in problemas)


def test_juizo_com_c1_veredito_invalido_e_problema(tmp_path):
    _escreve(tmp_path / "judgments" / f"{TID}.json", {"trace_id": TID, "verdicts": {"C1": "talvez"}})
    problemas = check_repo(tmp_path).problems
    assert any(f"judgments/{TID}.json" in p and "C1" in p and "inválido" in p for p in problemas)


def test_juizo_com_c5_e_rejeitado_com_a_lista_atual_de_criterios(tmp_path):
    _escreve(tmp_path / "judgments" / f"{TID}.json", {"trace_id": TID, "verdicts": {"C5": "pass"}})
    problemas = check_repo(tmp_path).problems
    assert any("C5" in p and "critério fora do juiz (use C1, C2, C3 ou C4)" in p
               for p in problemas)


# 6. Recontagem do juiz


def test_recontagem_que_bate_nao_gera_problema(tmp_path):
    _repo_para_recontagem(tmp_path, tpr_reportado=1.0)
    assert check_repo(tmp_path).problems == []


def test_recontagem_ignora_trace_cego_cuja_ultima_versao_e_revisada(tmp_path):
    # Um trace da amostra cega que virou revisada nao calibra o juiz (R3).
    _repo_para_recontagem(tmp_path)
    tid3 = "c03-2b3c4d5e"
    _escreve(tmp_path / "cases" / "c03.json", _caso("c03"))
    _grava_anotacao(tmp_path, _anotacao(tid3))
    _grava_anotacao(tmp_path, _anotacao(tid3, kind="revised", version=2))
    _escreve(tmp_path / "drafts" / "annotations" / f"{tid3}.json", {"trace_id": tid3})
    _escreve(tmp_path / "judgments" / f"{tid3}.json", {"trace_id": tid3, "verdicts": {"C2": "fail"}})
    _escreve(tmp_path / "annotations" / "_samples.json",
             {"blind": {"seed": 1, "n": 3, "trace_ids": [TID, TID2, tid3]}})
    assert check_repo(tmp_path).problems == []


def test_tpr_de_c1_divergente_nomeia_o_criterio_c1(tmp_path):
    # Humano: C1 pass nos dois traces. Juiz: pass em TID e fail em TID2, logo TPR recontado 0.5.
    _repo_para_recontagem(tmp_path)
    _escreve(tmp_path / "judgments" / f"{TID}.json",
             {"trace_id": TID, "verdicts": {"C1": "pass", "C2": "pass"}})
    _escreve(tmp_path / "judgments" / f"{TID2}.json",
             {"trace_id": TID2, "verdicts": {"C1": "fail", "C2": "fail"}})
    _relatorio(tmp_path, "2026-01-15", {
        "C1": {"tpr": 0.0, "tnr": None, "n_pos": 2, "n_neg": 0, "calibrated": False},
        "C2": {"tpr": 1.0, "tnr": 1.0, "n_pos": 1, "n_neg": 1, "calibrated": False},
        "C3": _juiz_zerado(),
        "C4": _juiz_zerado(),
    })
    problemas = check_repo(tmp_path).problems
    assert len(problemas) == 1
    assert "juiz C1" in problemas[0] and "tpr" in problemas[0]


def test_o_relatorio_mais_recente_e_o_de_nome_mais_alto(tmp_path):
    _repo_para_recontagem(tmp_path)
    _relatorio(tmp_path, "2026-01-01", {"C2": {"tpr": 0.0, "tnr": 0.0, "n_pos": 9, "n_neg": 9}})
    assert check_repo(tmp_path).problems == []


def test_tpr_divergente_nomeia_o_criterio(tmp_path):
    _repo_para_recontagem(tmp_path, tpr_reportado=0.5)
    problemas = check_repo(tmp_path).problems
    assert len(problemas) == 1
    assert "C2" in problemas[0] and "tpr" in problemas[0]


# 7. Rascunhos e regras cegas


def test_revisada_sem_rascunho_e_problema(tmp_path):
    _caso_no_repo(tmp_path)
    _grava_anotacao(tmp_path, _anotacao(TID))
    _grava_anotacao(tmp_path, _anotacao(TID, kind="revised", version=2, note=""))
    problemas = check_repo(tmp_path).problems
    assert any(f"{TID}.v2.json" in p and "rascunho" in p for p in problemas)


def test_rascunho_de_trace_cego_sem_anotacao_cega_e_problema(tmp_path):
    _caso_no_repo(tmp_path)
    _escreve(tmp_path / "annotations" / "_samples.json",
             {"blind": {"seed": 1, "n": 1, "trace_ids": [TID]}})
    _escreve(tmp_path / "drafts" / "annotations" / f"{TID}.json", {"trace_id": TID})
    problemas = check_repo(tmp_path).problems
    assert any("rascunho de trace cego sem a anotação cega" in p and TID in p for p in problemas)


def test_rascunho_de_trace_cego_com_anotacao_cega_passa(tmp_path):
    _caso_no_repo(tmp_path)
    _grava_anotacao(tmp_path, _anotacao(TID))
    _escreve(tmp_path / "annotations" / "_samples.json",
             {"blind": {"seed": 1, "n": 1, "trace_ids": [TID]}})
    _escreve(tmp_path / "drafts" / "annotations" / f"{TID}.json", {"trace_id": TID})
    assert check_repo(tmp_path).problems == []


def test_gabarito_rascunhado_sem_caso_e_problema(tmp_path):
    _escreve(tmp_path / "drafts" / "cases" / "c99.v1.json", {"case_id": "c99"})
    problemas = check_repo(tmp_path).problems
    assert any("c99" in p for p in problemas)


# 8. Limiares


def _relatorio_c3(root: Path, tpr: float, tnr: float, n: int = 12) -> None:
    _relatorio(root, "2026-01-15", {
        "C3": {"tpr": tpr, "tnr": tnr, "n_pos": n, "n_neg": n, "calibrated": True}})


def _limiar_c3(root: Path) -> None:
    _escreve(root / "config" / "thresholds.json", {"C3": {"tpr": 0.8, "tnr": 0.8}})


def test_sem_limiares_avisa(tmp_path):
    resultado = check_repo(tmp_path)
    assert "sem limiar definido (config/thresholds.json)" in resultado.warnings


def test_limiar_violado_por_criterio_calibrado_e_problema(tmp_path):
    _limiar_c3(tmp_path)
    _relatorio_c3(tmp_path, tpr=0.7, tnr=0.9)
    problemas = check_repo(tmp_path).problems
    assert len(problemas) == 1
    assert "C3" in problemas[0] and "tpr" in problemas[0]


def test_limiar_cumprido_passa(tmp_path):
    _limiar_c3(tmp_path)
    _relatorio_c3(tmp_path, tpr=0.9, tnr=0.85)
    assert check_repo(tmp_path).problems == []


def test_criterio_nao_calibrado_nao_entra_no_limiar(tmp_path):
    _limiar_c3(tmp_path)
    _relatorio_c3(tmp_path, tpr=0.1, tnr=0.1, n=5)
    assert check_repo(tmp_path).problems == []


# 9. run.json e antes/depois


def _run(**campos) -> dict:
    base = {
        "p2_tag": "v1.2.0",
        "models": ["modelo-a", "modelo-b"],
        "judge_model": "juiz-x",
        "judge_prompts_sha256": "abc123",
    }
    base.update(campos)
    return base


def test_run_igual_ao_relatorio_passa(tmp_path):
    _escreve(tmp_path / "config" / "run.json", _run())
    _relatorio(tmp_path, "2026-01-15", {}, header=HEADER)
    resultado = check_repo(tmp_path)
    assert resultado.problems == []
    assert not any("incompleto" in w for w in resultado.warnings)


def test_tag_p2_diferente_exige_relatorio_novo(tmp_path):
    _escreve(tmp_path / "config" / "run.json", _run(p2_tag="v1.3.0"))
    _relatorio(tmp_path, "2026-01-15", {}, header=HEADER)
    problemas = check_repo(tmp_path).problems
    assert len(problemas) == 1
    assert ("mudou prompt, modelo ou tag do P2: falta um relatório novo "
            "(diferem: p2_tag)") in problemas[0]


def test_modelos_em_outra_ordem_nao_contam_como_mudanca(tmp_path):
    _escreve(tmp_path / "config" / "run.json", _run(models=["modelo-b", "modelo-a"]))
    _relatorio(tmp_path, "2026-01-15", {}, header=dict(HEADER, models=["modelo-a", "modelo-b"]))
    assert check_repo(tmp_path).problems == []


def test_run_incompleto_vira_aviso(tmp_path):
    _escreve(tmp_path / "config" / "run.json", _run(judge_model=None, models=[]))
    _relatorio(tmp_path, "2026-01-15", {}, header=HEADER)
    resultado = check_repo(tmp_path)
    assert resultado.problems == []
    assert any("incompleto" in w and "judge_model" in w and "models" in w
               for w in resultado.warnings)


def test_run_sem_relatorio_avisa(tmp_path):
    _escreve(tmp_path / "config" / "run.json", _run())
    resultado = check_repo(tmp_path)
    assert resultado.problems == []
    assert "sem relatório ainda" in " ".join(resultado.warnings)


# 10. Hash dos prompts


def test_hash_prompts_deterministico_muda_com_arquivo_e_none_sem_pasta(tmp_path):
    pasta = tmp_path / "prompts"
    _escreve(pasta / "a.md", "um")
    _escreve(pasta / "b.md", "dois")
    h = hash_prompts(pasta)
    assert isinstance(h, str) and len(h) == 64
    assert hash_prompts(pasta) == h

    _escreve(pasta / "x.txt", "nao e prompt")
    assert hash_prompts(pasta) == h

    _escreve(pasta / "b.md", "dois!")
    assert hash_prompts(pasta) != h

    assert hash_prompts(tmp_path / "nao-existe") is None
    (tmp_path / "vazia").mkdir()
    assert hash_prompts(tmp_path / "vazia") is None


# 11. Repositorio real


def test_repositorio_real_nao_tem_problemas():
    raiz = Path(__file__).resolve().parent.parent
    resultado = check_repo(raiz)
    assert resultado.problems == []
