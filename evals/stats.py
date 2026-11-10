"""Intervalo de Wilson (95%): decisao adiada de D12, tomada na tarefa 7."""
from __future__ import annotations

import math


def wilson_interval(successes: int, n: int, z: float = 1.96) -> tuple[float, float] | None:
    if n == 0:
        return None
    p = successes / n
    denom = 1 + z * z / n
    centro = (p + z * z / (2 * n)) / denom
    meia = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return max(0.0, centro - meia), min(1.0, centro + meia)


def intervals_overlap(a: tuple[float, float], b: tuple[float, float]) -> bool:
    return not (a[1] < b[0] or b[1] < a[0])
