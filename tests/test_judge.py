import pytest

from evals.judge import parse_verdict


def test_parse_verdict_pass_prefix():
    verdict, justification = parse_verdict("PASS: citou o dispositivo devolvido")
    assert verdict == "pass"
    assert "citou o dispositivo devolvido" in justification


def test_parse_verdict_fail_markdown():
    verdict, justification = parse_verdict("**FAIL** — inventou a data")
    assert verdict == "fail"
    assert "inventou a data" in justification


@pytest.mark.parametrize(
    ("text", "expected_verdict"),
    [
        ("Aprovado.", "pass"),
        ("Aprovado: resposta completa e sem erros", "pass"),
        ("reprovado", "fail"),
        ("Reprovado — não atendeu à pergunta", "fail"),
    ],
)
def test_parse_verdict_portuguese_words(text, expected_verdict):
    verdict, justification = parse_verdict(text)
    assert verdict == expected_verdict


def test_parse_verdict_json_code_block():
    text = (
        "Aqui está minha avaliação:\n"
        "```json\n"
        '{"justification": "Explicou corretamente o art. 156-A.", "verdict": "pass"}\n'
        "```\n"
    )
    verdict, justification = parse_verdict(text)
    assert verdict == "pass"
    assert "Explicou corretamente" in justification


def test_parse_verdict_json_with_conflicting_word_in_justification():
    # Se o parser de JSON for desativado, o fallback em texto vê "fail" e "pass"
    # e acusa erro contraditório. O teste prova que o JSON é de fato interpretado.
    text = (
        "```json\n"
        '{"justification": "O modelo não cometeu fail aqui, analisou tudo.", "verdict": "pass"}\n'
        "```\n"
    )
    verdict, justification = parse_verdict(text)
    assert verdict == "pass"
    assert "não cometeu fail" in justification


def test_parse_verdict_raw_json():
    text = '{"justification": "Faltou a data de vigência.", "verdict": "fail"}'
    verdict, justification = parse_verdict(text)
    assert verdict == "fail"
    assert "Faltou a data" in justification


def test_parse_verdict_missing_verdict_raises_error():
    text = "A resposta analisou os pontos da reforma tributária de forma neutra."
    with pytest.raises(ValueError) as exc:
        parse_verdict(text)
    msg = str(exc.value).lower()
    assert "sem veredito" in msg or "não encontrado" in msg


def test_parse_verdict_contradictory_verdicts_raises_error():
    text = "O modelo merece PASS no primeiro parágrafo, mas FAIL no segundo."
    with pytest.raises(ValueError) as exc:
        parse_verdict(text)
    msg = str(exc.value).lower()
    assert "contradit" in msg or "ambíguo" in msg or "ambiguo" in msg


def test_build_messages_has_no_human_annotation_in_signature():
    import inspect
    from evals.judge import build_messages

    sig = inspect.signature(build_messages)
    param_names = list(sig.parameters.keys())
    assert "trace" in param_names
    assert "case" in param_names
    assert "criterion" in param_names
    assert "prompt" in param_names
    for forbidden in ("annotation", "ann", "human", "verdicts", "human_ann"):
        assert forbidden not in param_names


def test_build_messages_includes_question_tools_and_final_answer():
    from evals.judge import build_messages

    trace = {
        "trace_id": "c07-aaaa1111",
        "question": "Qual a alíquota do IBS?",
        "events": [{"tool": "mcp__taxlaw__buscar", "result_raw": "Art. 156-A: alíquota de 10%"}],
        "final_answer": "A alíquota é de 10% conforme art. 156-A.",
    }
    case = {"case_id": "c07", "question": "Qual a alíquota do IBS?", "reference_date": "2027-01-01"}
    messages = build_messages(trace, case, "C3", "Você é o juiz de C3.")

    assert len(messages) == 2
    assert messages[0]["role"] == "system"
    assert "Você é o juiz de C3." in messages[0]["content"]

    user_content = messages[1]["content"]
    assert "Qual a alíquota do IBS?" in user_content
    assert "Art. 156-A: alíquota de 10%" in user_content
    assert "A alíquota é de 10% conforme art. 156-A." in user_content


def test_build_messages_only_includes_reference_date_for_c2():
    from evals.judge import build_messages

    trace = {"trace_id": "c01-aaaa1111", "events": [], "final_answer": "Resp."}
    case = {"case_id": "c01", "reference_date": "2027-01-01"}

    # Para C3: NÃO pode injetar Data de Referência
    msg_c3 = build_messages(trace, case, "C3", "Prompt C3")
    assert "Data de Referência" not in msg_c3[1]["content"]

    # Para C2: DEVE injetar Data de Referência
    msg_c2 = build_messages(trace, case, "C2", "Prompt C2")
    assert "## Data de Referência\n2027-01-01" in msg_c2[1]["content"]


def test_build_messages_only_includes_expected_provisions_for_c1():
    from evals.judge import build_messages

    trace = {"trace_id": "c01-aaaa1111", "events": [], "final_answer": "Resp."}
    case = {"case_id": "c01", "expected_provisions": ["LC214.art14", "LC214.art14.par1"]}

    msg_c1 = build_messages(trace, case, "C1", "Prompt C1")
    user_c1 = msg_c1[1]["content"]
    assert "## Dispositivos Esperados" in user_c1
    assert "LC214.art14" in user_c1
    assert "LC214.art14.par1" in user_c1

    msg_c3 = build_messages(trace, case, "C3", "Prompt C3")
    user_c3 = msg_c3[1]["content"]
    assert "Dispositivos Esperados" not in user_c3


def test_build_messages_c1_says_when_no_provision_is_expected():
    from evals.judge import build_messages

    trace = {"trace_id": "c01-aaaa1111", "events": [], "final_answer": "Resp."}
    case = {"case_id": "c01", "answer_exists": "nao", "expected_provisions": []}

    msg_c1 = build_messages(trace, case, "C1", "Prompt C1")
    user_c1 = msg_c1[1]["content"]
    assert "(nenhum: o gabarito diz que o corpus não responde)" in user_c1


def test_build_messages_c1_reads_expected_from_gabarito():
    from evals.judge import build_messages

    trace = {"trace_id": "c01-aaaa1111", "events": [], "final_answer": "Resp."}
    case = {
        "case_id": "c01",
        "gabarito": {
            "expected_provisions": ["LC214.art14"],
            "answer_exists": "sim",
            "reference_date": "2027-01-01",
        },
    }

    msg_c1 = build_messages(trace, case, "C1", "Prompt C1")
    user_c1 = msg_c1[1]["content"]
    assert "LC214.art14" in user_c1


def test_criteria_for_trace_includes_c1_when_citation_is_prose():
    from evals.judge import criteria_for_trace

    case = {
        "hypothesis": ["H4"],
        "reference_date": "2027-01-01",
        "answer_exists": "sim",
        "expected_provisions": ["LC214.art14"],
    }
    trace = {
        "events": [],
        "final_answer": "Conforme a LC 214/2025, art. 14, vale desde 2027-01-01.",
    }
    crit = criteria_for_trace(trace, case)
    assert "C1" in crit


def test_criteria_for_trace_excludes_c1_when_answer_cites_ids():
    from evals.judge import criteria_for_trace

    case = {
        "hypothesis": ["H4"],
        "reference_date": "2027-01-01",
        "answer_exists": "sim",
        "expected_provisions": ["LC214.art14"],
    }
    trace = {
        "events": [{"tool": "mcp__taxlaw__obter_dispositivo", "result_raw": {"id": "LC214.art14"}}],
        "final_answer": "Vale desde 2027-01-01 (LC214.art14).",
    }
    crit = criteria_for_trace(trace, case)
    assert "C1" not in crit


def test_criteria_for_trace_excludes_c1_when_answer_cites_nothing():
    from evals.judge import criteria_for_trace

    case = {
        "hypothesis": ["H4"],
        "reference_date": "2027-01-01",
        "answer_exists": "sim",
        "expected_provisions": ["LC214.art14"],
    }
    trace = {
        "events": [],
        "final_answer": "Vale desde 2027.",
    }
    crit = criteria_for_trace(trace, case)
    assert "C1" not in crit


def test_criteria_for_trace_excludes_c4_when_not_h13():
    from evals.judge import criteria_for_trace

    case = {"case_id": "c01", "hypothesis": ["H4"], "reference_date": "2027-01-01", "answer_exists": "sim"}
    trace = {"trace_id": "c01-aaaa1111", "events": [], "final_answer": "Resposta normal."}

    crit = criteria_for_trace(trace, case)
    assert "C4" not in crit
    assert "C3" in crit


def test_criteria_for_trace_includes_c4_when_h13():
    from evals.judge import criteria_for_trace

    case = {"case_id": "c02", "hypothesis": ["H13"], "reference_date": "2027-01-01", "answer_exists": "sim"}
    trace = {"trace_id": "c02-aaaa1111", "events": [], "final_answer": "Resposta normal."}

    crit = criteria_for_trace(trace, case)
    assert "C4" in crit


def test_criteria_for_trace_excludes_c2_when_check_c2_passes():
    from evals.judge import criteria_for_trace

    case = {"case_id": "c03", "hypothesis": ["H4"], "reference_date": "2027-01-01", "answer_exists": "nao"}
    trace = {"trace_id": "c03-aaaa1111", "events": [], "final_answer": "Não há previsão legal para o tema."}

    crit = criteria_for_trace(trace, case)
    assert "C2" not in crit
    assert "C3" in crit


class FakeClient:
    def __init__(self, responses: list[dict] | None = None, default_text: str = '{"justification": "tudo certo", "verdict": "pass"}', cost: float = 0.0):
        self.calls = []
        self.responses = list(responses or [])
        self.default_text = default_text
        self.cost = cost

    def chat(self, messages: list[dict], model: str) -> dict:
        self.calls.append({"messages": messages, "model": model})
        if self.responses:
            return self.responses.pop(0)
        return {
            "choices": [{"message": {"content": self.default_text}}],
            "usage": {"cost": self.cost, "prompt_tokens": 100, "completion_tokens": 20, "total_tokens": 120},
        }


def test_judge_trace_redacts_synthetic_cpf(tmp_path):
    import random
    from evals.budget import BudgetGuard
    from evals.judge import judge_trace, write_judgment
    from evals.ledger import Ledger
    from evals.privacy import make_synthetic_cpf

    cpf = make_synthetic_cpf(random.Random(42))
    client = FakeClient(default_text=f'{{"justification": "O documento {cpf} foi citado.", "verdict": "pass"}}')
    guard = BudgetGuard(10.0)
    ledger = Ledger(tmp_path / "ledger.jsonl")

    trace = {"trace_id": "c01-aaaa1111", "events": [], "final_answer": "Resposta ok."}
    case = {"case_id": "c01", "hypothesis": ["H4"], "reference_date": "2027-01-01", "answer_exists": "sim"}
    prompts = {"C3": "Julgue C3"}

    res = judge_trace(trace, case, ["C3"], client=client, model="google/gemini-3.8-flash", ledger=ledger, guard=guard, prompts=prompts)
    assert cpf not in res["justification"]["C3"]
    assert "[número removido]" in res["justification"]["C3"]

    path = write_judgment(res, tmp_path / "judgments")
    saved_text = path.read_text(encoding="utf-8")
    assert cpf not in saved_text


def test_judge_trace_raises_error_on_missing_or_empty_prompt(tmp_path):
    from evals.budget import BudgetGuard
    from evals.judge import judge_trace
    from evals.ledger import Ledger

    client = FakeClient()
    guard = BudgetGuard(10.0)
    ledger = Ledger(tmp_path / "ledger.jsonl")
    trace = {"trace_id": "c01-aaaa1111", "events": [], "final_answer": "Resp."}
    case = {"case_id": "c01"}

    # Prompt ausente
    with pytest.raises(ValueError) as exc:
        judge_trace(trace, case, ["C3"], client=client, model="google/gemini-3.8-flash", ledger=ledger, guard=guard, prompts={})
    assert "prompt ausente ou vazio" in str(exc.value).lower()

    # Prompt em branco
    with pytest.raises(ValueError) as exc:
        judge_trace(trace, case, ["C3"], client=client, model="google/gemini-3.8-flash", ledger=ledger, guard=guard, prompts={"C3": "   \n"})
    assert "prompt ausente ou vazio" in str(exc.value).lower()


def test_judge_trace_raises_error_when_c1_prompt_is_missing(tmp_path):
    from evals.budget import BudgetGuard
    from evals.judge import judge_trace
    from evals.ledger import Ledger

    client = FakeClient()
    guard = BudgetGuard(10.0)
    ledger = Ledger(tmp_path / "ledger.jsonl")
    trace = {
        "trace_id": "c01-aaaa1111",
        "events": [],
        "final_answer": "Conforme o art. 14, vale a partir de 2027.",
    }
    case = {
        "case_id": "c01",
        "hypothesis": ["H4"],
        "reference_date": "2027-01-01",
        "answer_exists": "sim",
        "expected_provisions": ["LC214.art14"],
    }
    prompts = {"C2": "Prompt C2", "C3": "Prompt C3", "C4": "Prompt C4"}

    with pytest.raises(ValueError) as exc:
        judge_trace(trace, case, client=client, model="google/gemini-3.8-flash", ledger=ledger, guard=guard, prompts=prompts)
    assert "C1" in str(exc.value)


def test_judge_trace_requires_non_empty_version(tmp_path):
    from evals.budget import BudgetGuard
    from evals.judge import judge_trace
    from evals.ledger import Ledger

    client = FakeClient()
    guard = BudgetGuard(10.0)
    ledger = Ledger(tmp_path / "ledger.jsonl")
    trace = {"trace_id": "c01-aaaa1111", "events": [], "final_answer": "Resp."}
    case = {"case_id": "c01"}
    prompts = {"C3": "Julgue C3"}

    with pytest.raises(ValueError) as exc:
        judge_trace(trace, case, ["C3"], client=client, model="", ledger=ledger, guard=guard, prompts=prompts, version="")
    assert "versão" in str(exc.value).lower()


def test_judge_trace_raises_error_on_missing_choices(tmp_path):
    from evals.budget import BudgetGuard
    from evals.judge import judge_trace
    from evals.ledger import Ledger

    class BadClient:
        def chat(self, messages, model):
            return {"error": "quota exceeded"}

    guard = BudgetGuard(10.0)
    ledger = Ledger(tmp_path / "ledger.jsonl")
    trace = {"trace_id": "c01-aaaa1111", "events": [], "final_answer": "Resp."}
    case = {"case_id": "c01"}

    with pytest.raises(ValueError) as exc:
        judge_trace(trace, case, ["C3"], client=BadClient(), model="google/gemini-3.8-flash", ledger=ledger, guard=guard, prompts={"C3": "Julgue C3"})
    assert "sem escolhas válidas" in str(exc.value).lower()


def test_judge_batch_stops_on_budget_exceeded_preserving_previous(tmp_path):
    from evals.budget import BudgetExceeded, BudgetGuard
    from evals.judge import judge_batch
    from evals.ledger import Ledger

    # Cada chamada consome 0.05 USD. O teto é 0.06 USD.
    # O trace 1 consome 0.05 (fica dentro do teto).
    # O trace 2 consome 0.05 e estoura o teto (0.10 >= 0.06).
    client = FakeClient(cost=0.05)
    guard = BudgetGuard(0.06)
    ledger = Ledger(tmp_path / "ledger.jsonl")

    trace1 = {"trace_id": "c01-aaaa1111", "events": [], "final_answer": "Resp 1."}
    case1 = {"case_id": "c01", "hypothesis": ["H4"]}
    trace2 = {"trace_id": "c02-bbbb2222", "events": [], "final_answer": "Resp 2."}
    case2 = {"case_id": "c02", "hypothesis": ["H4"]}

    judgments_dir = tmp_path / "judgments"
    prompts = {"C3": "Julgue C3"}

    with pytest.raises(BudgetExceeded):
        judge_batch(
            [(trace1, case1), (trace2, case2)],
            client=client,
            model="google/gemini-3.8-flash",
            ledger=ledger,
            guard=guard,
            judgments_dir=judgments_dir,
            prompts=prompts,
        )

    # O primeiro trace foi gravado antes do estouro do teto
    assert (judgments_dir / "c01-aaaa1111.json").exists()
    # O segundo trace não foi gravado
    assert not (judgments_dir / "c02-bbbb2222.json").exists()


def test_judge_batch_skips_unparseable_trace_and_continues(tmp_path, capsys):
    from evals.budget import BudgetGuard
    from evals.judge import judge_batch
    from evals.ledger import Ledger

    # Primeiro trace devolve resposta ilegível (sem veredito); segundo devolve pass normal
    class MixedClient:
        def __init__(self):
            self.count = 0
        def chat(self, messages, model):
            self.count += 1
            if self.count == 1:
                return {
                    "choices": [{"message": {"content": "Texto discursivo qualquer sem nenhum veredito."}}],
                    "usage": {"cost": 0.01, "prompt_tokens": 10, "completion_tokens": 10},
                }
            return {
                "choices": [{"message": {"content": '{"justification": "ok", "verdict": "pass"}'}}],
                "usage": {"cost": 0.01, "prompt_tokens": 10, "completion_tokens": 10},
            }

    guard = BudgetGuard(10.0)
    ledger = Ledger(tmp_path / "ledger.jsonl")
    trace1 = {"trace_id": "c01-aaaa1111", "events": [], "final_answer": "Resp 1."}
    case1 = {"case_id": "c01"}
    trace2 = {"trace_id": "c02-bbbb2222", "events": [], "final_answer": "Resp 2."}
    case2 = {"case_id": "c02"}

    judgments_dir = tmp_path / "judgments"
    prompts = {"C3": "Julgue C3"}

    records = judge_batch(
        [(trace1, case1), (trace2, case2)],
        client=MixedClient(),
        model="google/gemini-3.8-flash",
        ledger=ledger,
        guard=guard,
        judgments_dir=judgments_dir,
        prompts=prompts,
    )

    # O primeiro falhou no parse e não gerou arquivo
    assert not (judgments_dir / "c01-aaaa1111.json").exists()
    # O segundo foi concluído com sucesso e gravado
    assert (judgments_dir / "c02-bbbb2222.json").exists()
    assert len(records) == 1
    assert records[0]["trace_id"] == "c02-bbbb2222"

    err = capsys.readouterr().err
    assert "aviso: não foi possível julgar c01-aaaa1111" in err


def test_judgment_file_format_accepted_by_consistency_check(tmp_path):
    from evals.budget import BudgetGuard
    from evals.consistency import _check_juizos
    from evals.judge import judge_trace, write_judgment
    from evals.ledger import Ledger

    client = FakeClient(default_text='{"justification": "Correto", "verdict": "pass"}')
    guard = BudgetGuard(10.0)
    ledger = Ledger(tmp_path / "ledger.jsonl")

    trace = {"trace_id": "c01-aaaa1111", "events": [], "final_answer": "Resp."}
    case = {"case_id": "c01", "hypothesis": ["H4"]}
    prompts = {"C3": "Julgue C3"}

    res = judge_trace(trace, case, ["C3"], client=client, model="google/gemini-3.8-flash", ledger=ledger, guard=guard, prompts=prompts)
    write_judgment(res, tmp_path / "judgments")

    problemas = []
    juizos = _check_juizos(tmp_path, problemas)
    assert not problemas
    assert "c01-aaaa1111" in juizos
    assert juizos["c01-aaaa1111"] == {"C3": "pass"}


def test_judgment_file_format_accepted_by_consistency_check_with_c1(tmp_path):
    from evals.budget import BudgetGuard
    from evals.consistency import _check_juizos
    from evals.judge import judge_trace, write_judgment
    from evals.ledger import Ledger

    client = FakeClient(default_text='{"justification": "Citação com lastro", "verdict": "pass"}')
    guard = BudgetGuard(10.0)
    ledger = Ledger(tmp_path / "ledger.jsonl")

    trace = {
        "trace_id": "c01-aaaa1111",
        "events": [],
        "final_answer": "Conforme a LC 214/2025, art. 14, vale desde 2027-01-01.",
    }
    case = {
        "case_id": "c01",
        "hypothesis": ["H4"],
        "reference_date": "2027-01-01",
        "answer_exists": "sim",
        "expected_provisions": ["LC214.art14"],
    }
    prompts = {"C1": "Julgue C1", "C2": "Julgue C2", "C3": "Julgue C3"}

    res = judge_trace(trace, case, client=client, model="google/gemini-3.8-flash", ledger=ledger, guard=guard, prompts=prompts)
    assert "C1" in res["verdicts"]
    write_judgment(res, tmp_path / "judgments")

    problemas = []
    juizos = _check_juizos(tmp_path, problemas)
    assert not problemas
    assert "c01-aaaa1111" in juizos
    assert "C1" in juizos["c01-aaaa1111"]
    assert juizos["c01-aaaa1111"]["C1"] == "pass"


def test_ledger_records_one_line_per_model_call(tmp_path):
    from evals.budget import BudgetGuard
    from evals.judge import judge_trace
    from evals.ledger import Ledger

    client = FakeClient()
    guard = BudgetGuard(10.0)
    ledger = Ledger(tmp_path / "ledger.jsonl")

    trace = {"trace_id": "c01-aaaa1111", "events": [], "final_answer": "Resp."}
    case = {"case_id": "c01", "hypothesis": ["H13"]}
    prompts = {"C3": "Julgue C3", "C4": "Julgue C4"}

    # Julga 2 critérios: C3 e C4
    judge_trace(trace, case, ["C3", "C4"], client=client, model="google/gemini-3.8-flash", ledger=ledger, guard=guard, prompts=prompts)

    linhas = (tmp_path / "ledger.jsonl").read_text(encoding="utf-8").strip().splitlines()
    assert len(linhas) == 2


def test_hash_prompts_matches_consistency_hash():
    from pathlib import Path
    from evals.consistency import hash_prompts as consistency_hash
    from evals.judge import hash_prompts, load_judge_prompts

    prompts_dir = Path("config/judge_prompts")
    prompts = load_judge_prompts(prompts_dir)
    assert hash_prompts(prompts) == consistency_hash(prompts_dir)
