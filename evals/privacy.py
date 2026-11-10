"""Detecta e gera numeros de CPF/CNPJ.

Regra do projeto: nenhum numero de documento, nem sintetico, entra no
repositorio. Os sinteticos sao gerados em tempo de execucao. A deteccao e
conservadora de proposito: olha o formato (11 ou 14 digitos), nao o digito
verificador, para nao deixar passar um numero so porque esta "invalido".
"""
from __future__ import annotations

import random
import re
from pathlib import Path

_CPF = r"(?<!\d)\d{3}\.?\d{3}\.?\d{3}-?\d{2}(?!\d)"
_CNPJ = r"(?<!\d)\d{2}\.?\d{3}\.?\d{3}/?\d{4}-?\d{2}(?!\d)"
# CNPJ primeiro: tem 14 digitos e um CPF nao pode "roubar" parte dele.
_PATTERN = re.compile(f"{_CNPJ}|{_CPF}")


def find_taxpayer_ids(text: str) -> list[str]:
    return [m.group(0) for m in _PATTERN.finditer(text)]


def redact_taxpayer_ids(text: str) -> str:
    return _PATTERN.sub("[número removido]", text)


def _check_digit(digits: list[int], weights: list[int]) -> int:
    resto = sum(d * w for d, w in zip(digits, weights)) % 11
    return 0 if resto < 2 else 11 - resto


def _cpf_digits(base: list[int]) -> list[int]:
    d1 = _check_digit(base, list(range(10, 1, -1)))
    d2 = _check_digit(base + [d1], list(range(11, 1, -1)))
    return base + [d1, d2]


_CNPJ_W1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
_CNPJ_W2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]


def _cnpj_digits(base: list[int]) -> list[int]:
    d1 = _check_digit(base, _CNPJ_W1)
    d2 = _check_digit(base + [d1], _CNPJ_W2)
    return base + [d1, d2]


def make_synthetic_cpf(rng: random.Random) -> str:
    while True:
        base = [rng.randint(0, 9) for _ in range(9)]
        if len(set(base)) > 1:  # evita 111111111 e semelhantes
            return "".join(map(str, _cpf_digits(base)))


def make_synthetic_cnpj(rng: random.Random) -> str:
    while True:
        base = [rng.randint(0, 9) for _ in range(12)]
        if len(set(base)) > 1:
            return "".join(map(str, _cnpj_digits(base)))


def is_valid_cpf(s: str) -> bool:
    d = [int(c) for c in s if c.isdigit()]
    return len(d) == 11 and len(set(d)) > 1 and _cpf_digits(d[:9]) == d


def is_valid_cnpj(s: str) -> bool:
    d = [int(c) for c in s if c.isdigit()]
    return len(d) == 14 and len(set(d)) > 1 and _cnpj_digits(d[:12]) == d


def scan_files(paths: list[Path]) -> list[tuple[Path, str]]:
    achados: list[tuple[Path, str]] = []
    for p in paths:
        try:
            texto = p.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        achados.extend((p, m) for m in find_taxpayer_ids(texto))
    return achados
