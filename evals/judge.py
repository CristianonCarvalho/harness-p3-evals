"""Juiz LLM para avaliação de C1, C2, C3 e C4 (Tarefa 11)."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import time
from pathlib import Path
from typing import Any

from evals.budget import BudgetExceeded, BudgetGuard
from evals.checks import check_c1, check_c2
from evals.ledger import Ledger
from evals.privacy import redact_taxpayer_ids

JUDGE_CRITERIA = ("C1", "C2", "C3", "C4")

_JSON_BLOCK_RE = re.compile(r"```(?:json)?\s*(\{.*?\})\s*```", re.DOTALL)
_JSON_OBJECT_RE = re.compile(r"\{[^{}]*\"verdict\"[^{}]*\}", re.DOTALL)

_PASS_RE = re.compile(r"\b(?:pass|aprovado)\b", re.IGNORECASE)
_FAIL_RE = re.compile(r"\b(?:fail|reprovado)\b", re.IGNORECASE)

# Padrões para limpar o prefixo de veredito da justificativa em texto livre
_CLEAN_PREFIX_RE = re.compile(
    r"^(?:\*{1,2})?(?:pass|fail|aprovado|reprovado)(?:\*{1,2})?\s*[:\-—]\s*",
    re.IGNORECASE,
)


def parse_verdict(text: str) -> tuple[str, str]:
    """Interpreta a resposta do juiz e devolve (veredito, justificativa).

    Aceita JSON (com ou sem bloco markdown) ou texto livre com prefixos como
    'PASS:', '**FAIL**', 'Aprovado' ou 'reprovado'.

    Levanta ValueError se a resposta não trouxer veredito claro ou se contiver
    vereditos contraditórios.
    """
    # 1. Tenta extrair JSON (de bloco markdown ou direto no texto)
    json_candidate = None
    m_block = _JSON_BLOCK_RE.search(text)
    if m_block:
        json_candidate = m_block.group(1)
    else:
        m_obj = _JSON_OBJECT_RE.search(text)
        if m_obj:
            json_candidate = m_obj.group(0)

    if json_candidate:
        try:
            data = json.loads(json_candidate)
            if isinstance(data, dict) and "verdict" in data:
                raw_v = str(data["verdict"]).strip().lower()
                justification = str(data.get("justification", "")).strip()
                if raw_v in ("pass", "aprovado"):
                    return "pass", justification
                if raw_v in ("fail", "reprovado"):
                    return "fail", justification
        except json.JSONDecodeError:
            pass

    # 2. Análise de texto livre (fallback quando não há JSON válido com verdict)
    has_pass = bool(_PASS_RE.search(text))
    has_fail = bool(_FAIL_RE.search(text))

    if has_pass and has_fail:
        raise ValueError(f"veredito contraditório na resposta do juiz: {text!r}")
    if not has_pass and not has_fail:
        raise ValueError(f"sem veredito na resposta do juiz: {text!r}")

    verdict = "pass" if has_pass else "fail"
    justification = _CLEAN_PREFIX_RE.sub("", text.strip())
    # Se o texto era só o veredito (ex: "Aprovado." ou "reprovado"), mantém limpo
    if justification.lower() in ("pass", "fail", "aprovado", "reprovado", "aprovado.", "reprovado."):
        justification = ""

    return verdict, justification


def build_messages(
    trace: dict[str, Any],
    case: dict[str, Any],
    criterion: str,
    prompt: str,
) -> list[dict[str, str]]:
    """Monta as mensagens para chamar o juiz LLM em um critério específico.

    A assinatura proíbe qualquer anotação humana (D8).
    """
    question = trace.get("question") or case.get("question", "")
    final_answer = trace.get("final_answer", "")

    events = trace.get("events", [])
    tool_outputs = []
    for ev in events:
        raw = ev.get("result_raw")
        if isinstance(raw, str):
            tool_outputs.append(raw)
        else:
            tool_outputs.append(json.dumps(raw, ensure_ascii=False))
    tools_text = "\n---\n".join(tool_outputs) if tool_outputs else "(nenhuma chamada de ferramenta)"

    user_parts = [
        f"## Pergunta do Usuário\n{question}",
    ]
    ref_date = case.get("reference_date") or case.get("gabarito", {}).get("reference_date", "")
    # A data de referência é injetada estritamente no C2 (critério temporal)
    if criterion == "C2" and ref_date:
        user_parts.append(f"## Data de Referência\n{ref_date}")

    if criterion == "C1":
        expected = case.get("expected_provisions")
        if expected is None:
            expected = case.get("gabarito", {}).get("expected_provisions", [])
        if expected:
            provisions_text = "\n".join(expected)
        else:
            provisions_text = "(nenhum: o gabarito diz que o corpus não responde)"
        user_parts.append(f"## Dispositivos Esperados\n{provisions_text}")

    user_parts.append(f"## Saída Bruta das Ferramentas (Lastro)\n{tools_text}")
    user_parts.append(f"## Resposta Final do Modelo\n{final_answer}")

    return [
        {"role": "system", "content": prompt},
        {"role": "user", "content": "\n\n".join(user_parts)},
    ]


def criteria_for_trace(trace: dict[str, Any], case: dict[str, Any]) -> list[str]:
    """Determina quais critérios o juiz LLM deve avaliar para este trace.

    - C3: sempre avaliado pelo juiz.
    - C1: avaliado se check_c1 retornar 'needs_judge' (citação em prosa).
    - C2: avaliado se check_c2 retornar 'needs_judge'.
    - C4: avaliado se o caso for H13 (prompt injection).
    """
    criteria = ["C3"]

    events = trace.get("events", [])
    final_answer = trace.get("final_answer", "")
    ref_date = case.get("reference_date") or case.get("gabarito", {}).get("reference_date", "")
    ans_exists = case.get("answer_exists") or case.get("gabarito", {}).get("answer_exists", "sim")

    expected = case.get("expected_provisions")
    if expected is None:
        expected = case.get("gabarito", {}).get("expected_provisions", [])

    res_c1 = check_c1(final_answer, events, expected)
    if res_c1.verdict == "needs_judge":
        criteria.append("C1")

    if ref_date:
        res_c2 = check_c2(final_answer, events, ref_date, answer_exists=ans_exists)
        if res_c2.verdict == "needs_judge":
            criteria.append("C2")

    hyps = case.get("hypothesis", [])
    if isinstance(hyps, str):
        hyps = [hyps]
    if "H13" in hyps:
        criteria.append("C4")

    return sorted(criteria)


def hash_prompts(prompts: dict[str, str] | Path) -> str:
    """Calcula o hash SHA-256 canônico dos prompts (compatível com consistency.hash_prompts)."""
    if isinstance(prompts, Path):
        from evals.consistency import hash_prompts as consistency_hash
        return consistency_hash(prompts) or ""
    h = hashlib.sha256()
    for k in sorted(prompts.keys()):
        h.update(f"{k}.md\n".encode("utf-8"))
        h.update(prompts[k].encode("utf-8"))
    return h.hexdigest()


def load_judge_prompts(prompts_dir: Path) -> dict[str, str]:
    """Carrega os arquivos de prompt para C2, C3 e C4."""
    prompts: dict[str, str] = {}
    for crit in JUDGE_CRITERIA:
        path = prompts_dir / f"{crit}.md"
        if path.is_file():
            prompts[crit] = path.read_text(encoding="utf-8")
    return prompts


def judge_trace(
    trace: dict[str, Any],
    case: dict[str, Any],
    criteria: list[str] | None = None,
    *,
    client: Any,
    model: str,
    ledger: Ledger,
    guard: BudgetGuard,
    prompts: dict[str, str],
    version: str | None = None,
) -> dict[str, Any]:
    """Julga um único trace com o modelo do juiz nos critérios aplicáveis."""
    tid = trace["trace_id"]
    if criteria is None:
        criteria = criteria_for_trace(trace, case)

    verdicts: dict[str, str] = {}
    justifications: dict[str, str] = {}

    for crit in criteria:
        prompt = prompts.get(crit)
        if not prompt or not prompt.strip():
            raise ValueError(f"prompt ausente ou vazio para o critério {crit}")

        messages = build_messages(trace, case, crit, prompt)

        start = time.monotonic()
        resp = client.chat(messages, model=model)
        latency_ms = int((time.monotonic() - start) * 1000)

        cost = ledger.llm(0, model, resp, latency_ms)
        guard.charge(cost)

        choices = resp.get("choices") if isinstance(resp, dict) else None
        if not choices or not isinstance(choices, list):
            raise ValueError(f"{tid}: resposta da API sem escolhas válidas (choices)")

        raw_text = choices[0].get("message", {}).get("content")
        if not isinstance(raw_text, str) or not raw_text.strip():
            raise ValueError(f"{tid}: resposta da API sem texto de conteúdo")

        verdict, justification = parse_verdict(raw_text)

        verdicts[crit] = verdict
        justifications[crit] = redact_taxpayer_ids(justification)

    exact_version = version or model
    if not exact_version or not str(exact_version).strip():
        raise ValueError("versão/id do modelo juiz não pode ser vazio")

    return {
        "trace_id": tid,
        "judge": {
            "model": model,
            "version": exact_version,
            "prompts_sha256": hash_prompts(prompts),
        },
        "verdicts": verdicts,
        "justification": justifications,
    }


def write_judgment(record: dict[str, Any], judgments_dir: Path) -> Path:
    """Grava o registro de julgamento em judgments/<trace_id>.json."""
    judgments_dir.mkdir(parents=True, exist_ok=True)
    path = judgments_dir / f"{record['trace_id']}.json"
    path.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def judge_batch(
    items: list[tuple[dict[str, Any], dict[str, Any]]],
    *,
    client: Any,
    model: str,
    ledger: Ledger,
    guard: BudgetGuard,
    judgments_dir: Path,
    prompts: dict[str, str] | None = None,
    prompts_dir: Path | None = None,
    version: str | None = None,
) -> list[dict[str, Any]]:
    """Julga um lote de pares (trace, case), gravando cada resultado imediatamente.

    Se uma resposta for ilegível, registra a falha e segue com os outros traces do lote.
    Se o teto de orçamento for atingido (BudgetExceeded), interrompe a execução,
    mantendo intactos os traces já gravados.
    """
    judgments_dir.mkdir(parents=True, exist_ok=True)

    if prompts is None:
        if prompts_dir is None:
            prompts_dir = Path("config/judge_prompts")
        prompts = load_judge_prompts(prompts_dir)

    results: list[dict[str, Any]] = []

    for trace, case in items:
        try:
            record = judge_trace(
                trace,
                case,
                client=client,
                model=model,
                ledger=ledger,
                guard=guard,
                prompts=prompts,
                version=version,
            )
            write_judgment(record, judgments_dir)
            results.append(record)
        except BudgetExceeded:
            # Estouro de teto: encerra o lote imediatamente, mantendo os anteriores gravados
            raise
        except ValueError as exc:
            # Resposta ilegível ou sem choices: não derruba o lote já pago.
            # O trace permanece sem julgamento gravado, ficando 'pendente'.
            tid = trace.get("trace_id", "desconhecido")
            print(f"aviso: não foi possível julgar {tid} ({exc})", file=sys.stderr)

    return results


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Julga traces com um LLM nos critérios C1, C2, C3 e C4.")
    ap.add_argument("trace_ids", nargs="+")
    ap.add_argument("--model", required=True, help="ID exato e com versão do modelo juiz no OpenRouter")
    ap.add_argument("--budget-usd", required=True, type=float)
    ap.add_argument("--traces-dir", type=Path, default=Path("traces"))
    ap.add_argument("--cases-dir", type=Path, default=Path("cases"))
    ap.add_argument("--judgments-dir", type=Path, default=Path("judgments"))
    ap.add_argument("--prompts-dir", type=Path, default=Path("config/judge_prompts"))
    ap.add_argument("--ledger", type=Path, default=Path("runs/judge-ledger.jsonl"))
    args = ap.parse_args(argv)

    chave = os.environ.get("OPENROUTER_API_KEY")
    if not chave:
        print("Variável OPENROUTER_API_KEY não definida no ambiente; nada foi enviado ao modelo.",
              file=sys.stderr)
        return 2

    try:
        from evals.cases import load_cases
        from evals.client import OpenRouterClient
        from evals.trace import load_trace

        casos = {c["case_id"]: c for c in load_cases(args.cases_dir)}
        itens: list[tuple[dict[str, Any], dict[str, Any]]] = []
        for tid in args.trace_ids:
            achados = sorted(args.traces_dir.rglob(f"{tid}.json"))
            if not achados:
                print(f"trace não encontrado: {tid}.json em {args.traces_dir}", file=sys.stderr)
                return 1
            trace = load_trace(achados[0])
            caso = casos.get(trace.get("case_id", ""))
            if caso is None:
                print(f"caso não encontrado: {trace.get('case_id')!r} em {args.cases_dir}", file=sys.stderr)
                return 1
            itens.append((trace, caso))
    except (OSError, ValueError) as exc:
        print(f"erro: {exc}", file=sys.stderr)
        return 1

    with OpenRouterClient(chave) as client:
        try:
            records = judge_batch(
                itens,
                client=client,
                model=args.model,
                guard=BudgetGuard(args.budget_usd),
                ledger=Ledger(args.ledger),
                judgments_dir=args.judgments_dir,
                prompts_dir=args.prompts_dir,
            )
        except BudgetExceeded as exc:
            print(f"teto de custo atingido: {exc}", file=sys.stderr)
            return 2

    for r in records:
        print(args.judgments_dir / f"{r['trace_id']}.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
