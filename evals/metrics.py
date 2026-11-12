"""Métricas TPR e TNR e matriz de confusão (Tarefa 6)."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

VALID_VERDICTS = ("pass", "fail", "n/a")
CRITERIA = ("C1", "C2", "C3", "C4")


@dataclass(frozen=True)
class ConfusionMatrix:
    tp: int
    fn: int
    fp: int
    tn: int
    tpr: float | None
    tnr: float | None
    n_pos: int
    n_neg: int
    n_na: int = 0
    n_disputed: int = 0


@dataclass(frozen=True)
class Agreement:
    agree: int
    total: int
    n_na: int
    rate: float | None


def _validate_blind_and_unique(
    annotations: list[dict[str, Any]], *, label: str = "anotações humanas"
) -> None:
    non_blind = [
        h.get("trace_id", "")
        for h in annotations
        if h.get("kind") != "blind"
    ]
    if non_blind:
        non_blind_sorted = ", ".join(sorted(non_blind))
        raise ValueError(
            f"só anotações cegas entram na calibração (R3); traces inválidos: {non_blind_sorted}"
        )

    seen = set()
    duplicates = set()
    for h in annotations:
        tid = h.get("trace_id", "")
        if tid in seen:
            duplicates.add(tid)
        seen.add(tid)
    if duplicates:
        dup_sorted = ", ".join(sorted(duplicates))
        raise ValueError(
            f"trace_id duplicado na lista de {label}: {dup_sorted}"
        )


def confusion(
    human: list[dict[str, Any]],
    judge: dict[str, Any],
    criterion: str,
    *,
    disputed: frozenset[str] = frozenset(),
) -> ConfusionMatrix:
    # 1. Validações da amostra humana (só cegas e sem duplicatas)
    _validate_blind_and_unique(human, label="anotações humanas")

    # 2. Separa os casos disputados (ficam fora da calibração)
    n_disputed = 0
    active_human = []
    for h in human:
        tid = h.get("trace_id", "")
        if tid in disputed:
            n_disputed += 1
        else:
            active_human.append(h)

    # 3. Falta no juiz ou formato inválido (avaliado apenas para os traces ativos)
    bad_format = []
    for h in active_human:
        tid = h.get("trace_id", "")
        if tid in judge and not isinstance(judge[tid], dict):
            bad_format.append(tid)
    if bad_format:
        bad_sorted = ", ".join(sorted(bad_format))
        raise ValueError(
            f"juiz com formato inválido para {len(bad_format)} trace(s) "
            f"(esperado dict {{critério: veredito}}): {bad_sorted}"
        )

    missing = []
    for h in active_human:
        tid = h.get("trace_id", "")
        if tid not in judge or criterion not in judge[tid]:
            missing.append(tid)
    if missing:
        missing_sorted = ", ".join(sorted(missing))
        raise ValueError(
            f"{criterion}: sem veredito do juiz para {len(missing)} trace(s): {missing_sorted}"
        )

    # 4. Validação de valores de veredito nos traces ativos
    invalid_verdicts = []
    for h in active_human:
        tid = h.get("trace_id", "")
        h_verdicts = h.get("verdicts", {})
        h_val = h_verdicts.get(criterion)
        j_val = judge[tid][criterion]

        if h_val not in VALID_VERDICTS:
            invalid_verdicts.append((tid, "humano", h_val))
        if j_val not in VALID_VERDICTS:
            invalid_verdicts.append((tid, "juiz", j_val))

    if invalid_verdicts:
        invalid_verdicts.sort(key=lambda item: item[0])
        details = ", ".join(
            f"{tid} ({side}={val!r})" for tid, side, val in invalid_verdicts
        )
        raise ValueError(f"veredito inválido (esperado pass/fail/n/a): {details}")

    # 5. Contagem dos vereditos
    tp = fn = fp = tn = n_na = 0

    for h in active_human:
        tid = h.get("trace_id", "")
        h_verdicts = h.get("verdicts", {})
        h_val = h_verdicts.get(criterion)
        j_val = judge[tid][criterion]

        if h_val == "n/a" or j_val == "n/a":
            n_na += 1
            continue

        if h_val == "pass" and j_val == "pass":
            tp += 1
        elif h_val == "pass" and j_val == "fail":
            fn += 1
        elif h_val == "fail" and j_val == "pass":
            fp += 1
        elif h_val == "fail" and j_val == "fail":
            tn += 1

    n_pos = tp + fn
    n_neg = tn + fp
    tpr = (tp / n_pos) if n_pos > 0 else None
    tnr = (tn / n_neg) if n_neg > 0 else None

    return ConfusionMatrix(
        tp=tp,
        fn=fn,
        fp=fp,
        tn=tn,
        tpr=tpr,
        tnr=tnr,
        n_pos=n_pos,
        n_neg=n_neg,
        n_na=n_na,
        n_disputed=n_disputed,
    )


def self_agreement(
    first: list[dict[str, Any]],
    second: list[dict[str, Any]],
) -> dict[str, Agreement]:
    # 1. Validações preliminares em cada lista
    _validate_blind_and_unique(first, label="primeira rodada")
    _validate_blind_and_unique(second, label="segunda rodada")

    # 2. Conferência de pareamento exato de traces
    map_first = {h.get("trace_id", ""): h for h in first}
    map_second = {h.get("trace_id", ""): h for h in second}

    set_first = set(map_first.keys())
    set_second = set(map_second.keys())

    if set_first != set_second:
        only_first = sorted(set_first - set_second)
        only_second = sorted(set_second - set_first)
        parts = []
        if only_first:
            parts.append(f"só na primeira: {', '.join(only_first)}")
        if only_second:
            parts.append(f"só na segunda: {', '.join(only_second)}")
        raise ValueError(f"traces não coincidem entre as rodadas: {'; '.join(parts)}")

    # 3. Validação de valores válidos e n/a unilateral
    invalid_verdicts = []
    unilateral_na = []

    for tid in sorted(set_first):
        h1 = map_first[tid]
        h2 = map_second[tid]
        v1_dict = h1.get("verdicts", {})
        v2_dict = h2.get("verdicts", {})

        for crit in CRITERIA:
            val1 = v1_dict.get(crit)
            val2 = v2_dict.get(crit)

            if val1 not in VALID_VERDICTS:
                invalid_verdicts.append((tid, "primeira", crit, val1))
            if val2 not in VALID_VERDICTS:
                invalid_verdicts.append((tid, "segunda", crit, val2))

            if val1 in VALID_VERDICTS and val2 in VALID_VERDICTS:
                if (val1 == "n/a") != (val2 == "n/a"):
                    unilateral_na.append((tid, crit, val1, val2))

    if invalid_verdicts:
        invalid_verdicts.sort(key=lambda x: x[0])
        details = ", ".join(
            f"{tid} ({side} {crit}={val!r})"
            for tid, side, crit, val in invalid_verdicts
        )
        raise ValueError(f"veredito inválido: {details}")

    if unilateral_na:
        unilateral_na.sort(key=lambda x: x[0])
        details = ", ".join(
            f"{tid} ({crit}: first={v1!r}, second={v2!r})"
            for tid, crit, v1, v2 in unilateral_na
        )
        raise ValueError(f"n/a de um lado só no mesmo trace: {details}")

    # 4. Cálculo da concordância por critério
    result: dict[str, Agreement] = {}
    for crit in CRITERIA:
        agree = 0
        total = 0
        n_na = 0
        for tid in sorted(set_first):
            val1 = map_first[tid].get("verdicts", {}).get(crit)
            val2 = map_second[tid].get("verdicts", {}).get(crit)

            if val1 == "n/a" and val2 == "n/a":
                n_na += 1
            else:
                total += 1
                if val1 == val2:
                    agree += 1

        rate = (agree / total) if total > 0 else None
        result[crit] = Agreement(agree=agree, total=total, n_na=n_na, rate=rate)

    return result
