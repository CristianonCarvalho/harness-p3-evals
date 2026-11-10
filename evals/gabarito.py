"""Confere o gabarito dos casos contra as ferramentas do P2, sem modelo nenhum."""
from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Callable

CallTool = Callable[[str, dict], dict]


def verify_case(case: dict, call_tool: CallTool) -> list[str]:
    g = case["gabarito"]
    erros = []
    for id_ in g["expected_provisions"]:
        saida = call_tool("obter_dispositivo", {
            "id": id_, "data_referencia": g["reference_date"], "incluir_filhos": False})
        if not saida.get("encontrado"):
            erros.append(f"{case['case_id']}: {id_} nao existe em {g['reference_date']}")
        elif not saida.get("efeitos"):
            erros.append(f"{case['case_id']}: {id_} voltou sem efeitos")
    return erros


def make_p2_caller(p2_dir: Path, run=subprocess.run) -> CallTool:
    def call(name: str, args: dict) -> dict:
        if name != "obter_dispositivo":
            raise ValueError(f"ferramenta nao suportada na conferencia: {name}")
        cmd = ["uv", "run", "python", "client/taxlaw_client.py", "--json",
               "obter", args["id"], "--data", args["data_referencia"]]
        done = run(cmd, cwd=p2_dir, capture_output=True, text=True, timeout=60)
        if done.returncode not in (0, 1):
            raise RuntimeError(f"cliente do P2 falhou (codigo {done.returncode})")
        return json.loads(done.stdout)
    return call
