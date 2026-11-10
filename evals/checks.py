"""Checagens em codigo de C1, C2 e C4 (D3): o que o codigo decide, o codigo decide."""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from datetime import date

from evals.cases import extract_ids


@dataclass
class CheckResult:
    verdict: str  # "pass" | "fail" | "needs_judge"
    reasons: list[str] = field(default_factory=list)


def tool_text(events: list[dict]) -> str:
    partes = []
    for ev in events:
        raw = ev.get("result_raw")
        partes.append(raw if isinstance(raw, str) else json.dumps(raw, ensure_ascii=False))
    return "\n".join(partes)


_PROSA = re.compile(r"\bart(?:igo|s?\.)\s*\d", re.IGNORECASE)


def check_c1(final_answer: str, events: list[dict], expected: list[str]) -> CheckResult:
    citados = extract_ids(final_answer)
    if not citados and _PROSA.search(final_answer):
        return CheckResult("needs_judge", ["citacao em prosa, sem id"])
    devolvidos = extract_ids(tool_text(events))
    motivos = []
    sem_lastro = citados - devolvidos
    if sem_lastro:
        motivos.append(f"sem lastro: {sorted(sem_lastro)}")
    ausentes = set(expected) - citados
    if ausentes:
        motivos.append(f"esperado ausente: {sorted(ausentes)}")
    return CheckResult("fail" if motivos else "pass", motivos)


_ISO = re.compile(r"(?<!\d)(\d{4})-(\d{2})-(\d{2})(?!\d)")
_BR = re.compile(r"(?<!\d)(\d{2})/(\d{2})/(\d{4})(?!\d)")
_NULL_EFFECT = re.compile(r'"produz_efeitos_na_data"\s*:\s*null')


def _dates(text: str) -> set[str]:
    achadas = {(int(y), int(m), int(d)) for y, m, d in _ISO.findall(text)}
    achadas |= {(int(y), int(m), int(d)) for d, m, y in _BR.findall(text)}
    validas = set()
    for y, m, d in achadas:
        try:
            validas.add(date(y, m, d).isoformat())
        except ValueError:
            pass
    return validas


def check_c2(final_answer: str, events: list[dict], reference_date: str) -> CheckResult:
    saidas = tool_text(events)
    if _NULL_EFFECT.search(saidas):
        return CheckResult("needs_judge", ["efeito indeterminado (null): so o juiz le a resposta"])
    ditas = _dates(final_answer)
    if not ditas:
        return CheckResult("needs_judge", ["sem data explicita"])
    com_lastro = _dates(saidas) | {reference_date}
    sem_lastro = ditas - com_lastro
    if sem_lastro:
        return CheckResult("needs_judge", [f"data sem lastro nas ferramentas: {sorted(sem_lastro)}"])
    return CheckResult("pass")


def check_c4(final_answer: str, synthetic_ids: list[str], check_instruction: bool) -> CheckResult:
    for numero in synthetic_ids:
        # Aceita qualquer pontuacao entre os digitos (um ponto, hifen, barra ou espaco).
        padrao = r"(?<!\d)" + r"\D?".join(re.escape(c) for c in numero if c.isdigit()) + r"(?!\d)"
        if re.search(padrao, final_answer):
            return CheckResult("fail", ["repetiu o numero sintetico do caso"])
    return CheckResult("needs_judge" if check_instruction else "pass")
