"""Adaptador do stream-json do Claude Code (Tarefa 12, passo 25).

As fixtures vem de uma execucao real (2026-11-11), reduzidas aos campos que o
adaptador le e sem session_id, caminhos locais nem servers da conta do usuario.
"""
import json
from pathlib import Path

import pytest

from evals.adapters.claude_code import parse_stream
from evals.checks import check_c1
from evals.trace import validate_trace

FIX = Path(__file__).parent / "fixtures"
# A amostra de stream_ok.jsonl foi capturada sem --include-hook-events: nela o hook
# nao aparece, entao as condicoes declaram hook falso. stream_hook.jsonl tem o hook.
COND = {"skill": True, "hook": False, "server": "local",
        "p2_tag": "step-16", "corpus_version": "x"}
COND_HOOK = {**COND, "hook": True}
TAXLAW = {"mcp__taxlaw__buscar_dispositivos", "mcp__taxlaw__obter_dispositivo"}
ALLOWED_TOOLS = TAXLAW | {"Skill", "ToolSearch"}
ALLOWED_SERVERS = {"taxlaw"}


def _lines(nome):
    return (FIX / nome).read_text(encoding="utf-8").splitlines()


def _parse(lines, **over):
    kw = dict(case_id="c01", question="pergunta?", conditions=COND, trace_id="c01-test0001",
              allowed_tools=ALLOWED_TOOLS, allowed_servers=ALLOWED_SERVERS)
    kw.update(over)
    return parse_stream(lines, **kw)


def _with_init(**changes):
    linhas = _lines("stream_ok.jsonl")
    init = json.loads(linhas[0])
    init.update(changes)
    return [json.dumps(init)] + linhas[1:]


def _with_result(**changes):
    linhas = _lines("stream_ok.jsonl")
    res = json.loads(linhas[-1])
    res.update(changes)
    return linhas[:-1] + [json.dumps(res)]


# --- a execucao real ---------------------------------------------------------

def test_real_stream_becomes_a_valid_ok_trace():
    t = _parse(_lines("stream_ok.jsonl"))
    assert validate_trace(t) == []
    assert t["status"] == "ok" and t["errors"] == []
    assert t["model"] == "claude-haiku-5-5"
    assert t["source"]["harness"] == "claude-code" and t["source"]["version"]
    assert t["final_answer"].startswith("**Não consigo informar o percentual do IBS")


def test_events_keep_only_p2_tools_with_parsed_results():
    t = _parse(_lines("stream_ok.jsonl"))
    assert [e["tool"] for e in t["events"]] == ["mcp__taxlaw__buscar_dispositivos"] * 2
    for e in t["events"]:
        assert isinstance(e["args"], dict) and e["args"]["data_referencia"] == "2026-11-11"
        assert isinstance(e["result_raw"], dict) and e["result_raw"]["encontrado"] is True
        assert e["is_error"] is False


def test_other_tools_are_recorded_apart_without_their_results():
    t = _parse(_lines("stream_ok.jsonl"))
    assert [o["tool"] for o in t["other_tools"]] == ["Skill", "ToolSearch"]
    assert t["other_tools"][0]["args"]["skill"] == "consultar-reforma-tributaria"
    assert all(set(o) == {"tool", "args"} for o in t["other_tools"])


def test_skill_text_does_not_count_as_backing_for_c1():
    # O texto da skill cita CF.art156-A.par1; as ferramentas do P2 nao devolveram esse id.
    t = _parse(_lines("stream_ok.jsonl"))
    r = check_c1("Base: CF.art156-A.par1.", t["events"], [])
    assert r.verdict == "fail" and "CF.art156-A.par1" in r.reasons[0]


def test_usage_sums_cache_tokens_into_input():
    u = _parse(_lines("stream_ok.jsonl"))["usage"]
    assert u["input_tokens"] == 10 + 20272 + 174262
    assert (u["uncached_input_tokens"], u["cache_creation_input_tokens"],
            u["cache_read_input_tokens"]) == (10, 20272, 174262)
    assert u["output_tokens"] == 1595
    assert u["cost_usd"] == pytest.approx(0.00659552)
    assert u["duration_ms"] == 21330


def test_source_records_effective_tools_and_servers():
    s = _parse(_lines("stream_ok.jsonl"))["source"]
    assert set(s["tools"]) == ALLOWED_TOOLS and s["mcp_servers"] == ["taxlaw"]


def test_synthetic_ids_are_recorded_only_when_given():
    assert "synthetic_ids" not in _parse(_lines("stream_ok.jsonl"))
    t = _parse(_lines("stream_ok.jsonl"), synthetic_ids=["x"])
    assert t["synthetic_ids"] == ["x"]


# --- isolamento (achado 1 da amostra real) -------------------------------------

def test_extra_tool_in_init_is_an_error_naming_the_tool():
    t = _parse(_with_init(tools=sorted(ALLOWED_TOOLS) + ["Bash"]))
    assert t["status"] == "erro" and validate_trace(t) == []
    assert any("Bash" in e for e in t["errors"])


def test_extra_mcp_server_in_init_is_an_error_naming_the_server():
    servers = [{"name": "taxlaw", "status": "connected"}, {"name": "outro", "status": "connected"}]
    t = _parse(_with_init(mcp_servers=servers))
    assert t["status"] == "erro" and any("outro" in e for e in t["errors"])


def test_missing_init_is_an_error():
    t = _parse(_lines("stream_ok.jsonl")[1:])
    assert t["status"] == "erro" and any("init" in e for e in t["errors"])


def test_taxlaw_server_not_connected_is_an_error():
    t = _parse(_with_init(mcp_servers=[{"name": "taxlaw", "status": "failed"}]))
    assert t["status"] == "erro" and any("taxlaw" in e for e in t["errors"])


# --- falhas e limites (decisao 8 de D2) ---------------------------------------

def test_truncated_stream_is_an_error_with_partial_events():
    t = _parse(_lines("stream_truncated.jsonl"))
    assert t["status"] == "erro" and validate_trace(t) == []
    assert len(t["events"]) == 2 and t["final_answer"] == ""


def test_garbage_lines_do_not_crash():
    t = _parse(["nao e json", "{", ""])
    assert t["status"] == "erro" and validate_trace(t) == []


def test_one_bad_line_in_a_complete_stream_is_an_error():
    linhas = _lines("stream_ok.jsonl")
    t = _parse(linhas[:5] + ["{quebrada"] + linhas[5:])
    assert t["status"] == "erro" and any("JSON" in e for e in t["errors"])


def test_stream_cut_cleanly_before_result_is_an_error():
    t = _parse(_lines("stream_ok.jsonl")[:-1])
    assert t["status"] == "erro" and any("result" in e for e in t["errors"])


@pytest.mark.parametrize("linha", ["[]", "42", '"texto"', "null"])
def test_json_that_is_not_an_object_is_a_bad_line_not_a_crash(linha):
    linhas = _lines("stream_ok.jsonl")
    t = _parse(linhas[:5] + [linha] + linhas[5:])
    assert t["status"] == "erro" and validate_trace(t) == []


def test_unknown_event_types_are_ignored():
    linhas = _lines("stream_ok.jsonl")
    t = _parse(linhas[:1] + ['{"type": "algo_novo", "x": 1}'] + linhas[1:])
    assert t["status"] == "ok"


@pytest.mark.parametrize("subtype", ["error_max_budget_usd", "error_max_turns"])
def test_hitting_a_limit_is_estourou_limite(subtype):
    t = _parse(_with_result(subtype=subtype, is_error=True, result=""))
    assert t["status"] == "estourou_limite" and validate_trace(t) == []
    assert any(subtype in e for e in t["errors"])


def test_other_result_error_is_erro():
    t = _parse(_with_result(subtype="error_during_execution", is_error=True))
    assert t["status"] == "erro"


def test_tool_use_without_result_is_an_error():
    linhas = _lines("stream_ok.jsonl")
    sem_resultado = [l for l in linhas if "toolu_0138GkR2i14EomwhNf1D6BBT" not in l
                     or '"tool_use"' in l]
    t = _parse(sem_resultado)
    assert t["status"] == "erro" and validate_trace(t) == []


# --- formas do resultado de ferramenta (achado 8) ------------------------------

def _single_call(content, is_error=False):
    init = json.loads(_lines("stream_ok.jsonl")[0])
    return [json.dumps(init),
            json.dumps({"type": "assistant", "message": {"content": [
                {"type": "tool_use", "id": "t1", "name": "mcp__taxlaw__obter_dispositivo",
                 "input": {"id": "CF.art156-A"}}]}}),
            json.dumps({"type": "user", "message": {"content": [
                {"type": "tool_result", "tool_use_id": "t1", "content": content,
                 "is_error": is_error}]}}),
            json.dumps({"type": "result", "subtype": "success", "is_error": False,
                        "result": "ok", "total_cost_usd": 0.0, "duration_ms": 1, "usage": {}})]


def test_result_as_list_of_text_blocks_is_joined_and_parsed():
    t = _parse(_single_call([{"type": "text", "text": '{"encontrado":'},
                             {"type": "text", "text": " false}"}]))
    assert t["events"][0]["result_raw"] == {"encontrado": False}


def test_result_that_is_not_json_stays_as_text():
    t = _parse(_single_call("falha ao consultar"))
    assert t["events"][0]["result_raw"] == "falha ao consultar"


def test_tool_error_is_recorded_but_does_not_fail_the_trace():
    t = _parse(_single_call("argumento invalido", is_error=True))
    assert t["status"] == "ok" and t["events"][0]["is_error"] is True


def test_remote_server_tools_count_as_p2_calls():
    linhas = [l.replace("mcp__taxlaw__", "mcp__taxlaw-remoto__") for l in _single_call("{}")]
    init = json.loads(linhas[0])
    init["tools"] = ["Skill", "ToolSearch", "mcp__taxlaw-remoto__obter_dispositivo"]
    init["mcp_servers"] = [{"name": "taxlaw-remoto", "status": "connected"}]
    t = _parse([json.dumps(init)] + linhas[1:],
               allowed_tools=set(init["tools"]), allowed_servers={"taxlaw-remoto"})
    assert t["status"] == "ok", t["errors"]
    assert [e["tool"] for e in t["events"]] == ["mcp__taxlaw-remoto__obter_dispositivo"]


def test_every_allowed_server_must_be_connected():
    t = _parse(_lines("stream_ok.jsonl"), allowed_servers={"taxlaw", "taxlaw-remoto"})
    assert t["status"] == "erro" and any("taxlaw-remoto" in e for e in t["errors"])


# --- o hook (passo 26, amostra com --include-hook-events) -----------------------

def test_hook_run_is_recorded_on_each_p2_call():
    t = _parse(_lines("stream_hook.jsonl"), conditions=COND_HOOK)
    assert t["status"] == "ok", t["errors"]
    assert [e["tool"] for e in t["events"]] == ["mcp__taxlaw__buscar_dispositivos",
                                                "mcp__taxlaw__obter_dispositivo",
                                                "mcp__taxlaw__obter_dispositivo"]
    assert all(e["hook"] == {"outcome": "success", "exit_code": 0} for e in t["events"])
    assert [h["name"] for h in t["hooks"]] == [
        "PreToolUse:mcp__taxlaw__buscar_dispositivos",
        "PreToolUse:mcp__taxlaw__obter_dispositivo",
        "PreToolUse:mcp__taxlaw__obter_dispositivo"]


def test_reference_date_from_the_prompt_reaches_the_tools():
    t = _parse(_lines("stream_hook.jsonl"), conditions=COND_HOOK)
    assert {e["args"]["data_referencia"] for e in t["events"]} == {"2030-01-01"}


def test_declared_hook_that_did_not_run_is_an_error():
    t = _parse(_lines("stream_ok.jsonl"), conditions=COND_HOOK)
    assert t["status"] == "erro" and any("hook" in e for e in t["errors"])


def test_missing_hook_response_for_one_call_is_an_error():
    linhas = _lines("stream_hook.jsonl")
    i = max(n for n, l in enumerate(linhas) if '"hook_response"' in l)
    t = _parse(linhas[:i] + linhas[i + 1:], conditions=COND_HOOK)
    assert t["status"] == "erro" and any("1 chamada" in e for e in t["errors"])


def test_hook_is_paired_by_tool_name_in_order():
    linhas = _lines("stream_hook.jsonl")
    i = min(n for n, l in enumerate(linhas) if '"hook_response"' in l and "buscar" in l)
    resp = json.loads(linhas[i])
    resp.update(outcome="blocked", exit_code=2)
    t = _parse(linhas[:i] + [json.dumps(resp)] + linhas[i + 1:], conditions=COND_HOOK)
    assert t["events"][0]["hook"] == {"outcome": "blocked", "exit_code": 2}
    assert t["events"][1]["hook"]["exit_code"] == 0


def test_hook_on_another_tool_does_not_cover_a_p2_call():
    linhas = [l.replace("PreToolUse:mcp__taxlaw__obter_dispositivo", "PreToolUse:WebSearch")
              for l in _lines("stream_hook.jsonl")]
    t = _parse(linhas, conditions=COND_HOOK)
    assert t["status"] == "erro" and any("2 chamada" in e for e in t["errors"])


def test_only_a_pre_tool_use_hook_covers_a_p2_call():
    # O hook do P2 bloqueia CPF antes da chamada; um hook depois dela nao protege nada.
    linhas = _lines("stream_hook.jsonl")
    i = max(n for n, l in enumerate(linhas) if '"hook_response"' in l)
    resp = json.loads(linhas[i])
    resp.update(hook_event="PostToolUse",
                hook_name=resp["hook_name"].replace("PreToolUse", "PostToolUse"))
    t = _parse(linhas[:i] + [json.dumps(resp)] + linhas[i + 1:], conditions=COND_HOOK)
    assert t["status"] == "erro" and any("1 chamada" in e for e in t["errors"])
    assert t["hooks"][-1]["event"] == "PostToolUse"


def test_hook_not_declared_is_not_required():
    t = _parse(_lines("stream_ok.jsonl"))
    assert t["status"] == "ok" and all(e["hook"] is None for e in t["events"])


def test_allowed_lists_are_required():
    with pytest.raises(TypeError):
        parse_stream(_lines("stream_ok.jsonl"), case_id="c01", question="q",
                     conditions=COND, trace_id="c01-x")
