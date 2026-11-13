"""Amostras cega e de consistencia dos traces (so do split de teste).

A amostra cega e sorteada uma vez, so entre traces do split "teste" com
status "ok", no maximo um trace por caso, estratificada pela primeira
hipotese do caso (a mesma regra de evals.cases.assign_splits).
"""
from __future__ import annotations

import argparse
import json
import random
import re
import sys
from collections import defaultdict
from fractions import Fraction
from math import floor
from pathlib import Path

from evals.cases import load_cases
from evals.trace import load_trace

TRACE_NAME_RE = re.compile(r"^[A-Za-z0-9_-]+-[0-9a-f]{8}\.json$")
DESCRICAO_ELEGIVEL = "casos elegiveis (teste, status ok)"


def eligible(traces: list[dict], cases: dict[str, dict]) -> list[dict]:
    """Traces de casos do split teste, com status ok, ordenados por trace_id."""
    out = [t for t in traces
           if t["case_id"] in cases
           and cases[t["case_id"]].get("split") == "teste"
           and t.get("status") == "ok"]
    return sorted(out, key=lambda t: t["trace_id"])


def _alocar(tamanhos: dict[str, int], n: int, *, minimo_um: bool = True) -> dict[str, int]:
    """Divide n vagas entre estratos proporcionalmente ao numero de casos.

    Maior resto; nenhum estrato passa do seu numero de casos; cada estrato
    com casos recebe pelo menos 1 (a vaga sai do estrato com mais vagas).
    Pre-condicao: n >= numero de estratos e n <= soma dos tamanhos.
    """
    alocacao: dict[str, int] = {}
    pendentes = dict(tamanhos)
    restante = n
    # Estratos que caberiam inteiros na cota ficam com todos os seus casos.
    while pendentes and restante > 0:
        total = sum(pendentes.values())
        cotas = {h: Fraction(restante * t, total) for h, t in pendentes.items()}
        saturados = [h for h in pendentes if cotas[h] >= pendentes[h]]
        if not saturados:
            break
        for h in saturados:
            alocacao[h] = pendentes.pop(h)
            restante -= alocacao[h]
    if pendentes and restante > 0:
        total = sum(pendentes.values())
        cotas = {h: Fraction(restante * t, total) for h, t in pendentes.items()}
        base = {h: floor(cotas[h]) for h in pendentes}
        faltam = restante - sum(base.values())
        ordem = sorted(pendentes, key=lambda h: (-(cotas[h] - base[h]), h))
        for h in ordem[:faltam]:
            base[h] += 1
        alocacao.update(base)
    for h in tamanhos:
        alocacao.setdefault(h, 0)
    for h in sorted(tamanhos):
        if minimo_um and alocacao[h] == 0:
            doadora = max((d for d in alocacao if alocacao[d] > 1),
                          key=lambda d: (alocacao[d], tamanhos[d], d))
            alocacao[doadora] -= 1
            alocacao[h] = 1
    return alocacao


def _sortear(traces: list[dict], cases: dict[str, dict], n: int, seed: int,
             pedido: str, *, cobrir_todos: bool = True) -> list[str]:
    """Sorteio estratificado de n traces, no maximo um por caso."""
    por_caso: dict[str, list[str]] = defaultdict(list)
    for t in traces:
        por_caso[t["case_id"]].append(t["trace_id"])
    por_estrato: dict[str, list[str]] = defaultdict(list)
    for cid in por_caso:
        por_estrato[cases[cid]["hypothesis"][0]].append(cid)
    total = len(por_caso)
    if n > total:
        raise ValueError(f"{pedido}, existem {total} {DESCRICAO_ELEGIVEL}")
    # Na amostra inicial, toda hipotese aparece; na extensao (para achar mais reprovados), nao se exige.
    if cobrir_todos and n < len(por_estrato):
        raise ValueError(f"{pedido}, mas ha {len(por_estrato)} hipoteses com casos "
                         f"elegiveis; n precisa ser pelo menos {len(por_estrato)} "
                         "para cobrir todas")
    tamanhos = {h: len(cids) for h, cids in por_estrato.items()}
    alocacao = _alocar(tamanhos, n, minimo_um=cobrir_todos)
    rng = random.Random(seed)
    escolhidos: list[str] = []
    for h in sorted(por_estrato):
        cids = sorted(por_estrato[h])
        rng.shuffle(cids)
        for cid in cids[:alocacao[h]]:
            escolhidos.append(rng.choice(sorted(por_caso[cid])))
    return sorted(escolhidos)


def draw_blind_sample(traces: list[dict], cases: dict[str, dict], *,
                      n: int = 30, seed: int) -> list[str]:
    if n < 1:
        raise ValueError(f"n precisa ser pelo menos 1, veio {n}")
    return _sortear(eligible(traces, cases), cases, n, seed, f"pedidos {n}")


def extend_blind_sample(current: list[str], traces: list[dict],
                        cases: dict[str, dict], *, n_more: int, seed: int) -> list[str]:
    if n_more < 1:
        raise ValueError(f"n_more precisa ser pelo menos 1, veio {n_more}")
    elegiveis = eligible(traces, cases)
    por_id = {t["trace_id"]: t for t in elegiveis}
    for tid in current:
        if tid not in por_id:
            raise ValueError(f"{tid} nao e elegivel (teste, status ok) "
                             "e nao pode estar na amostra")
    casos_atuais = [por_id[tid]["case_id"] for tid in current]
    if len(set(casos_atuais)) != len(casos_atuais):
        raise ValueError("a amostra atual tem mais de um trace do mesmo caso")
    ja = set(casos_atuais)
    disponiveis = [t for t in elegiveis if t["case_id"] not in ja]
    novos = _sortear(disponiveis, cases, n_more, seed,
                     f"pedidos {n_more} novos (fora da amostra atual)", cobrir_todos=False)
    return list(current) + novos


def draw_consistency_sample(blind: list[str], *, n: int = 10, seed: int) -> list[str]:
    if len(set(blind)) != len(blind):
        raise ValueError("a amostra cega tem ids repetidos")
    if n < 1:
        raise ValueError(f"n precisa ser pelo menos 1, veio {n}")
    if n > len(blind):
        raise ValueError(f"pedidos {n}, mas a amostra cega tem {len(blind)} traces")
    rng = random.Random(seed)
    return sorted(rng.sample(sorted(blind), n))


def load_samples(path: Path) -> dict:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _gravar(path: Path, dados: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    texto = json.dumps(dados, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    path.write_text(texto, encoding="utf-8")


def record_blind(path: Path, *, seed: int, n: int, trace_ids: list[str]) -> None:
    dados = load_samples(path)
    if "blind" in dados:
        raise ValueError("a amostra cega ja foi registrada; ela e sorteada uma vez so")
    dados["blind"] = {"seed": seed, "n": n, "trace_ids": sorted(trace_ids)}
    _gravar(path, dados)


def record_extension(path: Path, *, seed: int, n_more: int,
                     trace_ids_added: list[str]) -> None:
    dados = load_samples(path)
    if "blind" not in dados:
        raise ValueError("registre a amostra cega antes de estender")
    ja = set(dados["blind"]["trace_ids"])
    for ext in dados.get("extensions", []):
        ja.update(ext["trace_ids_added"])
    repetidos = sorted(set(trace_ids_added) & ja)
    if repetidos:
        raise ValueError(f"ids ja presentes na amostra: {', '.join(repetidos)}")
    dados.setdefault("extensions", []).append(
        {"seed": seed, "n_more": n_more, "trace_ids_added": sorted(trace_ids_added)})
    _gravar(path, dados)


def record_consistency(path: Path, *, seed: int, n: int, trace_ids: list[str]) -> None:
    dados = load_samples(path)
    if "consistency" in dados:
        raise ValueError("a amostra de consistencia ja foi registrada")
    if "blind" not in dados:
        raise ValueError("registre a amostra cega antes da consistencia")
    permitidos = set(dados["blind"]["trace_ids"])
    for ext in dados.get("extensions", []):
        permitidos.update(ext["trace_ids_added"])
    fora = sorted(set(trace_ids) - permitidos)
    if fora:
        raise ValueError(f"ids fora da amostra cega (inclui extensoes): {', '.join(fora)}")
    dados["consistency"] = {"seed": seed, "n": n, "trace_ids": sorted(trace_ids)}
    _gravar(path, dados)


def load_traces(traces_dir: Path) -> list[dict]:
    return [load_trace(p) for p in sorted(traces_dir.rglob("*.json"))
            if TRACE_NAME_RE.match(p.name)]


def _ids_da_amostra(dados: dict) -> list[str]:
    ids = list(dados["blind"]["trace_ids"])
    for ext in dados.get("extensions", []):
        ids.extend(ext["trace_ids_added"])
    return ids


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m evals.sampling")
    sub = parser.add_subparsers(dest="comando", required=True)

    def comum(p: argparse.ArgumentParser) -> None:
        p.add_argument("--seed", type=int, required=True)
        p.add_argument("--traces-dir", type=Path, default=Path("traces"))
        p.add_argument("--cases-dir", type=Path, default=Path("cases"))
        p.add_argument("--out", type=Path, default=Path("annotations/_samples.json"))

    p_blind = sub.add_parser("blind", help="sorteia a amostra cega (uma vez)")
    comum(p_blind)
    p_blind.add_argument("--n", type=int, default=30)

    p_ext = sub.add_parser("extend", help="acrescenta traces a amostra cega")
    comum(p_ext)
    p_ext.add_argument("--n-more", type=int, required=True)

    p_cons = sub.add_parser("consistency", help="sorteia a amostra de consistencia")
    comum(p_cons)
    p_cons.add_argument("--n", type=int, default=10)

    args = parser.parse_args(argv)
    try:
        cases = {c["case_id"]: c for c in load_cases(args.cases_dir)}
        traces = load_traces(args.traces_dir)
        if args.comando == "blind":
            ids = draw_blind_sample(traces, cases, n=args.n, seed=args.seed)
            record_blind(args.out, seed=args.seed, n=args.n, trace_ids=ids)
        elif args.comando == "extend":
            dados = load_samples(args.out)
            if "blind" not in dados:
                raise ValueError("nao ha amostra cega registrada; rode 'blind' antes")
            atuais = _ids_da_amostra(dados)
            resultado = extend_blind_sample(atuais, traces, cases,
                                            n_more=args.n_more, seed=args.seed)
            ids = resultado[len(atuais):]
            record_extension(args.out, seed=args.seed, n_more=args.n_more,
                             trace_ids_added=ids)
        else:
            dados = load_samples(args.out)
            if "blind" not in dados:
                raise ValueError("nao ha amostra cega registrada; rode 'blind' antes")
            ids = draw_consistency_sample(_ids_da_amostra(dados), n=args.n,
                                          seed=args.seed)
            record_consistency(args.out, seed=args.seed, n=args.n, trace_ids=ids)
    except (ValueError, OSError) as e:
        print(f"erro: {e}", file=sys.stderr)
        return 1
    for tid in ids:
        print(tid)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
