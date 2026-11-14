"""Rodada em lote (evals/round.py). Nenhum teste chama o `claude` de verdade: o `run` e fake."""
from __future__ import annotations

import json
import random
import subprocess
from pathlib import Path

import pytest

from evals import cli
from evals import round as rodada
from evals.runner import RemoteNotConfigured, prepare_workdir

FIX = Path(__file__).parent / "fixtures"
STREAM_OK = (FIX / "stream_hook.jsonl").read_text(encoding="utf-8")
CUSTO_POR_RUN = 0.00566555  # custo do stream_hook.jsonl


def _caso(cid, subsets=()):
    return {"case_id": cid, "question": f"pergunta {cid} sobre o IBS?", "hypothesis": ["H1"],
            "split": "teste", "subsets": list(subsets),
            "gabarito": {"answer_exists": "sim", "expected_provisions": ["CF.art156-A"],
                         "reference_date": "2026-11-11", "disputed": False}}


CASOS = [_caso("c01"), _caso("c02", ["sem_skill", "remoto"]),
         _caso("c03", ["sem_skill"]), _caso("c04", ["remoto"])]


def fake_p2(tmp_path: Path) -> Path:
    p2 = tmp_path / "p2"
    if p2.exists():
        return p2
    (p2 / ".claude" / "skills" / "consultar").mkdir(parents=True)
    (p2 / ".claude" / "skills" / "consultar" / "SKILL.md").write_text("skill")
    (p2 / ".claude" / "settings.json").write_text('{"hooks": {}}')
    (p2 / "corpus").mkdir()
    (p2 / "corpus" / "dispositivos.json").write_text('{"d": 1}')
    (p2 / ".mcp.json").write_text(json.dumps({"mcpServers": {
        "taxlaw": {"type": "stdio", "command": "uv", "args": ["-m", "taxlaw.server"]}}}))
    return p2


class FakeRun:
    """Faz o papel de subprocess.run: guarda as chamadas e devolve um stream pronto."""

    def __init__(self, stdout=STREAM_OK):
        self.calls = []
        self.stdout = stdout

    def __call__(self, argv, **kw):
        self.calls.append((argv, kw))
        return subprocess.CompletedProcess(argv, 0, self.stdout, "")


class RecordPrepare:
    """Registra cada preparo de diretorio de trabalho e usa o preparo real por tras."""

    def __init__(self):
        self.calls = []

    def __call__(self, p2_dir, dest, *, with_skill, server):
        self.calls.append({"dest": Path(dest), "with_skill": with_skill, "server": server})
        return prepare_workdir(p2_dir, dest, with_skill=with_skill, server=server)


def _rodada(tmp_path, cases, conditions=("com_skill",), run=None, prepare=None, **over):
    kw = dict(conditions=list(conditions), model="claude-haiku-5-5", p2_dir=fake_p2(tmp_path),
              p2_tag="step-16", out_dir=tmp_path / "rounds", workdirs_dir=tmp_path / "workdirs",
              budget_usd=1.0, per_case_usd=0.2, seed=20261114, run=run or FakeRun(),
              prepare=prepare or RecordPrepare(), round_id="r1")
    kw.update(over)
    return rodada.run_round(cases, **kw)


def _escreve_casos(cases_dir: Path, casos) -> None:
    cases_dir.mkdir(parents=True, exist_ok=True)
    for c in casos:
        (cases_dir / f"{c['case_id']}.json").write_text(json.dumps(c), encoding="utf-8")


def _argv(tmp_path, *extra, cases_dir=None):
    # Os extras vem depois: o argparse fica com a ultima ocorrencia de cada opcao.
    return ["--model", "claude-haiku-5-5", "--p2-dir", str(fake_p2(tmp_path)),
            "--p2-tag", "step-16", "--budget-usd", "1", "--per-case-usd", "0.2",
            "--conditions", "com_skill",
            "--cases-dir", str(cases_dir or tmp_path / "cases"),
            "--out-dir", str(tmp_path / "rounds"), "--workdirs-dir", str(tmp_path / "workdirs"),
            "--round-id", "r1", *extra]


# --- plano -----------------------------------------------------------------------------

def test_plan_filters_by_subset_and_orders_by_condition_then_case():
    plano = rodada.plan_round(CASOS, ["sem_skill", "com_skill", "remoto"])
    assert [(cond, c["case_id"]) for cond, c in plano] == [
        ("sem_skill", "c02"), ("sem_skill", "c03"),
        ("com_skill", "c01"), ("com_skill", "c02"), ("com_skill", "c03"), ("com_skill", "c04"),
        ("remoto", "c02"), ("remoto", "c04")]


def test_plan_is_deterministic_whatever_the_input_order():
    a = rodada.plan_round(CASOS, ["com_skill", "remoto"])
    b = rodada.plan_round(list(reversed(CASOS)), ["com_skill", "remoto"])
    assert a == b


def test_plan_rejects_unknown_condition():
    with pytest.raises(ValueError, match="condi"):
        rodada.plan_round(CASOS, ["com_skill", "xpto"])


def test_plan_rejects_repeated_condition():
    with pytest.raises(ValueError, match="repet"):
        rodada.plan_round(CASOS, ["com_skill", "com_skill"])


# --- remoto ----------------------------------------------------------------------------

def test_remote_without_env_fails_before_anything(tmp_path, monkeypatch):
    monkeypatch.delenv("TAXLAW_REMOTE_URL", raising=False)
    monkeypatch.setenv("TAXLAW_HTTP_TOKEN", "segredo-de-teste")
    run, prep = FakeRun(), RecordPrepare()
    with pytest.raises(RemoteNotConfigured) as exc:
        _rodada(tmp_path, CASOS, conditions=("com_skill", "remoto"), run=run, prepare=prep)
    assert run.calls == [] and prep.calls == []
    assert not (tmp_path / "rounds").exists()
    assert "TAXLAW_REMOTE_URL" in str(exc.value) and "segredo-de-teste" not in str(exc.value)


# --- diretorios de trabalho ------------------------------------------------------------

def test_one_workdir_per_condition_with_the_matching_skill_and_server(tmp_path, monkeypatch):
    monkeypatch.setenv("TAXLAW_REMOTE_URL", "https://exemplo.invalid/mcp")
    monkeypatch.setenv("TAXLAW_HTTP_TOKEN", "x")
    prep = RecordPrepare()
    _rodada(tmp_path, CASOS, conditions=("com_skill", "sem_skill", "remoto"), prepare=prep)
    assert [c["dest"] for c in prep.calls] == [
        tmp_path / "workdirs" / "r1-com_skill", tmp_path / "workdirs" / "r1-sem_skill",
        tmp_path / "workdirs" / "r1-remoto"]
    assert [(c["with_skill"], c["server"]) for c in prep.calls] == [
        (True, "local"), (False, "local"), (True, "remoto")]


def test_trace_records_the_skill_of_its_condition(tmp_path):
    _rodada(tmp_path, CASOS, conditions=("com_skill", "sem_skill"))
    com = json.loads(next((tmp_path / "rounds" / "r1" / "com_skill").glob("*.json"))
                     .read_text(encoding="utf-8"))
    sem = json.loads(next((tmp_path / "rounds" / "r1" / "sem_skill").glob("*.json"))
                     .read_text(encoding="utf-8"))
    assert com["conditions"]["skill"] is True and sem["conditions"]["skill"] is False


# --- execucao e traces -------------------------------------------------------------------

def test_traces_land_in_the_folder_of_their_condition(tmp_path):
    run = FakeRun()
    _rodada(tmp_path, CASOS, conditions=("com_skill", "sem_skill"), run=run)
    com = list((tmp_path / "rounds" / "r1" / "com_skill").glob("*.json"))
    sem = list((tmp_path / "rounds" / "r1" / "sem_skill").glob("*.json"))
    assert len(com) == 4 and len(sem) == 2
    assert len(run.calls) == 6


def test_one_shared_budget_and_per_case_limit_reach_the_runner(tmp_path):
    run = FakeRun()
    resumo = _rodada(tmp_path, CASOS[:2], run=run, budget_usd=1.0, per_case_usd=0.25)
    assert resumo["spent_usd"] == round(2 * CUSTO_POR_RUN, 4)
    for argv, _kw in run.calls:
        assert argv[argv.index("--max-budget-usd") + 1] == "0.25"


def test_error_trace_is_listed_in_the_summary_with_every_attempt(tmp_path):
    class Errors(FakeRun):
        def __init__(self):
            super().__init__()
            self.n = 0

        def __call__(self, argv, **kw):
            self.n += 1
            self.stdout = "lixo" if self.n == 1 else STREAM_OK
            return super().__call__(argv, **kw)

    resumo = _rodada(tmp_path, CASOS[:1], run=Errors())
    run = resumo["runs"][0]
    assert run["status"] == "ok" and len(run["traces"]) == 2 and run["investigate"] is False


def test_budget_exceeded_stops_and_the_summary_records_it(tmp_path):
    run = FakeRun()
    resumo = _rodada(tmp_path, [_caso("c01"), _caso("c02"), _caso("c03")], run=run,
                     budget_usd=0.01)
    assert len(run.calls) == 2
    assert resumo["stopped"] and "teto" in resumo["stopped"]
    assert [r["case_id"] for r in resumo["runs"]] == ["c01", "c02"]
    assert resumo["spent_usd"] == round(2 * CUSTO_POR_RUN, 4)
    assert len(list((tmp_path / "rounds" / "r1" / "com_skill").glob("*.json"))) == 2


# --- resumo -----------------------------------------------------------------------------

def test_summary_json_has_the_agreed_content(tmp_path):
    resumo = _rodada(tmp_path, CASOS[:2], budget_usd=1.0, per_case_usd=0.2, seed=7)
    assert set(resumo) == {"round_id", "model", "p2_tag", "conditions", "budget_usd",
                           "per_case_usd", "seed", "spent_usd", "stopped", "runs"}
    assert resumo["round_id"] == "r1" and resumo["model"] == "claude-haiku-5-5"
    assert resumo["p2_tag"] == "step-16" and resumo["conditions"] == ["com_skill"]
    assert resumo["budget_usd"] == 1.0 and resumo["per_case_usd"] == 0.2 and resumo["seed"] == 7
    assert resumo["stopped"] is None
    primeiro = resumo["runs"][0]
    assert primeiro["condition"] == "com_skill" and primeiro["case_id"] == "c01"
    assert primeiro["status"] == "ok" and primeiro["investigate"] is False
    assert primeiro["traces"] == [p.name for p in
                                  (tmp_path / "rounds" / "r1" / "com_skill").glob("c01-*.json")]
    gravado = json.loads((tmp_path / "rounds" / "r1" / "_round.json").read_text(encoding="utf-8"))
    assert gravado == resumo


def test_round_id_defaults_to_a_timestamp(tmp_path):
    resumo = _rodada(tmp_path, CASOS[:1], round_id=None)
    assert len(resumo["round_id"]) >= 8 and (tmp_path / "rounds" / resumo["round_id"]).is_dir()


def test_existing_round_is_refused(tmp_path):
    _rodada(tmp_path, CASOS[:1])
    with pytest.raises(FileExistsError):
        _rodada(tmp_path, CASOS[:1])


# --- CLI ---------------------------------------------------------------------------------

def test_cli_unknown_condition_exits_2_and_runs_nothing(tmp_path, capsys):
    _escreve_casos(tmp_path / "cases", CASOS)
    run = FakeRun()
    assert rodada.main(_argv(tmp_path, "--conditions", "com_skill,xpto"), run=run) == 2
    assert "xpto" in capsys.readouterr().err and run.calls == []


def test_cli_dry_run_counts_and_prepares_nothing(tmp_path, capsys):
    _escreve_casos(tmp_path / "cases", CASOS)
    run, prep = FakeRun(), RecordPrepare()
    rc = rodada.main(_argv(tmp_path, "--dry-run", "--conditions", "com_skill,sem_skill,remoto"),
                     run=run, prepare=prep)
    out = capsys.readouterr().out
    assert rc == 0 and run.calls == [] and prep.calls == []
    assert "com_skill: 4" in out and "sem_skill: 2" in out and "remoto: 2" in out
    assert not (tmp_path / "rounds").exists() and not (tmp_path / "workdirs").exists()


def test_cli_prints_one_line_per_run_and_the_total(tmp_path, capsys):
    _escreve_casos(tmp_path / "cases", CASOS[:2])
    rc = rodada.main(_argv(tmp_path), run=FakeRun())
    out = capsys.readouterr().out.splitlines()
    assert rc == 0
    assert any("com_skill" in l and "c01" in l and "ok" in l for l in out)
    assert out[-1].startswith("gasto total: US$ ") and "0.0113" in out[-1]


def test_cli_exits_1_when_the_budget_stops_the_round(tmp_path, capsys):
    _escreve_casos(tmp_path / "cases", CASOS[:3])
    rc = rodada.main(_argv(tmp_path, "--budget-usd", "0.01"), run=FakeRun())
    assert rc == 1 and "teto" in capsys.readouterr().err


def test_cli_exits_1_when_a_case_must_be_investigated(tmp_path, capsys):
    _escreve_casos(tmp_path / "cases", CASOS[:1])
    rc = rodada.main(_argv(tmp_path), run=FakeRun(stdout="lixo"))
    assert rc == 1
    resumo = json.loads((tmp_path / "rounds" / "r1" / "_round.json").read_text(encoding="utf-8"))
    assert resumo["runs"][0]["investigate"] is True


def test_cli_remote_without_env_exits_1_without_printing_values(tmp_path, capsys, monkeypatch):
    monkeypatch.delenv("TAXLAW_REMOTE_URL", raising=False)
    monkeypatch.setenv("TAXLAW_HTTP_TOKEN", "segredo-de-teste")
    _escreve_casos(tmp_path / "cases", CASOS)
    run = FakeRun()
    rc = rodada.main(_argv(tmp_path, "--conditions", "remoto"), run=run)
    captured = capsys.readouterr()
    assert rc == 1 and run.calls == []
    assert "TAXLAW_REMOTE_URL" in captured.err
    assert "segredo-de-teste" not in captured.err + captured.out


def test_cli_is_registered_as_run_round(tmp_path, capsys):
    assert "run-round" in cli.DELEGADOS
    _escreve_casos(tmp_path / "cases", CASOS)
    assert cli.main(["run-round", *_argv(tmp_path, "--dry-run")]) == 0
    assert "com_skill" in capsys.readouterr().out


# --- testes acrescentados na revisao (mutacoes que sobreviviam) ------------------------

def test_remote_condition_calls_the_remote_server_tools(tmp_path, monkeypatch):
    monkeypatch.setenv("TAXLAW_REMOTE_URL", "https://exemplo.invalid/mcp")
    monkeypatch.setenv("TAXLAW_HTTP_TOKEN", "segredo-de-teste")
    run = FakeRun()
    _rodada(tmp_path, [_caso("c04", ["remoto"])], conditions=("remoto",), run=run)
    argv = run.calls[0][0]
    assert "mcp__taxlaw-remoto__buscar_dispositivos" in argv
    assert "mcp__taxlaw__buscar_dispositivos" not in argv


def test_same_seed_gives_the_same_synthetic_numbers(tmp_path):
    caso = _caso("c09")
    caso["question"] = "Meu CPF é {CPF}, como fica o IBS?"
    run_a, run_b = FakeRun(), FakeRun()
    _rodada(tmp_path, [caso], run=run_a, round_id="ra")
    _rodada(tmp_path, [caso], run=run_b, round_id="rb")
    pergunta_a = run_a.calls[0][1]["input"]
    assert "{CPF}" not in pergunta_a
    assert pergunta_a == run_b.calls[0][1]["input"]
