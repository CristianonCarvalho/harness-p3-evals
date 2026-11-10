"""Formato do trace (D5): um JSON por execucao, imutavel."""
from __future__ import annotations

import json
import uuid
from pathlib import Path

STATUSES = {"ok", "erro", "estourou_limite"}
SERVERS = {"local", "remoto"}
_REQUIRED = ("trace_id", "case_id", "status", "source", "model", "conditions",
             "question", "events", "final_answer", "usage")
_CONDITIONS = ("skill", "hook", "server", "p2_tag", "corpus_version")
_USAGE = ("input_tokens", "output_tokens", "cost_usd", "duration_ms")


def validate_trace(d: dict) -> list[str]:
    errors = [f"campo ausente: {k}" for k in _REQUIRED if k not in d]
    if errors:
        return errors
    if d["status"] not in STATUSES:
        errors.append(f"status invalido: {d['status']!r}")
    conds = d["conditions"]
    errors += [f"conditions.{k} ausente" for k in _CONDITIONS if k not in conds]
    if conds.get("server") not in SERVERS:
        errors.append(f"conditions.server invalido: {conds.get('server')!r}")
    errors += [f"usage.{k} ausente" for k in _USAGE if k not in d["usage"]]
    for i, ev in enumerate(d["events"]):
        if "tool" not in ev or "args" not in ev:
            errors.append(f"events[{i}]: faltam tool/args")
        # Sem a saida bruta, C1 e C2 nao sao checaveis por codigo.
        if d["status"] == "ok" and ev.get("result_raw") is None:
            errors.append(f"events[{i}]: result_raw ausente")
    return errors


def new_trace_id(case_id: str) -> str:
    return f"{case_id}-{uuid.uuid4().hex[:8]}"


def write_trace(d: dict, traces_dir: Path) -> Path:
    errors = validate_trace(d)
    if errors:
        raise ValueError("trace invalido: " + "; ".join(errors))
    traces_dir.mkdir(parents=True, exist_ok=True)
    path = traces_dir / f"{d['trace_id']}.json"
    # Modo "x": o trace e imutavel, nunca se sobrescreve.
    with open(path, "x", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=2)
    return path


def load_trace(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))
