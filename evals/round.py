"""Rodada em lote (Passo 43): roda os casos nas condicoes pedidas e grava um resumo.

Condicoes:
- com_skill: todos os casos, server local, com a skill.
- sem_skill: so os casos com `sem_skill` em `subsets`, server local, sem a skill.
- remoto: so os casos com `remoto` em `subsets`, server remoto, com a skill.

Um diretorio de trabalho por condicao, um teto de custo para a rodada inteira e um
`random.Random(seed)` compartilhado (a pergunta sai com os mesmos CPF/CNPJ sinteticos
em qualquer repeticao da mesma semente). A rodada para no teto e grava o resumo mesmo assim.
"""
from __future__ import annotations

import json
import random
import subprocess
import sys
from argparse import ArgumentParser
from datetime import datetime
from pathlib import Path
from typing import Callable

from evals.budget import BudgetExceeded, BudgetGuard
from evals.cases import load_cases
from evals.runner import RemoteNotConfigured, _check_remote_env, prepare_workdir, run_with_retries

# Condicao -> (com skill?, server, subset exigido nos casos ou None para todos)
CONDICOES = {
    "com_skill": {"with_skill": True, "server": "local", "subset": None},
    "sem_skill": {"with_skill": False, "server": "local", "subset": "sem_skill"},
    "remoto": {"with_skill": True, "server": "remoto", "subset": "remoto"},
}
CONDICOES_PADRAO = "com_skill,sem_skill,remoto"
SEED_PADRAO = 20261114


def _validar_condicoes(conditions: list[str]) -> None:
    desconhecidas = [c for c in conditions if c not in CONDICOES]
    if desconhecidas:
        raise ValueError(f"condicao desconhecida: {', '.join(desconhecidas)} "
                         f"(use {', '.join(CONDICOES)})")
    if len(set(conditions)) != len(conditions):
        raise ValueError("condicao repetida na lista")


def plan_round(cases: list[dict], conditions: list[str]) -> list[tuple[str, dict]]:
    """Pares (condicao, caso), por condicao na ordem dada e depois por case_id."""
    _validar_condicoes(conditions)
    plano: list[tuple[str, dict]] = []
    for cond in conditions:
        subset = CONDICOES[cond]["subset"]
        escolhidos = [c for c in cases if subset is None or subset in c.get("subsets", [])]
        plano += [(cond, c) for c in sorted(escolhidos, key=lambda c: c["case_id"])]
    return plano


def _arquivos(pasta: Path) -> set[Path]:
    return set(pasta.glob("*.json")) if pasta.is_dir() else set()


def _traces_novos(pasta: Path, antes: set[Path]) -> list[Path]:
    # Ordem de gravacao (mtime): o trace_id e aleatorio, nao cronologico.
    return sorted(_arquivos(pasta) - antes, key=lambda p: p.stat().st_mtime_ns)


def run_round(cases: list[dict], *, conditions: list[str], model: str, p2_dir: Path,
              p2_tag: str, out_dir: Path, workdirs_dir: Path, budget_usd: float,
              per_case_usd: float, seed: int, run: Callable = subprocess.run,
              prepare: Callable = prepare_workdir, round_id: str | None = None,
              progress: Callable[[str, str, str, float], None] | None = None) -> dict:
    """Roda a rodada e grava `_round.json` em out_dir/<round_id>/. Devolve o mesmo dict."""
    _validar_condicoes(conditions)
    if "remoto" in conditions:
        _check_remote_env("remoto")  # falha antes de preparar ou rodar qualquer coisa
    rid = round_id or datetime.now().strftime("%Y%m%d-%H%M%S")
    pasta_rodada = Path(out_dir) / rid
    if pasta_rodada.exists():
        raise FileExistsError(f"a rodada {rid} ja existe: {pasta_rodada}")
    pasta_rodada.mkdir(parents=True)

    plano = plan_round(cases, conditions)
    workdirs = {}
    for cond in conditions:
        cfg = CONDICOES[cond]
        workdirs[cond] = prepare(Path(p2_dir), Path(workdirs_dir) / f"{rid}-{cond}",
                               with_skill=cfg["with_skill"], server=cfg["server"])

    guard = BudgetGuard(budget_usd)
    rng = random.Random(seed)
    runs: list[dict] = []
    stopped: str | None = None

    for cond, caso in plano:
        pasta = pasta_rodada / cond
        antes = _arquivos(pasta)
        try:
            resultado = run_with_retries(
                caso, model=model, server=CONDICOES[cond]["server"], workdir=workdirs[cond],
                p2_tag=p2_tag, traces_dir=pasta, guard=guard, max_budget_usd=per_case_usd,
                rng=rng, run=run)
            status, investigate = resultado.status, resultado.investigate
        except BudgetExceeded as exc:
            # O trace do caso que estourou o teto e gravado antes da excecao.
            novos = _traces_novos(pasta, antes)
            status = json.loads(novos[-1].read_text(encoding="utf-8"))["status"] if novos else "erro"
            investigate = False
            stopped = str(exc)
        novos = _traces_novos(pasta, antes)
        runs.append({"condition": cond, "case_id": caso["case_id"], "status": status,
                     "investigate": investigate, "traces": [p.name for p in novos]})
        if progress:
            progress(cond, caso["case_id"], status, guard.spent)
        if stopped:
            break

    resumo = {"round_id": rid, "model": model, "p2_tag": p2_tag, "conditions": list(conditions),
              "budget_usd": budget_usd, "per_case_usd": per_case_usd, "seed": seed,
              "spent_usd": round(guard.spent, 4), "stopped": stopped, "runs": runs}
    (pasta_rodada / "_round.json").write_text(
        json.dumps(resumo, ensure_ascii=False, indent=2), encoding="utf-8")
    return resumo


def _montar_parser() -> ArgumentParser:
    p = ArgumentParser(prog="python -m evals.cli run-round",
                       description="Roda uma rodada de casos nas condicoes pedidas.")
    p.add_argument("--model", required=True)
    p.add_argument("--p2-dir", type=Path, required=True)
    p.add_argument("--p2-tag", required=True)
    p.add_argument("--budget-usd", type=float, required=True)
    p.add_argument("--per-case-usd", type=float, required=True)
    p.add_argument("--conditions", default=CONDICOES_PADRAO)
    p.add_argument("--cases-dir", type=Path, default=Path("cases"))
    p.add_argument("--out-dir", type=Path, default=Path("traces/rounds"))
    p.add_argument("--workdirs-dir", type=Path, default=Path("workdirs"))
    p.add_argument("--seed", type=int, default=SEED_PADRAO)
    p.add_argument("--round-id")
    p.add_argument("--dry-run", action="store_true")
    return p


def main(argv: list[str] | None = None, *, run: Callable = subprocess.run,
         prepare: Callable = prepare_workdir) -> int:
    args = _montar_parser().parse_args(argv)
    condicoes = [c.strip() for c in args.conditions.split(",")]
    try:
        _validar_condicoes(condicoes)
    except ValueError as exc:
        print(f"erro: {exc}", file=sys.stderr)
        return 2
    if args.budget_usd <= 0 or args.per_case_usd <= 0:
        print("erro: os tetos de custo devem ser positivos", file=sys.stderr)
        return 2
    if not args.cases_dir.is_dir():
        print(f"erro: pasta de casos não encontrada: {args.cases_dir}", file=sys.stderr)
        return 1
    casos = load_cases(args.cases_dir)

    if args.dry_run:
        for cond in condicoes:
            n = len(plan_round(casos, [cond]))
            print(f"{cond}: {n} execução(ões)")
        print(f"total: {len(plan_round(casos, condicoes))} execução(ões); nada foi rodado")
        return 0

    if not args.p2_dir.is_dir():
        print(f"erro: pasta do P2 não encontrada: {args.p2_dir}", file=sys.stderr)
        return 1

    def imprimir(cond: str, case_id: str, status: str, gasto: float) -> None:
        print(f"{cond} {case_id} {status} gasto acumulado: US$ {gasto:.4f}")

    try:
        resumo = run_round(
            casos, conditions=condicoes, model=args.model, p2_dir=args.p2_dir,
            p2_tag=args.p2_tag, out_dir=args.out_dir, workdirs_dir=args.workdirs_dir,
            budget_usd=args.budget_usd, per_case_usd=args.per_case_usd, seed=args.seed,
            run=run, prepare=prepare, round_id=args.round_id, progress=imprimir)
    except RemoteNotConfigured as exc:
        print(f"erro: {exc}", file=sys.stderr)
        return 1
    except FileExistsError as exc:
        print(f"erro: {exc}", file=sys.stderr)
        return 1

    print(f"gasto total: US$ {resumo['spent_usd']:.4f} de US$ {args.budget_usd:.4f}")
    if resumo["stopped"]:
        print(f"rodada parada: {resumo['stopped']}", file=sys.stderr)
    investigar = [r for r in resumo["runs"] if r["investigate"]]
    for r in investigar:
        print(f"investigar: {r['condition']} {r['case_id']}", file=sys.stderr)
    return 1 if resumo["stopped"] or investigar else 0


if __name__ == "__main__":
    raise SystemExit(main())
