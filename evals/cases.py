"""Formato do caso e do gabarito (D13) e divisao sorteada (D6)."""
from __future__ import annotations

import json
import random
import re
from collections import defaultdict
from datetime import date
from pathlib import Path

from evals.privacy import find_taxpayer_ids

# Formato real dos ids do corpus do P2: NORMA.artN[-A][.parN|.parunico][.incROMANO][.aliX]
ID_RE = re.compile(
    r"(?<![A-Za-z0-9])(?:CF|ADCT|EC\d+|LC\d+)\.art\d+(?:-[A-Z])?"
    r"(?:\.par(?:\d+|unico))?(?:\.inc[IVXLCDM]+)?(?:\.ali[a-z])?"
    r"(?![A-Za-z0-9]|\.(?:par|inc|ali))"
)
HYPOTHESES = {f"H{i}" for i in range(1, 15)}
ANSWER_EXISTS = {"sim", "nao", "parcial"}
SPLITS = {"desenvolvimento", "teste"}
SUBSETS = {"sem_skill", "remoto"}
PLACEHOLDERS = ("{CPF}", "{CNPJ}")


def extract_ids(text: str) -> set[str]:
    return {m.group(0) for m in ID_RE.finditer(text)}


def validate_case(d: dict) -> list[str]:
    errors = [f"campo ausente: {k}" for k in
              ("case_id", "question", "hypothesis", "gabarito") if k not in d]
    if errors:
        return errors
    if not d["hypothesis"] or not set(d["hypothesis"]) <= HYPOTHESES:
        errors.append(f"hypothesis invalida: {d['hypothesis']!r}")
    if d.get("split") not in (None, *SPLITS):
        errors.append(f"split invalido: {d.get('split')!r}")
    if not set(d.get("subsets", [])) <= SUBSETS:
        errors.append(f"subsets invalido: {d.get('subsets')!r}")
    # Vigia so de ida (D2, decisao 6): sem H12, o C4 viraria n/a em silencio.
    for marcador in PLACEHOLDERS:
        if marcador in d["question"] and "H12" not in d["hypothesis"]:
            errors.append(f"a pergunta tem {marcador} mas a hipotese nao inclui H12 "
                          "(sem H12, o C4 nao se aplica e o vazamento nao e medido)")
    pergunta = d["question"]
    for marcador in PLACEHOLDERS:
        pergunta = pergunta.replace(marcador, "")
    if find_taxpayer_ids(pergunta):
        errors.append("a pergunta contem numero de documento; use {CPF} ou {CNPJ}")
    g = d["gabarito"]
    if g.get("answer_exists") not in ANSWER_EXISTS:
        errors.append(f"gabarito.answer_exists invalido: {g.get('answer_exists')!r}")
    esperados = g.get("expected_provisions", [])
    for i in esperados:
        if not ID_RE.fullmatch(i):
            errors.append(f"id fora do formato: {i!r}")
    if g.get("answer_exists") == "nao" and esperados:
        errors.append("answer_exists=nao exige expected_provisions vazio")
    if g.get("answer_exists") in ("sim", "parcial") and not esperados:
        errors.append("answer_exists=sim/parcial exige expected_provisions")
    try:
        date.fromisoformat(g.get("reference_date", ""))
    except ValueError:
        errors.append("gabarito.reference_date deve ser AAAA-MM-DD")
    if not isinstance(g.get("disputed"), bool):
        errors.append("gabarito.disputed deve ser booleano")
    return errors


def load_cases(cases_dir: Path) -> list[dict]:
    return [json.loads(p.read_text(encoding="utf-8"))
            for p in sorted(cases_dir.glob("*.json")) if not p.name.startswith("_")]


def assign_splits(cases: list[dict], seed: int, dev_fraction: float = 0.3) -> dict[str, str]:
    rng = random.Random(seed)
    grupos: dict[str, list[str]] = defaultdict(list)
    for c in sorted(cases, key=lambda c: c["case_id"]):
        grupos[c["hypothesis"][0]].append(c["case_id"])
    out: dict[str, str] = {}
    for h in sorted(grupos):
        ids = grupos[h][:]
        rng.shuffle(ids)
        n_dev = round(len(ids) * dev_fraction)
        for i, cid in enumerate(ids):
            out[cid] = "desenvolvimento" if i < n_dev else "teste"
    return out


def apply_splits(cases_dir: Path, seed: int) -> dict[str, str]:
    cases = load_cases(cases_dir)
    out = assign_splits(cases, seed)
    for c in cases:
        c["split"] = out[c["case_id"]]
        (cases_dir / f"{c['case_id']}.json").write_text(
            json.dumps(c, ensure_ascii=False, indent=2), encoding="utf-8")
    (cases_dir / "_split_meta.json").write_text(json.dumps({"seed": seed}), encoding="utf-8")
    return out
