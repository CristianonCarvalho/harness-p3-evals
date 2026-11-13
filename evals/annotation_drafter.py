"""Rascunho de anotação por LLM: a IA rascunha os veredictos e o código confere e recusa o que estiver errado.

O rascunho nunca vira anotação aqui. Ele fica guardado para sempre, sem alteração, e a pessoa
confirma ou muda cada veredicto depois. Assim o projeto mede quantas vezes a pessoa mudou o que
a IA sugeriu (ancoragem).

Regras que protegem a medição:
- um trace da amostra cega só é rascunhado depois que a anotação cega humana existe;
- um rascunho por trace, nunca sobrescrito nem refeito;
- o rascunho precisa passar no validador da anotação; um rascunho inválido é recusado, nunca corrigido.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import time
from pathlib import Path

from evals.annotation import load_annotation, validate_annotation
from evals.budget import BudgetExceeded, BudgetGuard
from evals.cases import load_cases
from evals.client import OpenRouterClient
from evals.dossier import build_dossier
from evals.drafter import DraftRejected
from evals.ledger import Ledger
from evals.privacy import redact_taxpayer_ids
from evals.sampling import load_samples
from evals.trace import load_trace

ROOT = Path(__file__).resolve().parent.parent
PROMPT_PATH = ROOT / "config" / "drafter_prompts" / "anotacao.md"

CAMPOS_RASCUNHO = ("verdicts", "uncertain", "note")
_FENCED = re.compile(r"```json\s*(.*?)\s*```", re.DOTALL)
_ID_SEGURO = re.compile(r"[A-Za-z0-9_-]+")


def blind_ids(samples: dict) -> set[str]:
    """Ids da amostra cega: os de 'blind' mais os de cada extensão."""
    if not samples:
        return set()
    ids = set(samples.get("blind", {}).get("trace_ids", []))
    for ext in samples.get("extensions", []):
        ids.update(ext.get("trace_ids_added", []))
    return ids


def parse_annotation_draft(text: str) -> dict:
    """Lê a resposta do modelo: JSON puro ou cerca ```json. Qualquer outra coisa é recusada."""
    s = text.strip()
    m = _FENCED.fullmatch(s)
    if m:
        s = m.group(1)
    try:
        data = json.loads(s)
    except json.JSONDecodeError as exc:
        raise DraftRejected([f"resposta sem JSON válido: {exc.msg}"]) from exc
    if not isinstance(data, dict):
        raise DraftRejected(["resposta não é um objeto JSON"])

    faltam = [k for k in CAMPOS_RASCUNHO if k not in data]
    if faltam:
        raise DraftRejected([f"campos ausentes no rascunho: {', '.join(faltam)}"])

    problemas = []
    verdicts = data["verdicts"]
    if not (isinstance(verdicts, dict)
            and all(isinstance(k, str) and isinstance(v, str) for k, v in verdicts.items())):
        problemas.append("verdicts deve ser um objeto que liga critérios a vereditos em texto")
    uncertain = data["uncertain"]
    if not (isinstance(uncertain, list) and all(isinstance(i, str) for i in uncertain)):
        problemas.append("uncertain deve ser uma lista de textos")
    if not isinstance(data["note"], str):
        problemas.append("note deve ser texto")
    if problemas:
        raise DraftRejected(problemas)
    return {"verdicts": verdicts, "uncertain": uncertain, "note": data["note"]}


def draft_annotation(
    trace: dict,
    case: dict,
    *,
    client,
    model: str,
    guard: BudgetGuard,
    ledger: Ledger,
    blind: set[str],
    annotations_dir: Path,
    drafts_dir: Path,
    prompt: str,
) -> dict:
    """Rascunha a anotação de um trace. Não grava nada: quem grava é write_annotation_draft."""
    tid = trace["trace_id"]

    # Recusas antes de qualquer chamada ao modelo.
    if trace.get("status") != "ok":
        raise DraftRejected([
            f"{tid}: trace com status {trace.get('status')!r}; só se rascunha trace com status 'ok'"
        ])
    e_cega = tid in blind
    if e_cega and load_annotation(annotations_dir, tid) is None:
        raise DraftRejected([
            f"{tid}: a amostra cega exige a anotação cega gravada antes do rascunho "
            "(grave a anotação cega primeiro)"
        ])
    caminho = drafts_dir / "annotations" / f"{tid}.json"
    if caminho.exists():
        raise DraftRejected([
            f"{tid}: já existe rascunho ({caminho.name}); um rascunho por trace, nunca refeito"
        ])

    # So o dossie cego entra na mensagem: nunca anotacao, rascunho ou veredito anterior.
    mensagens = [
        {"role": "system", "content": prompt},
        {"role": "user", "content": build_dossier(trace, case, mode="cega")},
    ]
    inicio = time.monotonic()
    resp = client.chat(mensagens, model=model)
    latency_ms = int((time.monotonic() - inicio) * 1000)
    # O ledger grava antes do teto: a chamada fica registrada mesmo se estourar.
    cost = ledger.llm(0, model, resp, latency_ms)
    guard.charge(cost)

    try:
        texto = resp["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as exc:
        raise DraftRejected(["resposta do modelo sem texto de conteúdo"]) from exc
    parsed = parse_annotation_draft(texto)

    candidata = {
        "trace_id": tid,
        "verdicts": parsed["verdicts"],
        "note": redact_taxpayer_ids(parsed["note"]),
        "uncertain": parsed["uncertain"],
        "kind": "revised",
        "draft": f"drafts/annotations/{tid}.json",
    }
    erros = validate_annotation(candidata, case, trace)
    if erros:
        raise DraftRejected(erros)

    return {
        "trace_id": tid,
        "model": model,
        "verdicts": parsed["verdicts"],
        "uncertain": parsed["uncertain"],
        "note": candidata["note"],
        "prompt_sha": hashlib.sha256(prompt.encode("utf-8")).hexdigest()[:12],
        "blind": e_cega,
    }


def write_annotation_draft(draft: dict, drafts_dir: Path) -> Path:
    """Grava o rascunho em modo 'x': um arquivo existente nunca e sobrescrito."""
    tid = draft["trace_id"]
    if not isinstance(tid, str) or not _ID_SEGURO.fullmatch(tid):
        raise ValueError(f"trace_id inseguro para nome de arquivo: {tid!r}")
    pasta = drafts_dir / "annotations"
    pasta.mkdir(parents=True, exist_ok=True)
    caminho = pasta / f"{tid}.json"
    with open(caminho, "x", encoding="utf-8") as f:
        json.dump(draft, f, ensure_ascii=False, indent=2)
    return caminho


def draft_annotations_batch(items: list[tuple[dict, dict]], *, drafts_dir: Path, **kwargs) -> dict:
    """Rascunha e grava um trace por vez. Recusa um trace e segue; para no teto de custo."""
    written: list[Path] = []
    rejected: list[dict] = []
    for trace, case in items:
        try:
            draft = draft_annotation(trace, case, drafts_dir=drafts_dir, **kwargs)
        except DraftRejected as exc:
            rejected.append({"trace_id": trace.get("trace_id"), "reasons": list(exc.reasons)})
            continue
        except BudgetExceeded as exc:
            # Os arquivos ja escritos ficam no disco; a nota diz quais, para quem le o erro.
            gravados = ", ".join(p.name for p in written) or "nenhum"
            exc.add_note(f"rascunhos já gravados antes do teto: {gravados}")
            raise
        written.append(write_annotation_draft(draft, drafts_dir))
    return {"written": written, "rejected": rejected}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Rascunha a anotação de traces com um LLM e confere offline.")
    ap.add_argument("trace_ids", nargs="+")
    ap.add_argument("--model", required=True)
    ap.add_argument("--budget-usd", required=True, type=float)
    ap.add_argument("--traces-dir", type=Path, default=Path("traces"))
    ap.add_argument("--cases-dir", type=Path, default=Path("cases"))
    ap.add_argument("--annotations-dir", type=Path, default=Path("annotations"))
    ap.add_argument("--drafts-dir", type=Path, default=Path("drafts"))
    ap.add_argument("--samples", type=Path, default=Path("annotations/_samples.json"))
    ap.add_argument("--ledger", type=Path, default=Path("runs/annotation-drafter-ledger.jsonl"))
    args = ap.parse_args(argv)

    chave = os.environ.get("OPENROUTER_API_KEY")
    if not chave:
        print("Variável OPENROUTER_API_KEY não definida no ambiente; nada foi enviado ao modelo.",
              file=sys.stderr)
        return 2

    try:
        casos = {c["case_id"]: c for c in load_cases(args.cases_dir)}
        itens: list[tuple[dict, dict]] = []
        for tid in args.trace_ids:
            achados = sorted(args.traces_dir.rglob(f"{tid}.json"))
            if not achados:
                print(f"trace não encontrado: {tid}.json em {args.traces_dir}", file=sys.stderr)
                return 1
            trace = load_trace(achados[0])
            caso = casos.get(trace.get("case_id"))
            if caso is None:
                print(f"caso não encontrado: {trace.get('case_id')!r} em {args.cases_dir}", file=sys.stderr)
                return 1
            itens.append((trace, caso))
        blind = blind_ids(load_samples(args.samples))
        prompt = PROMPT_PATH.read_text(encoding="utf-8")
    except (OSError, ValueError) as exc:
        print(f"erro: {exc}", file=sys.stderr)
        return 1

    with OpenRouterClient(chave) as client:
        try:
            res = draft_annotations_batch(
                itens,
                drafts_dir=args.drafts_dir,
                client=client,
                model=args.model,
                guard=BudgetGuard(args.budget_usd),
                ledger=Ledger(args.ledger),
                blind=blind,
                annotations_dir=args.annotations_dir,
                prompt=prompt,
            )
        except BudgetExceeded as exc:
            print(f"teto de custo atingido: {exc}", file=sys.stderr)
            for nota in getattr(exc, "__notes__", []):
                print(nota, file=sys.stderr)
            return 2

    for caminho in res["written"]:
        print(caminho)
    for rec in res["rejected"]:
        for motivo in rec["reasons"]:
            print(f"recusado ({rec['trace_id']}): {motivo}", file=sys.stderr)
    return 1 if res["rejected"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
