"""Teto de custo e de turnos por execução do agente. Falha fechado."""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path


def read_result(path: str) -> dict:
    dados = json.loads(Path(path).read_text(encoding="utf-8"))
    mensagens = dados if isinstance(dados, list) else [dados]
    for msg in reversed(mensagens):
        if isinstance(msg, dict) and msg.get("type") == "result":
            return msg
    raise ValueError("sem mensagem de resultado no arquivo de execução")


def _numero_valido(valor: object) -> bool:
    """Número real, finito e não negativo. bool é int em Python: fica de fora de propósito.

    NaN precisa ser barrado aqui: `nan > teto` dá falso e passaria como "dentro do teto".
    """
    if isinstance(valor, bool) or not isinstance(valor, (int, float)):
        return False
    return math.isfinite(valor) and valor >= 0


def check(result: dict, max_cost_usd: float, max_turns: int) -> list[str]:
    problemas = []
    custo = result.get("total_cost_usd")
    turnos = result.get("num_turns")
    if custo is None:
        problemas.append("custo ausente no resultado (falha fechada)")
    elif not _numero_valido(custo):
        problemas.append(f"custo inválido no resultado: {custo!r} (falha fechada)")
    elif custo > max_cost_usd:
        problemas.append(f"custo {custo:.4f} USD acima do teto de {max_cost_usd:.2f}")
    if turnos is None:
        problemas.append("número de turnos ausente no resultado (falha fechada)")
    elif not _numero_valido(turnos) or turnos != int(turnos):
        problemas.append(f"número de turnos inválido no resultado: {turnos!r} (falha fechada)")
    elif turnos > max_turns:
        problemas.append(f"{turnos} turnos acima do teto de {max_turns}")
    return problemas


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("arquivo")
    ap.add_argument("--max-cost", type=float, required=True)
    ap.add_argument("--max-turns", type=int, required=True)
    args = ap.parse_args(argv)
    try:
        resultado = read_result(args.arquivo)
    except (OSError, ValueError) as erro:  # json.JSONDecodeError é ValueError
        print(f"orçamento: não consegui ler o resultado: {erro}", file=sys.stderr)
        return 1
    problemas = check(resultado, args.max_cost, args.max_turns)
    for p in problemas:
        print(f"orçamento: {p}", file=sys.stderr)
    if not problemas:
        print(f"orçamento ok: {resultado['total_cost_usd']:.4f} USD, {resultado['num_turns']} turnos")
    return 1 if problemas else 0


if __name__ == "__main__":
    raise SystemExit(main())
