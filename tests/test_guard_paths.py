import pytest

from pipeline.guard_paths import violations


@pytest.mark.parametrize(
    "caminho",
    [
        ".github/workflows/ci.yml",
        "./.github/workflows/ci.yml",
        "a/../.github/workflows/ci.yml",
        ".GITHUB/workflows/ci.yml",
        ".github/CODEOWNERS",
        "CODEOWNERS",
        "docs/CODEOWNERS",
        ".semgrep/agent-code.yml",
        "pipeline/guard_paths.py",
        "pyproject.toml",
        "uv.lock",
        "../fora/do/repo.txt",
        "/etc/passwd",
        "..",
    ],
)
def test_barra_caminhos_protegidos(caminho):
    assert violations([caminho]) == [caminho]


@pytest.mark.parametrize(
    "caminho",
    [
        "README.md",
        "evals/stats.py",
        "tests/test_stats.py",
        "config/judge_prompts/C1.md",
        ".github-notas.md",
        "pipelines/x.py",
    ],
)
def test_libera_caminhos_comuns(caminho):
    assert violations([caminho]) == []


def test_ignora_linhas_vazias_e_mantem_so_as_violacoes():
    assert violations(["", "  ", "README.md", "uv.lock"]) == ["uv.lock"]
