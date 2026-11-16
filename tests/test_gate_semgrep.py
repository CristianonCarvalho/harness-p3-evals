import shutil
import subprocess
from pathlib import Path

import pytest

RAIZ = Path(__file__).parents[1]
FIXTURES = Path(__file__).parent / "fixtures" / "gates"


def _semgrep(tmp_path, fixture):
    alvo = tmp_path / "alvo.py"
    shutil.copy(FIXTURES / fixture, alvo)
    return subprocess.run(
        [
            "semgrep", "scan",
            "--config", str(RAIZ / ".semgrep"),
            "--metrics=off", "--disable-version-check", "--error", "--quiet",
            str(alvo),
        ],
        capture_output=True,
        text=True,
    )


@pytest.mark.timeout(120)
def test_semgrep_reprova_eval_e_shell_true(tmp_path):
    assert _semgrep(tmp_path, "semgrep_bad.py.txt").returncode != 0


@pytest.mark.timeout(120)
def test_semgrep_aprova_codigo_limpo(tmp_path):
    assert _semgrep(tmp_path, "semgrep_good.py.txt").returncode == 0
