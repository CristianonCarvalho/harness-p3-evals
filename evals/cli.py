"""Linha de comando do projeto: so le argumentos e chama os modulos. Sem regra de negocio aqui."""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

from evals import annotation_drafter, annotate, dossier, drafter, sampling
from evals.cases import apply_splits, load_cases
from evals.consistency import check_repo, hash_prompts, scan_privacy
from evals.gabarito import make_p2_caller, verify_case

# Subcomandos que repassam os argumentos restantes ao main do modulo dono.
DELEGADOS = {
    "dossier": dossier.main,
    "annotate": annotate.main,
    "sample": sampling.main,
    "draft-gabarito": drafter.main,
    "draft-annotation": annotation_drafter.main,
}


def _montar_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python -m evals.cli",
                                     description="Comandos do projeto de avaliação (P3).")
    sub = parser.add_subparsers(dest="comando", required=True, metavar="COMANDO")

    p = sub.add_parser("check-repo", help="confere a coerência dos dados versionados")
    p.add_argument("--root", type=Path, default=Path("."))

    p = sub.add_parser("scan-privacy", help="procura números com formato de CPF/CNPJ")
    p.add_argument("--root", type=Path, default=Path("."))

    p = sub.add_parser("apply-splits", help="sorteia os splits dos casos com a semente dada")
    p.add_argument("--seed", type=int, required=True)
    p.add_argument("--cases-dir", type=Path, default=Path("cases"))

    p = sub.add_parser("verify-gabarito", help="confere o gabarito contra o P2")
    p.add_argument("--p2-dir", type=Path, required=True)
    p.add_argument("--cases-dir", type=Path, default=Path("cases"))

    p = sub.add_parser("hash-prompts", help="imprime o hash dos prompts do juiz")
    p.add_argument("--dir", type=Path, default=Path("config/judge_prompts"))

    for nome in DELEGADOS:
        sub.add_parser(nome, add_help=False, help="delegado ao módulo dono (os argumentos seguem para ele)")
    return parser


def _cmd_check_repo(args) -> int:
    resultado = check_repo(args.root)
    for aviso in resultado.warnings:
        print(f"aviso: {aviso}")
    for problema in resultado.problems:
        print(f"problema: {problema}", file=sys.stderr)
    if resultado.problems:
        print(f"{len(resultado.problems)} problema(s) encontrado(s)", file=sys.stderr)
        return 1
    print("nenhum problema encontrado")
    return 0


def _cmd_scan_privacy(args) -> int:
    problemas = scan_privacy(args.root)
    for problema in problemas:
        print(f"problema: {problema}", file=sys.stderr)
    if problemas:
        return 1
    print("nenhum número com formato de CPF/CNPJ")
    return 0


def _cmd_apply_splits(args) -> int:
    try:
        divisao = apply_splits(args.cases_dir, args.seed)
    except (OSError, ValueError) as exc:
        print(f"erro: {exc}", file=sys.stderr)
        return 1
    print(f"{len(divisao)} caso(s) dividido(s) com a semente {args.seed}")
    return 0


def _cmd_verify_gabarito(args) -> int:
    if not args.p2_dir.is_dir():
        print(f"erro: pasta do P2 não encontrada: {args.p2_dir}", file=sys.stderr)
        return 1
    try:
        casos = load_cases(args.cases_dir)
        chamar = make_p2_caller(args.p2_dir)
        erros: list[str] = []
        for caso in casos:
            erros += verify_case(caso, chamar)
    except (OSError, ValueError, RuntimeError, subprocess.SubprocessError) as exc:
        print(f"erro: {exc}", file=sys.stderr)
        return 1
    for erro in erros:
        print(f"problema: {erro}", file=sys.stderr)
    if erros:
        return 1
    print(f"gabarito conferido: {len(casos)} caso(s)")
    return 0


def _cmd_hash_prompts(args) -> int:
    h = hash_prompts(args.dir)
    if h is None:
        print(f"nada a conferir: sem prompts .md em {args.dir}")
        return 0
    print(h)
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = _montar_parser()
    args, resto = parser.parse_known_args(argv)
    if args.comando in DELEGADOS:
        return DELEGADOS[args.comando](resto)
    if resto:
        parser.error(f"argumentos desconhecidos: {' '.join(resto)}")
    if args.comando == "check-repo":
        return _cmd_check_repo(args)
    if args.comando == "scan-privacy":
        return _cmd_scan_privacy(args)
    if args.comando == "apply-splits":
        return _cmd_apply_splits(args)
    if args.comando == "verify-gabarito":
        return _cmd_verify_gabarito(args)
    return _cmd_hash_prompts(args)


if __name__ == "__main__":
    raise SystemExit(main())
