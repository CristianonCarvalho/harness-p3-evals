"""Guard de caminhos: o agente não pode alterar o que define os gates."""

from __future__ import annotations

import posixpath
import sys

# Em minúsculas: a comparação ignora maiúsculas (macOS e Windows não diferenciam).
PROTEGIDOS = (
    ".github",
    ".semgrep",
    "pipeline",
    "pyproject.toml",
    "uv.lock",
)


def _protegido(caminho: str) -> bool:
    if posixpath.basename(caminho) == "codeowners":
        return True
    return any(caminho == p or caminho.startswith(p + "/") for p in PROTEGIDOS)


def violations(changed: list[str]) -> list[str]:
    ruins = []
    for bruto in changed:
        texto = bruto.strip()
        if not texto:
            continue
        norm = posixpath.normpath(texto.replace("\\", "/"))
        if norm.startswith("/") or norm == ".." or norm.startswith("../"):
            ruins.append(bruto)
        elif _protegido(norm.lower()):
            ruins.append(bruto)
    return ruins


def main() -> int:
    ruins = violations(sys.stdin.read().splitlines())
    for caminho in ruins:
        print(f"caminho protegido alterado pelo agente: {caminho}", file=sys.stderr)
    return 1 if ruins else 0


if __name__ == "__main__":
    raise SystemExit(main())
