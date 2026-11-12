"""Gabarito drafter: um LLM rascunha o gabarito; o codigo confere e recusa o que estiver errado.

O rascunho nunca e decidido aqui. Uma pessoa confere depois. Este modulo so
escreve o rascunho em disco quando ele passa em todas as checagens offline e
nas consultas ao P2 (via ``call_tool``).
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import re
import sys
import time
from collections import defaultdict
from pathlib import Path

from evals.budget import BudgetExceeded, BudgetGuard
from evals.cases import validate_case
from evals.client import OpenRouterClient
from evals.gabarito import make_p2_caller, verify_case
from evals.ledger import Ledger
from evals.privacy import redact_taxpayer_ids
from evals.runner import corpus_version as compute_corpus_version

ROOT = Path(__file__).resolve().parent.parent
PROMPT_PATH = ROOT / "config" / "drafter_prompts" / "gabarito.md"

REQUIRED_KEYS = ("answer_exists", "expected_provisions", "reference_date", "quotes", "justification")
_FENCED = re.compile(r"```(?:json)?\s*(.*?)\s*```", re.DOTALL)


class DraftRejected(ValueError):
    """O rascunho foi recusado; ``reasons`` lista todos os problemas encontrados."""

    def __init__(self, reasons: list[str]) -> None:
        self.reasons = list(reasons)
        super().__init__("rascunho recusado: " + "; ".join(self.reasons))


def load_corpus(path: Path) -> list[dict]:
    return json.loads(path.read_text(encoding="utf-8"))["dispositivos"]


def format_corpus(corpus: list[dict]) -> str:
    # Um id pode aparecer varias vezes (versoes diferentes): todas as linhas entram, na ordem do corpus.
    return "\n".join(
        f"{d['id']} | {d['citacao']} | efeitos {d['efeitos_desde']}..{d['efeitos_ate'] or ''} | {d['texto']}"
        for d in corpus
    )


def build_messages(case: dict, corpus: list[dict], *, reference_date: str, prompt: str) -> list[dict]:
    # So a pergunta do caso entra: nunca gabarito, trace ou resposta de modelo.
    usuario = (
        f"Pergunta: {case['question']}\n"
        f"Data de referencia: {reference_date}\n\n"
        f"Corpus:\n{format_corpus(corpus)}"
    )
    return [
        {"role": "system", "content": prompt},
        {"role": "user", "content": usuario},
    ]


def parse_draft(text: str) -> dict:
    s = text.strip()
    m = _FENCED.fullmatch(s)
    if m:
        s = m.group(1)
    try:
        data = json.loads(s)
    except json.JSONDecodeError as exc:
        raise DraftRejected([f"resposta sem JSON valido: {exc.msg}"]) from exc
    if not isinstance(data, dict):
        raise DraftRejected(["resposta nao e um objeto JSON"])

    faltam = [k for k in REQUIRED_KEYS if k not in data]
    if faltam:
        raise DraftRejected([f"campos ausentes no rascunho: {', '.join(faltam)}"])

    problemas = []
    if not isinstance(data["answer_exists"], str):
        problemas.append("answer_exists deve ser texto")
    if not (isinstance(data["expected_provisions"], list)
            and all(isinstance(i, str) for i in data["expected_provisions"])):
        problemas.append("expected_provisions deve ser uma lista de textos")
    if not isinstance(data["reference_date"], str):
        problemas.append("reference_date deve ser texto")
    quotes = data["quotes"]
    if not (isinstance(quotes, list) and all(
            isinstance(q, dict) and isinstance(q.get("id"), str) and isinstance(q.get("text"), str)
            for q in quotes)):
        problemas.append("quotes deve ser uma lista de {id, text} textos")
    if not isinstance(data["justification"], str):
        problemas.append("justification deve ser texto")
    if problemas:
        raise DraftRejected(problemas)
    return data


def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()


def check_quotes(draft: dict, corpus: list[dict]) -> list[str]:
    textos: dict[str, list[str]] = defaultdict(list)
    for d in corpus:
        textos[d["id"]].append(_norm(d["texto"]))

    erros = []
    for q in draft["quotes"]:
        qid, trecho = q["id"], _norm(q["text"])
        if not trecho:
            erros.append(f"trecho vazio para {qid}")
        elif qid not in textos:
            erros.append(f"id do trecho fora do corpus: {qid}")
        elif not any(trecho in t for t in textos[qid]):
            erros.append(f"trecho nao aparece literalmente no texto de {qid}")

    citados = {q["id"] for q in draft["quotes"]}
    for id_ in draft["expected_provisions"]:
        if id_ not in citados:
            erros.append(f"{id_} esta em expected_provisions sem nenhum trecho")
    return erros


def _refuse_if_traced(case_id: str, traces_dir: Path) -> None:
    if not traces_dir.exists():
        return
    padrao = re.compile(rf"{re.escape(case_id)}-[0-9a-f]{{8}}\.json")
    for p in traces_dir.rglob("*"):
        if padrao.fullmatch(p.name):
            raise DraftRejected([
                f"{case_id} ja tem trace ({p.name}); o gabarito nao pode ser rascunhado depois da resposta do modelo"
            ])


def draft_gabarito(
    case: dict,
    corpus: list[dict],
    *,
    client,
    model: str,
    guard: BudgetGuard,
    ledger: Ledger,
    traces_dir: Path,
    call_tool,
    prompt: str,
    reference_date: str,
    corpus_version: str,
) -> dict:
    case_id = case["case_id"]
    _refuse_if_traced(case_id, traces_dir)

    mensagens = build_messages(case, corpus, reference_date=reference_date, prompt=prompt)
    inicio = time.monotonic()
    resp = client.chat(mensagens, model=model)
    latency_ms = int((time.monotonic() - inicio) * 1000)
    # O ledger grava antes do teto: a chamada fica registrada mesmo se estourar.
    cost = ledger.llm(0, model, resp, latency_ms)
    guard.charge(cost)

    draft = parse_draft(resp["choices"][0]["message"]["content"])

    problemas: list[str] = []
    if draft["reference_date"] != reference_date:
        problemas.append(
            f"reference_date do rascunho ({draft['reference_date']}) difere da data de referencia ({reference_date})")

    candidato = copy.deepcopy(case)
    candidato["gabarito"] = {
        "answer_exists": draft["answer_exists"],
        "expected_provisions": draft["expected_provisions"],
        "reference_date": draft["reference_date"],
        "disputed": False,
    }
    problemas.extend(validate_case(candidato))
    problemas.extend(check_quotes(draft, corpus))
    # O P2 so e consultado quando as checagens offline passaram.
    if not problemas:
        problemas.extend(verify_case(candidato, call_tool))
    if problemas:
        raise DraftRejected(problemas)

    return {
        "case_id": case_id,
        "model": model,
        "answer_exists": draft["answer_exists"],
        "expected_provisions": draft["expected_provisions"],
        "reference_date": reference_date,
        "quotes": [{"id": q["id"], "text": redact_taxpayer_ids(q["text"])} for q in draft["quotes"]],
        "justification": redact_taxpayer_ids(draft["justification"]),
        "disputed": False,
        # Contra qual corpus e qual prompt o rascunho foi feito: sem isso, ele nao se reproduz.
        "corpus_version": corpus_version,
        "prompt_sha": hashlib.sha256(prompt.encode("utf-8")).hexdigest()[:12],
    }


def write_draft(draft: dict, drafts_dir: Path) -> Path:
    cases_dir = drafts_dir / "cases"
    cases_dir.mkdir(parents=True, exist_ok=True)
    case_id = draft["case_id"]
    padrao = re.compile(rf"{re.escape(case_id)}\.v([0-9]+)\.json")
    usados = [int(m.group(1)) for p in cases_dir.iterdir() if (m := padrao.fullmatch(p.name))]
    n = 1 + max(usados, default=0)
    caminho = cases_dir / f"{case_id}.v{n}.json"
    with open(caminho, "x", encoding="utf-8") as f:
        json.dump(draft, f, ensure_ascii=False, indent=2)
    return caminho


def draft_batch(cases: list[dict], corpus: list[dict], *, drafts_dir: Path, **kwargs) -> dict:
    written: list[Path] = []
    rejected: list[dict] = []
    for case in cases:
        try:
            draft = draft_gabarito(case, corpus, **kwargs)
        except DraftRejected as exc:
            rejected.append({"case_id": case["case_id"], "reasons": list(exc.reasons)})
            continue
        except BudgetExceeded as exc:
            # Os arquivos ja escritos ficam no disco; a nota diz quais, para quem le o erro.
            gravados = ", ".join(p.name for p in written) or "nenhum"
            exc.add_note(f"rascunhos ja gravados antes do teto: {gravados}")
            raise
        written.append(write_draft(draft, drafts_dir))
    return {"written": written, "rejected": rejected}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Rascunha o gabarito de um caso com um LLM e confere offline.")
    ap.add_argument("case_json", type=Path)
    ap.add_argument("--reference-date", required=True)
    ap.add_argument("--model", required=True)
    ap.add_argument("--p2-dir", required=True, type=Path)
    ap.add_argument("--budget-usd", required=True, type=float)
    ap.add_argument("--drafts-dir", type=Path, default=Path("drafts"))
    ap.add_argument("--traces-dir", type=Path, default=Path("traces"))
    ap.add_argument("--ledger", type=Path, default=Path("runs/drafter-ledger.jsonl"))
    args = ap.parse_args(argv)

    chave = os.environ.get("OPENROUTER_API_KEY")
    if not chave:
        print("Variavel OPENROUTER_API_KEY nao definida no ambiente; nada foi enviado ao modelo.",
              file=sys.stderr)
        return 2

    case = json.loads(args.case_json.read_text(encoding="utf-8"))
    corpus = load_corpus(args.p2_dir / "corpus" / "dispositivos.json")
    prompt = PROMPT_PATH.read_text(encoding="utf-8")

    with OpenRouterClient(chave) as client:
        try:
            res = draft_batch(
                [case], corpus,
                drafts_dir=args.drafts_dir,
                client=client,
                model=args.model,
                guard=BudgetGuard(args.budget_usd),
                ledger=Ledger(args.ledger),
                traces_dir=args.traces_dir,
                call_tool=make_p2_caller(args.p2_dir),
                prompt=prompt,
                reference_date=args.reference_date,
                corpus_version=compute_corpus_version(args.p2_dir),
            )
        except BudgetExceeded as exc:
            print(f"teto de custo atingido: {exc}", file=sys.stderr)
            for nota in getattr(exc, "__notes__", []):
                print(nota, file=sys.stderr)
            return 2

    if res["rejected"]:
        for motivo in res["rejected"][0]["reasons"]:
            print(f"recusado: {motivo}", file=sys.stderr)
        return 1
    for caminho in res["written"]:
        print(caminho)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
