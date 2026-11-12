"""Transcreve o formulario do dossie para uma anotacao versionada.

Este modulo NAO decide nada: nao corrige, nao completa e nao chuta valor.
Ele so checa a ESTRUTURA do formulario. As regras de conteudo ficam em
evals/annotation.py (validate_annotation), que e quem grava.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from evals.annotation import write_annotation
from evals.cases import load_cases
from evals.privacy import redact_taxpayer_ids
from evals.trace import load_trace

_ABRE = "```anotacao"
_CHAVES = ("trace_id", "kind", "draft", "C1", "C2", "C3", "C4", "uncertain", "note")
_CRITERIOS = ("C1", "C2", "C3", "C4")
_PREFIXO_VALIDACAO = "anotação inválida: "


class FormError(ValueError):
    """Erros estruturais do formulario. `errors` traz todos, cada um com origem e linha."""

    def __init__(self, errors: list[str]):
        self.errors = list(errors)
        super().__init__("\n".join(self.errors))


def _incertos(valor: str) -> list[str]:
    """Itens de uncertain, como escritos. Aceita '[C2 C3]', 'C2, C3' ou vazio."""
    v = valor.strip()
    if v.startswith("["):
        v = v[1:]
    if v.endswith("]"):
        v = v[:-1]
    return [p for p in re.split(r"[,\s]+", v.strip()) if p]


def parse_dossier_annotation(markdown: str, *, source: str = "<dossiê>") -> dict:
    """Le o bloco 'anotacao' do dossie e devolve o dict da anotacao (sem version nem date).

    Junta todos os erros estruturais e levanta FormError no fim, cada um com a linha.
    """
    linhas = [ln[:-1] if ln.endswith("\r") else ln for ln in markdown.split("\n")]
    aberturas = [i for i, ln in enumerate(linhas) if ln.rstrip() == _ABRE]
    if not aberturas:
        raise FormError([f"{source}: seção 'Sua anotação' (bloco anotacao) ausente"])
    if len(aberturas) > 1:
        raise FormError([f"{source}: {len(aberturas)} blocos anotacao; deixe só um"])
    ini = aberturas[0] + 1
    fim = next((i for i in range(ini, len(linhas)) if linhas[i].strip() == "```"), None)
    if fim is None:
        raise FormError([f"{source}: bloco anotacao sem a cerca de fechamento"])

    erros: list[str] = []
    valores: dict[str, str] = {}
    linha_de: dict[str, int] = {}
    nota_linhas: list[str] | None = None  # depois de 'note:', tudo e texto da nota
    for i in range(ini, fim):
        ln = linhas[i]
        n = i + 1
        if nota_linhas is not None:
            nota_linhas.append(ln)
            continue
        if not ln.strip():
            continue
        if ":" not in ln:
            erros.append(f"{source}:{n}: linha sem 'chave: valor'")
            continue
        chave, _, resto = ln.partition(":")
        chave = chave.strip()
        if chave not in _CHAVES:
            # Ecoa a chave sem o numero de documento, caso alguem tenha escrito um no lugar dela.
            erros.append(f"{source}:{n}: chave desconhecida {redact_taxpayer_ids(chave)!r}")
            continue
        if chave in linha_de:
            erros.append(f"{source}:{n}: chave repetida {chave!r}")
            continue
        linha_de[chave] = n
        if chave == "note":
            nota_linhas = [resto.strip()]
        else:
            valores[chave] = resto.strip()

    for chave in _CHAVES:
        if chave not in linha_de:
            erros.append(f"{source}: bloco anotacao: chave ausente {chave!r}")
    for chave in ("trace_id", "kind", *_CRITERIOS):
        if chave in linha_de and not valores[chave]:
            erros.append(f"{source}:{linha_de[chave]}: {chave} em branco")
    if erros:
        raise FormError(erros)

    nota = "\n".join(nota_linhas).strip() if nota_linhas is not None else ""
    draft = valores["draft"] or None
    return {
        "trace_id": valores["trace_id"],
        "verdicts": {c: valores[c] for c in _CRITERIOS},
        "note": nota,
        "uncertain": _incertos(valores["uncertain"]),
        "kind": valores["kind"],
        "draft": draft,
    }


def find_trace(traces_dir: Path, trace_id: str) -> Path:
    """Acha <trace_id>.json em qualquer subpasta de traces_dir. Exige um so."""
    achados = sorted(traces_dir.rglob(f"{trace_id}.json"))
    if not achados:
        raise FileNotFoundError(f"trace não encontrado: {trace_id}.json em {traces_dir}")
    if len(achados) > 1:
        lugares = ", ".join(str(p) for p in achados)
        raise ValueError(f"trace duplicado: {trace_id}.json aparece em {len(achados)} lugares: {lugares}")
    return achados[0]


def annotate(dossier_path: Path, *, date: str, annotations_dir: Path,
             traces_dir: Path, cases_dir: Path) -> Path:
    """Transcreve o formulario do dossie e grava a anotacao versionada. Devolve o caminho."""
    markdown = dossier_path.read_text(encoding="utf-8")
    ann = parse_dossier_annotation(markdown, source=str(dossier_path))
    trace = load_trace(find_trace(traces_dir, ann["trace_id"]))
    casos = [c for c in load_cases(cases_dir) if c.get("case_id") == trace.get("case_id")]
    if not casos:
        raise FileNotFoundError(f"caso não encontrado: {trace.get('case_id')!r} em {cases_dir}")
    if len(casos) > 1:
        raise ValueError(f"caso duplicado: {trace.get('case_id')!r} aparece {len(casos)} vezes em {cases_dir}")
    return write_annotation(ann, casos[0], trace, annotations_dir, date=date)


def _imprime_erros(exc: Exception) -> None:
    msg = str(exc)
    if msg.startswith(_PREFIXO_VALIDACAO):
        print(_PREFIXO_VALIDACAO.rstrip(), file=sys.stderr)
        # Separa so onde comeca outro erro ("<trace_id>: ..."): uma mensagem pode ter "; " dentro.
        for erro in re.split(r"; (?=[^\s;]+: )", msg[len(_PREFIXO_VALIDACAO):]):
            print(f"  {erro}", file=sys.stderr)
    else:
        print(msg, file=sys.stderr)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m evals.annotate",
        description="Transcreve o formulario 'Sua anotação' de um dossiê para a anotação versionada.")
    parser.add_argument("dossie", type=Path)
    parser.add_argument("--date", required=True,
                        help="data da anotação, AAAA-MM-DD (obrigatória: nunca vem do relógio)")
    parser.add_argument("--annotations-dir", type=Path, default=Path("annotations"))
    parser.add_argument("--traces-dir", type=Path, default=Path("traces"))
    parser.add_argument("--cases-dir", type=Path, default=Path("cases"))
    args = parser.parse_args(argv)
    try:
        path = annotate(args.dossie, date=args.date, annotations_dir=args.annotations_dir,
                        traces_dir=args.traces_dir, cases_dir=args.cases_dir)
    except FormError as exc:
        for erro in exc.errors:
            print(erro, file=sys.stderr)
        return 1
    except (ValueError, OSError) as exc:
        _imprime_erros(exc)
        return 1
    print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
