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


def test_barra_symlink_novo(tmp_path):
    (tmp_path / "alvo.txt").write_text("x")
    (tmp_path / "atalho").symlink_to(tmp_path / "alvo.txt")
    assert violations(["atalho"], root=tmp_path) == ["atalho"]


def test_barra_symlink_que_aponta_para_pasta_protegida(tmp_path):
    (tmp_path / ".github").mkdir()
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "atalho").symlink_to(tmp_path / ".github", target_is_directory=True)
    assert violations(["docs/atalho"], root=tmp_path) == ["docs/atalho"]


def test_barra_caminho_que_passa_por_symlink_de_diretorio(tmp_path):
    (tmp_path / "real").mkdir()
    (tmp_path / "dir").symlink_to(tmp_path / "real", target_is_directory=True)
    assert violations(["dir/arquivo.txt"], root=tmp_path) == ["dir/arquivo.txt"]


def test_arquivo_comum_e_arquivo_inexistente_passam_com_root(tmp_path):
    (tmp_path / "a.txt").write_text("x")
    assert violations(["a.txt", "novo/b.txt", "apagado.txt"], root=tmp_path) == []
