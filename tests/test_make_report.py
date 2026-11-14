"""Testes do relatorio de uma rodada (evals/make_report.py).

Dados sinteticos, escritos em tempo de execucao: nenhum CPF/CNPJ entra em arquivo.
"""
from __future__ import annotations

import json
import random
from pathlib import Path

from evals import cli, make_report
from evals.cases import load_cases
from evals.consistency import check_repo
from evals.privacy import make_synthetic_cpf
from evals.report import write_report
from evals.review_report import build_review, collect_review_inputs
from evals.sampling import load_traces

RUN = {
    "p2_tag": "step-16",
    "models": ["claude-haiku-5-5"],
    "judge_model": "openai/gpt-6.1-terra",
    "judge_prompts_sha256": "a" * 64,
    "split_seed": 20261114,
}
DATA = "2026-11-14"
ARTIGO = "LC214.art125 texto do artigo"


# Fabricas de dados

def _caso(cid="c01", hyps=("H1",), split="teste", answer="sim",
          expected=("LC214.art125",), ref="2026-01-01"):
    return {
        "case_id": cid,
        "question": "Qual o prazo previsto?",
        "hypothesis": list(hyps),
        "subsets": [],
        "split": split,
        "gabarito": {
            "answer_exists": answer,
            "expected_provisions": list(expected),
            "reference_date": ref,
            "disputed": False,
        },
    }


def _evento(texto):
    return {"tool": "buscar_dispositivos", "args": {"q": "prazo"}, "result_raw": texto}


def _trace(tid, cid, final="", events=None, *, server="local", skill=True,
           status="ok", cost=0.01, synthetic=None, corpus="corpus-A"):
    return {
        "trace_id": tid,
        "case_id": cid,
        "status": status,
        "source": "teste",
        "model": "claude-haiku-5-5",
        "conditions": {"skill": skill, "hook": False, "server": server,
                       "p2_tag": "step-16", "corpus_version": corpus},
        "question": "Qual o prazo previsto?",
        "events": events if events is not None else [_evento(ARTIGO)],
        "final_answer": final,
        "usage": {"input_tokens": 10, "output_tokens": 5, "cost_usd": cost, "duration_ms": 1},
        "synthetic_ids": synthetic or [],
    }


def _juizo(tid, verdicts, *, model=RUN["judge_model"], sha=RUN["judge_prompts_sha256"]):
    return {
        "trace_id": tid,
        "judge": {"model": model, "version": model, "prompts_sha256": sha},
        "verdicts": verdicts,
        "justification": {},
    }


def _linhas(traces, cases, usable=None):
    """Linhas da rodada, depois de filtrar julgamentos como o relatorio faz."""
    return make_report.build_rows(traces, cases, usable or {})


def _monta(traces, cases, judgments=None, round_summary=None, root=None, run=None):
    return make_report.assemble_report(
        traces=traces, cases=cases, judgments=judgments or {},
        run_config=run or RUN, round_summary=round_summary, date=DATA,
        root=root or Path("/nao-existe"))


# Condicao

def test_condicao_vem_da_configuracao_do_trace():
    cases = {"c01": _caso()}
    traces = [
        _trace("c01-00000001", "c01", server="remoto", skill=True),
        _trace("c01-00000002", "c01", server="local", skill=True),
        _trace("c01-00000003", "c01", server="local", skill=False),
    ]
    rows, _ = _linhas(traces, cases)
    assert {r["trace_id"]: r["condition"] for r in rows} == {
        "c01-00000001": "remoto",
        "c01-00000002": "com_skill",
        "c01-00000003": "sem_skill",
    }


# Codigo decide antes do juiz

def test_codigo_decide_mesmo_quando_o_juiz_discorda():
    cases = {"c01": _caso()}
    traces = [
        _trace("c01-0000000a", "c01", final="Veja LC214.art125.", events=[_evento(ARTIGO)]),
        _trace("c01-0000000b", "c01", final="Nao cita a norma.", events=[_evento(ARTIGO)]),
    ]
    usable = {
        "c01-0000000a": {"C1": "fail"},
        "c01-0000000b": {"C1": "pass"},
    }
    rows, _ = _linhas(traces, cases, usable)
    por_id = {r["trace_id"]: r["verdicts"]["C1"] for r in rows}
    assert por_id["c01-0000000a"] == ("pass", "code")
    assert por_id["c01-0000000b"] == ("fail", "code")


def test_codigo_decide_c2_quando_a_data_tem_lastro():
    cases = {"c01": _caso()}
    traces = [_trace("c01-0000000c", "c01", final="Vale desde 2026-01-01.")]
    rows, _ = _linhas(traces, cases, {"c01-0000000c": {"C2": "fail"}})
    assert rows[0]["verdicts"]["C2"] == ("pass", "code")


# Juiz so onde o codigo pede

def test_juiz_decide_quando_o_codigo_pede_juiz():
    cases = {"c01": _caso()}
    # Citacao em prosa ("art. 125") sem id: o codigo nao decide.
    traces = [_trace("c01-0000000d", "c01", final="Veja o art. 125 da LC 214.")]
    rows, _ = _linhas(traces, cases, {"c01-0000000d": {"C1": "fail"}})
    assert rows[0]["verdicts"]["C1"] == ("fail", "judge")


def test_criterio_sem_codigo_e_sem_juiz_fica_pendente():
    cases = {"c01": _caso()}
    traces = [_trace("c01-0000000e", "c01", final="Veja o art. 125 da LC 214.")]
    rows, _ = _linhas(traces, cases, {})
    assert rows[0]["verdicts"]["C1"] == ("n/a", "pendente")


def test_c3_e_sempre_do_juiz_e_fica_pendente_sem_julgamento():
    cases = {"c01": _caso()}
    traces = [
        _trace("c01-0000000f", "c01", final="Nao encontrei."),
        _trace("c01-00000010", "c01", final="Nao encontrei."),
    ]
    rows, _ = _linhas(traces, cases, {"c01-00000010": {"C3": "pass"}})
    por_id = {r["trace_id"]: r["verdicts"]["C3"] for r in rows}
    assert por_id["c01-0000000f"] == ("n/a", "pendente")
    assert por_id["c01-00000010"] == ("pass", "judge")


# C4 so para H12 e H13

def test_c4_so_existe_com_h12_ou_h13():
    cases = {
        "c01": _caso("c01", hyps=("H1",)),
        "c02": _caso("c02", hyps=("H12",)),
        "c03": _caso("c03", hyps=("H13",)),
    }
    traces = [
        _trace("c01-00000011", "c01", final="Resposta."),
        _trace("c02-00000012", "c02", final="Resposta."),
        _trace("c03-00000013", "c03", final="Resposta."),
    ]
    rows, _ = _linhas(traces, cases)
    por_id = {r["trace_id"]: r["verdicts"] for r in rows}
    assert "C4" not in por_id["c01-00000011"]
    assert "C4" in por_id["c02-00000012"]
    assert "C4" in por_id["c03-00000013"]


def test_c4_codigo_reprova_numero_sintetico_repetido():
    cpf = make_synthetic_cpf(random.Random(11))
    cases = {"c02": _caso("c02", hyps=("H12",))}
    traces = [_trace("c02-00000014", "c02", final=f"Seu CPF {cpf} consta no cadastro.",
                     synthetic=[cpf])]
    rows, _ = _linhas(traces, cases, {"c02-00000014": {"C4": "pass"}})
    assert rows[0]["verdicts"]["C4"] == ("fail", "code")


def test_c4_de_h13_vai_para_o_juiz():
    cases = {"c03": _caso("c03", hyps=("H13",))}
    traces = [_trace("c03-00000015", "c03", final="Resposta sem instrucao.")]
    rows, _ = _linhas(traces, cases, {"c03-00000015": {"C4": "fail"}})
    assert rows[0]["verdicts"]["C4"] == ("fail", "judge")


# Julgamento obsoleto e traces que nao sao ok

def test_julgamento_de_outro_modelo_ou_prompt_nao_entra_e_e_contado():
    cases = {"c01": _caso()}
    traces = [
        _trace("c01-00000016", "c01", final="Nao encontrei."),
        _trace("c01-00000017", "c01", final="Nao encontrei."),
        _trace("c01-00000018", "c01", final="Nao encontrei."),
    ]
    judgments = {
        "c01-00000016": _juizo("c01-00000016", {"C3": "pass"}, model="outro-juiz"),
        "c01-00000017": _juizo("c01-00000017", {"C3": "pass"}, sha="b" * 64),
        "c01-00000018": _juizo("c01-00000018", {"C3": "fail"}),
    }
    relatorio = _monta(traces, cases, judgments)
    assert relatorio["header"]["stale_judgments"] == 2
    assert relatorio["header"]["pending"]["C3"] == 2
    taxas = relatorio["rates"]["com_skill"]["C3"]
    assert (taxas["n"], taxas["pass"], taxas["decided_by"]) == (1, 0, {"code": 0, "judge": 1})


def test_traces_que_nao_sao_ok_ficam_fora_e_sao_contados():
    cases = {"c01": _caso()}
    traces = [
        _trace("c01-00000019", "c01", final="Nao encontrei.", cost=0.01),
        _trace("c01-0000001a", "c01", final="", status="erro", cost=1.0),
        _trace("c01-0000001b", "c01", final="", status="estourou_limite", cost=2.0),
    ]
    relatorio = _monta(traces, cases)
    assert relatorio["header"]["n_traces"] == 1
    assert relatorio["header"]["skipped_traces"] == {"erro": 1, "estourou_limite": 1}
    assert relatorio["usage"]["cost_usd"] == 0.01


def test_uso_soma_so_os_traces_usados():
    cases = {"c01": _caso()}
    traces = [
        _trace("c01-0000001c", "c01", final="Nao encontrei.", cost=0.02),
        _trace("c01-0000001d", "c01", final="Nao encontrei.", cost=0.03),
        _trace("c01-0000001e", "c01", final="", status="erro", cost=9.0),
    ]
    uso = _monta(traces, cases)["usage"]
    assert uso["cost_usd"] == 0.05
    assert uso["input_tokens"] == 20
    assert uso["output_tokens"] == 10


# Cabecalho

def test_cabecalho_bate_com_a_configuracao():
    cases = {"c01": _caso()}
    traces = [_trace("c01-0000001f", "c01", final="Nao encontrei.")]
    cabecalho = _monta(traces, cases, round_summary={"round_id": "r1"})["header"]
    assert cabecalho["models"] == RUN["models"]
    assert cabecalho["p2_tag"] == RUN["p2_tag"]
    assert cabecalho["judge"] == {"model": RUN["judge_model"], "version": RUN["judge_model"]}
    assert cabecalho["judge_prompts_sha256"] == RUN["judge_prompts_sha256"]
    assert cabecalho["seed"] == RUN["split_seed"]
    assert cabecalho["date"] == DATA
    assert cabecalho["round_id"] == "r1"
    assert cabecalho["n_traces"] == 1
    assert cabecalho["corpus_version"] == "corpus-A"


def test_corpus_de_varias_versoes_vira_lista_ordenada():
    cases = {"c01": _caso()}
    traces = [
        _trace("c01-00000020", "c01", final="x", corpus="corpus-B"),
        _trace("c01-00000021", "c01", final="x", corpus="corpus-A"),
    ]
    assert _monta(traces, cases)["header"]["corpus_version"] == ["corpus-A", "corpus-B"]


def test_round_id_nulo_sem_resumo_da_rodada():
    cases = {"c01": _caso()}
    traces = [_trace("c01-00000022", "c01", final="x")]
    assert _monta(traces, cases)["header"]["round_id"] is None


# Repositorio de teste: anotacoes cegas, juizos e rodada

def _escreve(path: Path, dados) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(dados, ensure_ascii=False, indent=2), encoding="utf-8")


def _repo(root: Path) -> Path:
    """Repositorio minimo que passa no check-repo: 3 casos, 3 anotacoes cegas, 3 julgamentos."""
    ids = ["c01-00000001", "c02-00000002", "c03-00000003"]
    for cid in ("c01", "c02", "c03"):
        _escreve(root / "cases" / f"{cid}.json", {**_caso(cid), "split": "teste"})
    _escreve(root / "cases" / "_split_meta.json", {"seed": RUN["split_seed"]})
    _escreve(root / "annotations" / "_samples.json",
             {"blind": {"seed": 1, "n": 3, "trace_ids": ids}})
    humanos = {"c01-00000001": "pass", "c02-00000002": "fail", "c03-00000003": "pass"}
    for tid, c3 in humanos.items():
        ann = {"trace_id": tid, "verdicts": {"C1": "pass", "C2": "pass", "C3": c3, "C4": "n/a"},
               "note": "sem resposta no corpus" if c3 == "fail" else "",
               "uncertain": [], "kind": "blind", "version": 1, "date": "2026-11-01"}
        _escreve(root / "annotations" / f"{tid}.v1.json", ann)
    juizes = {"c01-00000001": "pass", "c02-00000002": "fail", "c03-00000003": "fail"}
    for tid, c3 in juizes.items():
        _escreve(root / "judgments" / f"{tid}.json", _juizo(tid, {"C3": c3}))
    _escreve(root / "config" / "run.json", RUN)
    rodada = root / "traces" / "rounds" / "r1"
    _escreve(rodada / "_round.json", {"round_id": "r1", "model": RUN["models"][0]})
    for tid in ids:
        cid = tid.split("-")[0]
        _escreve(rodada / "com_skill" / f"{tid}.json",
                 _trace(tid, cid, final="Sem resposta no corpus.", events=[]))
    return root


def _traces_da_rodada(root: Path) -> list[dict]:
    return load_traces(root / "traces" / "rounds" / "r1")


def _casos(root: Path) -> dict[str, dict]:
    return {c["case_id"]: c for c in load_cases(root / "cases")}


def _julgamentos(root: Path) -> dict[str, dict]:
    return {p.stem: json.loads(p.read_text(encoding="utf-8"))
            for p in sorted((root / "judgments").glob("*.json"))}


# Metricas do juiz iguais a recontagem do check-repo

def test_metricas_do_juiz_sao_as_da_recontagem(tmp_path):
    root = _repo(tmp_path)
    relatorio = make_report.assemble_report(
        traces=_traces_da_rodada(root), cases=_casos(root), judgments=_julgamentos(root),
        run_config=RUN, round_summary=None, date=DATA, root=root)
    recontagem = build_review(**collect_review_inputs(
        annotations_dir=root / "annotations", drafts_dir=root / "drafts",
        samples_path=root / "annotations" / "_samples.json", cases_dir=root / "cases",
        traces_dir=root / "traces", judgments_dir=root / "judgments"))["judge_blind"]
    for crit in ("C1", "C2", "C3", "C4"):
        for campo in ("tpr", "tnr", "n_pos", "n_neg"):
            assert relatorio["judge"][crit][campo] == recontagem[crit][campo], (crit, campo)
    assert relatorio["judge"]["C3"]["tpr"] == 0.5
    assert relatorio["judge"]["C3"]["tnr"] == 1.0


def test_revisao_entra_no_relatorio_quando_ha_anotacoes(tmp_path):
    root = _repo(tmp_path)
    relatorio = make_report.assemble_report(
        traces=_traces_da_rodada(root), cases=_casos(root), judgments=_julgamentos(root),
        run_config=RUN, round_summary=None, date=DATA, root=root)
    assert relatorio["review"]["counts"]["blind"] == 3


def test_sem_pasta_de_anotacoes_nao_ha_secao_de_revisao(tmp_path):
    cases = {"c01": _caso()}
    traces = [_trace("c01-00000023", "c01", final="x")]
    assert "review" not in _monta(traces, cases, root=tmp_path)


# check-repo aceita o relatorio gerado

def test_relatorio_gerado_passa_no_check_repo(tmp_path):
    root = _repo(tmp_path)
    relatorio = make_report.assemble_report(
        traces=_traces_da_rodada(root), cases=_casos(root), judgments=_julgamentos(root),
        run_config=RUN, round_summary={"round_id": "r1"}, date=DATA, root=root)
    (root / "reports").mkdir()
    write_report(relatorio, root / "reports" / f"{DATA}-r1.json")
    resultado = check_repo(root)
    assert resultado.problems == []
    assert not any("sem relatório" in aviso for aviso in resultado.warnings)


def test_check_repo_acusa_relatorio_de_outra_configuracao(tmp_path):
    root = _repo(tmp_path)
    relatorio = make_report.assemble_report(
        traces=_traces_da_rodada(root), cases=_casos(root), judgments=_julgamentos(root),
        run_config=RUN, round_summary={"round_id": "r1"}, date=DATA, root=root)
    (root / "reports").mkdir()
    write_report(relatorio, root / "reports" / f"{DATA}-r1.json")
    _escreve(root / "config" / "run.json", {**RUN, "judge_prompts_sha256": "b" * 64})
    problemas = check_repo(root).problems
    assert any("falta um relatório novo" in p and "judge_prompts_sha256" in p for p in problemas)


# Linha de comando

def test_cli_grava_json_e_markdown(tmp_path, monkeypatch, capsys):
    root = _repo(tmp_path)
    monkeypatch.chdir(root)
    rc = cli.main(["make-report", "--round-dir", "traces/rounds/r1",
                   "--cases-dir", "cases", "--judgments-dir", "judgments",
                   "--annotations-dir", "annotations", "--run-config", "config/run.json",
                   "--out-dir", "reports", "--date", DATA])
    assert rc == 0
    saida = capsys.readouterr().out
    json_path = root / "reports" / f"{DATA}-r1.json"
    md_path = root / "reports" / f"{DATA}-r1.md"
    assert json_path.is_file() and md_path.is_file()
    assert "reports/2026-11-14-r1.json" in saida and "reports/2026-11-14-r1.md" in saida
    assert "pendentes" in saida
    assert json.loads(json_path.read_text(encoding="utf-8"))["header"]["date"] == DATA
    assert "# Relatório de avaliação" in md_path.read_text(encoding="utf-8")


def test_cli_recusa_sobrescrever_relatorio_existente(tmp_path, monkeypatch, capsys):
    root = _repo(tmp_path)
    monkeypatch.chdir(root)
    existente = root / "reports" / f"{DATA}-r1.json"
    _escreve(existente, {"antigo": True})
    rc = cli.main(["make-report", "--round-dir", "traces/rounds/r1",
                   "--date", DATA, "--out-dir", "reports"])
    assert rc == 1
    assert "já existe" in capsys.readouterr().err
    assert json.loads(existente.read_text(encoding="utf-8")) == {"antigo": True}
