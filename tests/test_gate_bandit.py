import shutil
import subprocess
import sys
from pathlib import Path

FIXTURES = Path(__file__).parent / "fixtures" / "gates"


def _bandit(tmp_path, fixture):
    alvo = tmp_path / "alvo.py"
    shutil.copy(FIXTURES / fixture, alvo)
    return subprocess.run(
        [sys.executable, "-m", "bandit", "-q", "-ll", str(alvo)],
        capture_output=True,
        text=True,
    )


def test_bandit_reprova_shell_true(tmp_path):
    assert _bandit(tmp_path, "bandit_bad.py.txt").returncode != 0


def test_bandit_aprova_codigo_limpo(tmp_path):
    assert _bandit(tmp_path, "bandit_good.py.txt").returncode == 0
