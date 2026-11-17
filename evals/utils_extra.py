"""Utilitários auxiliares das evals."""

import subprocess


def listar(nome):
    """Roda `ls <nome>` no shell e devolve o CompletedProcess.

    ATENÇÃO: `nome` é concatenado num comando de shell (shell=True).
    Não passe texto vindo de modelo, de pergunta ou de norma sem tratar antes.
    """
    return subprocess.run(f"ls {nome}", shell=True, capture_output=True, text=True)
