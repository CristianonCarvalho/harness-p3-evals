"""Runner das rodadas (Tarefa 13, passo 26). Nenhum teste chama o `claude` de verdade."""
import json
import random
import subprocess
from pathlib import Path

import pytest

from evals.budget import BudgetExceeded, BudgetGuard
from evals.privacy import is_valid_cnpj, is_valid_cpf
from evals.trace import load_trace, validate_trace
from evals import runner
from evals.runner import (RemoteNotConfigured, build_argv, build_prompt, prepare_workdir,
                          run_case, run_with_retries, substitute_placeholders)

FIX = Path(__file__).parent / "fixtures"
# Amostra real com --include-hook-events: o hook do P2 roda em cada chamada (3 chamadas).
STREAM_OK = (FIX / "stream_hook.jsonl").read_text(encoding="utf-8")


def make_case(question="Qual o percentual do IBS?", **over):
    c = {"case_id": "c01", "question": question, "hypothesis": ["H1"], "split": "teste",
         "subsets": [], "gabarito": {"answer_exists": "sim",
                                     "expected_provisions": ["CF.art156-A"],
                                     "reference_date": "2026-11-11", "disputed": False}}
    c.update(over)
    return c


def fake_p2(tmp_path: Path) -> Path:
    p2 = tmp_path / "p2"
    (p2 / ".claude" / "skills" / "consultar").mkdir(parents=True)
    (p2 / ".claude" / "skills" / "consultar" / "SKILL.md").write_text("skill")
    (p2 / ".claude" / "settings.json").write_text('{"hooks": {}}')
    (p2 / ".claude" / "settings.local.json").write_text('{"x": 1}')
    (p2 / ".git").mkdir()
    (p2 / ".venv").mkdir()
    (p2 / "traces").mkdir()
    (p2 / "corpus").mkdir()
    (p2 / "corpus" / "dispositivos.json").write_text('{"d": 1}')
    (p2 / ".mcp.json").write_text(json.dumps({"mcpServers": {
        "eco": {"type": "stdio", "command": "uv", "args": ["eco"]},
        "taxlaw": {"type": "stdio", "command": "uv", "args": ["-m", "taxlaw.server"]}}}))
    return p2


class FakeRun:
    """Faz o papel de subprocess.run: guarda a chamada e devolve um stream pronto."""

    def __init__(self, stdout: str | bytes = STREAM_OK, returncode=0, raise_timeout=False):
        self.calls = []
        self.stdout, self.returncode, self.raise_timeout = stdout, returncode, raise_timeout

    def __call__(self, argv, **kw):
        self.calls.append((argv, kw))
        if self.raise_timeout:
            raise subprocess.TimeoutExpired(argv, kw.get("timeout") or 0, output=self.stdout)
        return subprocess.CompletedProcess(argv, self.returncode, self.stdout, "")


def _run(tmp_path, run, case=None, guard=None, **over):
    wd = over.pop("workdir", None) or prepare_workdir(fake_p2(tmp_path), tmp_path / "wd",
                                                     with_skill=True, server="local")
    kw = dict(model="claude-haiku-5-5", server="local", workdir=wd, p2_tag="step-16",
              traces_dir=tmp_path / "traces", guard=guard or BudgetGuard(1.0),
              max_budget_usd=0.2, rng=random.Random(7), run=run)
    kw.update(over)
    return run_case(case or make_case(), **kw)


# --- argv -------------------------------------------------------------------------

def test_argv_isolates_the_execution(tmp_path):
    argv = build_argv("claude-haiku-5-5", server="local", max_budget_usd=0.2,
                      mcp_config=tmp_path / "m.json")
    assert argv[:2] == ["claude", "-p"]
    for par in (["--output-format", "stream-json"], ["--model", "claude-haiku-5-5"],
                ["--max-budget-usd", "0.2"], ["--setting-sources", "project"],
                ["--mcp-config", str(tmp_path / "m.json")], ["--tools", "Skill,ToolSearch"]):
        i = argv.index(par[0])
        assert argv[i:i + 2] == par
    for flag in ("--verbose", "--no-session-persistence", "--strict-mcp-config",
                 "--include-hook-events"):
        assert flag in argv
    i = argv.index("--allowedTools")
    assert argv[i + 1:] == ["mcp__taxlaw__buscar_dispositivos", "mcp__taxlaw__obter_dispositivo"]


def test_argv_for_remote_uses_the_remote_prefix(tmp_path):
    argv = build_argv("m", server="remoto", max_budget_usd=0.2, mcp_config=tmp_path / "m.json")
    assert argv[-2:] == ["mcp__taxlaw-remoto__buscar_dispositivos",
                         "mcp__taxlaw-remoto__obter_dispositivo"]


def test_argv_rejects_unknown_server(tmp_path):
    with pytest.raises(ValueError, match="server"):
        build_argv("m", server="outro", max_budget_usd=0.2, mcp_config=tmp_path / "m.json")


# --- diretorio de trabalho ----------------------------------------------------------

def test_workdir_without_skill_keeps_the_hook(tmp_path):
    wd = prepare_workdir(fake_p2(tmp_path), tmp_path / "wd", with_skill=False, server="local")
    assert not (wd / ".claude" / "skills").exists()
    assert (wd / ".claude" / "settings.json").exists()


def test_workdir_with_skill_keeps_everything_but_heavy_and_local_dirs(tmp_path):
    wd = prepare_workdir(fake_p2(tmp_path), tmp_path / "wd", with_skill=True, server="local")
    assert (wd / ".claude" / "skills" / "consultar" / "SKILL.md").exists()
    assert (wd / ".claude" / "settings.json").exists()
    for nome in (".git", ".venv", "traces"):
        assert not (wd / nome).exists()


def test_workdir_mcp_config_has_only_the_p2_server(tmp_path):
    wd = prepare_workdir(fake_p2(tmp_path), tmp_path / "wd", with_skill=True, server="local")
    cfg = json.loads((wd / runner.MCP_CONFIG_NAME).read_text())
    assert list(cfg["mcpServers"]) == ["taxlaw"]
    assert cfg["mcpServers"]["taxlaw"]["args"] == ["-m", "taxlaw.server"]


def test_remote_mcp_config_keeps_secrets_out_of_the_file(tmp_path, monkeypatch):
    monkeypatch.setenv("TAXLAW_REMOTE_URL", "https://exemplo.invalid/mcp")
    monkeypatch.setenv("TAXLAW_HTTP_TOKEN", "segredo-de-teste")
    wd = prepare_workdir(fake_p2(tmp_path), tmp_path / "wd", with_skill=True, server="remoto")
    texto = (wd / runner.MCP_CONFIG_NAME).read_text()
    assert "segredo-de-teste" not in texto and "exemplo.invalid" not in texto
    cfg = json.loads(texto)["mcpServers"]["taxlaw-remoto"]
    assert cfg["url"] == "${TAXLAW_REMOTE_URL}"
    assert cfg["headers"]["Authorization"] == "Bearer ${TAXLAW_HTTP_TOKEN}"


def test_existing_workdir_is_refused(tmp_path):
    p2 = fake_p2(tmp_path)
    prepare_workdir(p2, tmp_path / "wd", with_skill=True, server="local")
    with pytest.raises(FileExistsError):
        prepare_workdir(p2, tmp_path / "wd", with_skill=True, server="local")


# --- pergunta ------------------------------------------------------------------------

def test_placeholders_become_valid_synthetic_numbers():
    q, ids = substitute_placeholders("cpf {CPF}, cnpj {CNPJ}, outro {CPF}", random.Random(1))
    assert "{" not in q and len(ids) == 3
    assert is_valid_cpf(ids[0]) and is_valid_cnpj(ids[1]) and is_valid_cpf(ids[2])
    assert ids[0] != ids[2] and all(i in q for i in ids)


def test_placeholders_depend_only_on_the_seed():
    a = substitute_placeholders("{CPF}", random.Random(3))
    assert a == substitute_placeholders("{CPF}", random.Random(3))
    assert a != substitute_placeholders("{CPF}", random.Random(4))


def test_prompt_states_the_reference_date():
    # Achado 4 da amostra real: sem isso o modelo usa a data do dia da rodada.
    prompt, ids = build_prompt(make_case(), random.Random(1))
    assert prompt.startswith("Qual o percentual do IBS?") and ids == []
    assert "Data de referência: 2026-11-11." in prompt


# --- run_case -----------------------------------------------------------------------

def test_run_case_writes_a_valid_trace_and_charges_the_guard(tmp_path):
    guard = BudgetGuard(1.0)
    run = FakeRun()
    path = _run(tmp_path, run, guard=guard)
    t = load_trace(path)
    assert validate_trace(t) == [] and t["status"] == "ok", t["errors"]
    assert t["conditions"] == {"skill": True, "hook": True, "server": "local",
                               "p2_tag": "step-16",
                               "corpus_version": runner.corpus_version(tmp_path / "wd")}
    assert guard.spent == pytest.approx(0.00566555)
    argv, kw = run.calls[0]
    assert kw["cwd"] == tmp_path / "wd" and kw["timeout"] == runner.DEFAULT_TIMEOUT_S
    assert "Data de referência: 2026-11-11." in kw["input"]
    assert t["question"] == kw["input"]


def test_question_goes_by_stdin_not_by_argv(tmp_path):
    # --allowedTools aceita varios valores: uma pergunta no fim do argv viraria ferramenta.
    run = FakeRun()
    _run(tmp_path, run)
    argv, kw = run.calls[0]
    assert not any("IBS" in a for a in argv)


def test_synthetic_numbers_go_to_the_trace_not_to_the_case(tmp_path):
    case = make_case(question="meu cpf {CPF}", hypothesis=["H12"])
    t = load_trace(_run(tmp_path, FakeRun(), case=case))
    assert len(t["synthetic_ids"]) == 1 and t["synthetic_ids"][0] in t["question"]
    assert case["question"] == "meu cpf {CPF}"


def test_hook_condition_is_false_for_remote(tmp_path, monkeypatch):
    monkeypatch.setenv("TAXLAW_REMOTE_URL", "https://exemplo.invalid/mcp")
    monkeypatch.setenv("TAXLAW_HTTP_TOKEN", "x")
    wd = prepare_workdir(fake_p2(tmp_path), tmp_path / "wd", with_skill=True, server="remoto")
    t = load_trace(_run(tmp_path, FakeRun(), workdir=wd, server="remoto"))
    assert t["conditions"]["hook"] is False and t["conditions"]["server"] == "remoto"


def test_skill_condition_follows_the_workdir(tmp_path):
    wd = prepare_workdir(fake_p2(tmp_path), tmp_path / "wd", with_skill=False, server="local")
    t = load_trace(_run(tmp_path, FakeRun(), workdir=wd))
    assert t["conditions"]["skill"] is False


def test_budget_is_raised_after_the_trace_is_written(tmp_path):
    guard = BudgetGuard(0.005)
    with pytest.raises(BudgetExceeded):
        _run(tmp_path, FakeRun(), guard=guard)
    assert len(list((tmp_path / "traces").glob("*.json"))) == 1


def test_remote_without_env_is_refused_before_running(tmp_path, monkeypatch):
    monkeypatch.delenv("TAXLAW_REMOTE_URL", raising=False)
    monkeypatch.setenv("TAXLAW_HTTP_TOKEN", "segredo-de-teste")
    run = FakeRun()
    with pytest.raises(RemoteNotConfigured) as exc:
        _run(tmp_path, run, workdir=tmp_path, server="remoto")
    assert run.calls == []
    assert "TAXLAW_REMOTE_URL" in str(exc.value) and "segredo-de-teste" not in str(exc.value)


def test_timeout_becomes_an_error_trace_with_what_was_read(tmp_path):
    corte = "\n".join(STREAM_OK.splitlines()[:-1])
    t = load_trace(_run(tmp_path, FakeRun(stdout=corte, raise_timeout=True)))
    assert t["status"] == "erro" and any("tempo" in e for e in t["errors"])
    assert len(t["events"]) == 3


def test_timeout_with_bytes_output_is_decoded(tmp_path):
    corte = "\n".join(STREAM_OK.splitlines()[:-1]).encode()
    t = load_trace(_run(tmp_path, FakeRun(stdout=corte, raise_timeout=True)))
    assert t["status"] == "erro" and len(t["events"]) == 3


def test_timeout_with_invalid_utf8_bytes_is_an_error_not_a_crash(tmp_path):
    corte = b"\x80\x81 lixo\n" + "\n".join(STREAM_OK.splitlines()[:-1]).encode()
    t = load_trace(_run(tmp_path, FakeRun(stdout=corte, raise_timeout=True)))
    assert t["status"] == "erro" and len(t["events"]) == 3


def test_remote_run_that_used_the_local_server_is_an_error(tmp_path, monkeypatch):
    monkeypatch.setenv("TAXLAW_REMOTE_URL", "https://exemplo.invalid/mcp")
    monkeypatch.setenv("TAXLAW_HTTP_TOKEN", "x")
    wd = prepare_workdir(fake_p2(tmp_path), tmp_path / "wd", with_skill=True, server="remoto")
    t = load_trace(_run(tmp_path, FakeRun(), workdir=wd, server="remoto"))
    assert t["status"] == "erro" and any("taxlaw-remoto" in e for e in t["errors"])


def test_nonzero_exit_turns_an_ok_stream_into_error(tmp_path):
    t = load_trace(_run(tmp_path, FakeRun(returncode=1)))
    assert t["status"] == "erro" and any("saida 1" in e for e in t["errors"])


def test_nonzero_exit_does_not_hide_a_limit(tmp_path):
    linhas = STREAM_OK.splitlines()
    res = json.loads(linhas[-1])
    res.update(subtype="error_max_budget_usd", is_error=True)
    stream = "\n".join(linhas[:-1] + [json.dumps(res)])
    t = load_trace(_run(tmp_path, FakeRun(stdout=stream, returncode=1)))
    assert t["status"] == "estourou_limite"


# --- repeticao (decisao 9 de D2) ------------------------------------------------------

class Sequence(FakeRun):
    def __init__(self, outputs):
        super().__init__()
        self.outputs = list(outputs)

    def __call__(self, argv, **kw):
        self.stdout = self.outputs.pop(0)
        return super().__call__(argv, **kw)


def _retry(tmp_path, run):
    wd = prepare_workdir(fake_p2(tmp_path), tmp_path / "wd", with_skill=True, server="local")
    return run_with_retries(make_case(), model="m", server="local", workdir=wd,
                            p2_tag="step-16", traces_dir=tmp_path / "traces",
                            guard=BudgetGuard(1.0), max_budget_usd=0.2,
                            rng=random.Random(7), run=run)


def test_error_is_retried_until_ok(tmp_path):
    r = _retry(tmp_path, Sequence(["lixo", STREAM_OK]))
    assert len(r.paths) == 2 and r.status == "ok" and not r.investigate


def test_three_errors_in_a_row_stop_and_mark_for_investigation(tmp_path):
    run = Sequence(["lixo", "lixo", "lixo", STREAM_OK])
    r = _retry(tmp_path, run)
    assert len(run.calls) == 3 and r.status == "erro" and r.investigate


def test_limit_is_not_retried(tmp_path):
    linhas = STREAM_OK.splitlines()
    res = json.loads(linhas[-1])
    res.update(subtype="error_max_turns", is_error=True)
    run = Sequence(["\n".join(linhas[:-1] + [json.dumps(res)]), STREAM_OK])
    r = _retry(tmp_path, run)
    assert len(run.calls) == 1 and r.status == "estourou_limite" and not r.investigate
