"""Carrega o prompt de um caso sintético e o entrega ao workflow do agente."""

from __future__ import annotations

import argparse
import json
import re
import sys
import uuid
from pathlib import Path

CASES_DIR = Path(__file__).parent / "pr_cases"
ID_RE = re.compile(r"[0-9]{2}-[a-z]+(-[a-z]+)*")
GATES_VALIDOS = {"offline", "bandit", "semgrep", "gitleaks", "codeql", "path-guard"}
CAMPOS = ("id", "title", "prompt", "expected")


def load_case(case_id: str, cases_dir: Path = CASES_DIR) -> dict:
    if not ID_RE.fullmatch(case_id):
        raise ValueError(f"id de caso inválido: {case_id!r}")
    caminho = cases_dir / f"{case_id}.json"
    if not caminho.is_file():
        raise ValueError(f"caso inexistente: {case_id}")
    caso = json.loads(caminho.read_text(encoding="utf-8"))
    for campo in CAMPOS:
        if campo not in caso:
            raise ValueError(f"caso {case_id} sem o campo {campo!r}")
    if caso["id"] != case_id:
        raise ValueError(f"id interno {caso['id']!r} difere do nome do arquivo {case_id!r}")
    return caso


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("case_id")
    ap.add_argument("--output", help="arquivo GITHUB_OUTPUT onde gravar o prompt")
    args = ap.parse_args(argv)
    try:
        caso = load_case(args.case_id)
    except ValueError as erro:
        print(erro, file=sys.stderr)
        return 1
    if args.output:
        delim = f"EOF_{uuid.uuid4().hex}"
        with open(args.output, "a", encoding="utf-8") as saida:
            saida.write(f"prompt<<{delim}\n{caso['prompt']}\n{delim}\n")
    else:
        print(caso["prompt"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
