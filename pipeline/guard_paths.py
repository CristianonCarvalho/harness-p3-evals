"""Guard de caminhos: o agente não pode alterar o que define os gates."""

from __future__ import annotations

import posixpath
import sys
from pathlib import Path, PurePosixPath

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


def _passa_por_symlink(caminho: str, root: Path) -> bool:
    """True se o próprio arquivo ou qualquer pasta do caminho for um symlink."""
    atual = root
    for parte in PurePosixPath(caminho).parts:
        atual = atual / parte
        if atual.is_symlink():
            return True
    return False


def violations(changed: list[str], root: Path | None = None) -> list[str]:
    """Caminhos proibidos entre os alterados.

    Com `root`, também barra symlinks: um atalho pode apontar para uma pasta
    protegida ou para fora do repositório, e o nome do caminho não mostra isso.
    """
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
        elif root is not None and _passa_por_symlink(norm, root):
            ruins.append(bruto)
    return ruins


def main() -> int:
    ruins = violations(sys.stdin.read().splitlines(), root=Path.cwd())
    for caminho in ruins:
        print(f"caminho protegido alterado pelo agente: {caminho}", file=sys.stderr)
    return 1 if ruins else 0


if __name__ == "__main__":
    raise SystemExit(main())
