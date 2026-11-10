"""Teto de custo por rodada (D10): a rodada para ao atingi-lo."""
from __future__ import annotations


class BudgetExceeded(Exception):
    """O gasto da rodada atingiu o teto."""


class BudgetGuard:
    def __init__(self, limit_usd: float) -> None:
        if limit_usd <= 0:
            raise ValueError("o teto deve ser positivo")
        self.limit_usd = limit_usd
        self.spent = 0.0

    def charge(self, cost_usd: float) -> None:
        self.spent += cost_usd
        if self.spent >= self.limit_usd:
            raise BudgetExceeded(
                f"teto de custo atingido: {self.spent:.4f} de {self.limit_usd:.4f} USD")
