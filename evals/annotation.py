"""Validação e persistência de anotações."""
from __future__ import annotations

import json
import re
from datetime import date as dt_date
from pathlib import Path, PurePosixPath

from evals.privacy import find_taxpayer_ids


CRITERIA = ("C1", "C2", "C3", "C4")
ALWAYS_APPLICABLE = ("C1", "C2", "C3")
SECURITY_HYPOTHESES = ("H12", "H13")
VERDICTS = ("pass", "fail", "n/a")
KINDS = ("blind", "revised")


def validate_annotation(ann: dict, case: dict, trace: dict) -> list[str]:
    errors: list[str] = []
    tid = ann.get("trace_id", trace.get("trace_id", "<sem-trace>"))
    if "trace_id" not in ann:
        errors.append(f"{tid}: trace_id ausente na anotação")
    elif ann["trace_id"] != trace.get("trace_id"):
        errors.append(
            f"{tid}: trace_id da anotação ({ann.get('trace_id')!r}) difere do trace ({trace.get('trace_id')!r})"
        )
    if trace.get("case_id") != case.get("case_id"):
        errors.append(
            f"{tid}: case_id do trace ({trace.get('case_id')!r}) difere do caso ({case.get('case_id')!r})"
        )
    # Continua acumulando para reportar todos os erros da anotação de uma só vez.
    if trace.get("status") != "ok":
        errors.append(
            f"{tid}: trace com status {trace.get('status')!r} não se anota (apenas status 'ok')"
        )
    verdicts = ann.get("verdicts", {})
    for c in sorted(set(verdicts.keys()) - set(CRITERIA)):
        errors.append(f"{tid}: {c}: critério desconhecido")
    case_hyps = case.get("hypothesis", [])
    sec_hyps = [h for h in SECURITY_HYPOTHESES if h in case_hyps]
    c4_applies = bool(sec_hyps)
    for c in CRITERIA:
        if c not in verdicts:
            errors.append(f"{tid}: {c}: critério ausente")
        else:
            val = verdicts[c]
            if val not in VERDICTS:
                errors.append(
                    f"{tid}: {c}: veredito inválido {val!r} (use 'pass', 'fail' ou 'n/a')"
                )
            elif c in ALWAYS_APPLICABLE and val == "n/a":
                errors.append(f"{tid}: {c}: n/a, mas {c} sempre se aplica")
            elif c == "C4":
                if c4_applies and val == "n/a":
                    errors.append(
                        f"{tid}: C4: n/a, mas o caso tem {sec_hyps[0]}, e o C4 se aplica"
                    )
                elif not c4_applies and val != "n/a":
                    errors.append(
                        f"{tid}: C4: {val!r}, mas o C4 não se aplica (o caso não tem H12 nem H13)"
                    )
    if "kind" not in ann:
        errors.append(f"{tid}: kind: campo ausente")
    elif ann["kind"] not in KINDS:
        errors.append(
            f"{tid}: kind: valor inválido {ann['kind']!r} (use 'blind' ou 'revised')"
        )
    # Nota ausente ou não-string (ex: None ou int) é tratada como vazia.
    raw_note = ann.get("note")
    note = raw_note.strip() if isinstance(raw_note, str) else ""
    if isinstance(raw_note, str):
        docs = find_taxpayer_ids(raw_note)
        if docs:
            qtd = len(docs)
            s = "número" if qtd == 1 else "números"
            errors.append(
                f"{tid}: note: a nota contém {qtd} {s} de documento (CPF/CNPJ); remova antes de gravar"
            )
    fails = [c for c in CRITERIA if verdicts.get(c) == "fail"]
    if fails and not note:
        errors.append(f"{tid}: {', '.join(fails)}: fail exige nota explicativa")
    raw_uncertain = ann.get("uncertain", [])
    if "uncertain" in ann and not isinstance(raw_uncertain, list):
        errors.append(
            f"{tid}: uncertain: deve ser uma lista (recebeu {type(raw_uncertain).__name__})"
        )
        valid_uncertain: list[str] = []
    else:
        valid_uncertain = []
        for c in (raw_uncertain if isinstance(raw_uncertain, list) else []):
            if c not in CRITERIA:
                errors.append(f"{tid}: uncertain: critério desconhecido {c!r}")
            else:
                valid_uncertain.append(c)

    for c in valid_uncertain:
        if verdicts.get(c) == "n/a":
            errors.append(
                f"{tid}: {c}: em uncertain, mas está n/a (não se aplica, não há o que duvidar)"
            )
    if valid_uncertain and not note:
        errors.append(f"{tid}: {', '.join(valid_uncertain)}: uncertain exige nota explicativa")

    if ann.get("kind") in KINDS:
        kind = ann["kind"]
        draft = ann.get("draft")
        if kind == "revised":
            if draft is None:
                errors.append(f"{tid}: anotação revisada exige draft preenchido")
            elif (
                not isinstance(draft, str)
                or draft.startswith("/")
                or PurePosixPath(draft).parts != ("drafts", "annotations", f"{tid}.json")
            ):
                errors.append(f"{tid}: draft: caminho inválido {draft!r}")
        elif kind == "blind":
            if draft is not None:
                errors.append(f"{tid}: anotação cega não pode ter draft")
    return errors


_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def _validate_date_str(date_str: str) -> bool:
    if not isinstance(date_str, str) or not _DATE_RE.fullmatch(date_str):
        return False
    try:
        dt_date.fromisoformat(date_str)
        return True
    except ValueError:
        return False


def write_annotation(
    ann: dict,
    case: dict,
    trace: dict,
    annotations_dir: Path,
    *,
    date: str,
) -> Path:
    if "version" in ann or "date" in ann:
        campo = "version" if "version" in ann else "date"
        raise ValueError(
            f"anotação não pode conter {campo!r} pré-preenchido antes de gravar"
        )
    if not _validate_date_str(date):
        raise ValueError(f"data inválida {date!r} (formato esperado AAAA-MM-DD)")

    errors = validate_annotation(ann, case, trace)
    if errors:
        raise ValueError("anotação inválida: " + "; ".join(errors))

    tid = trace["trace_id"]
    pattern = re.compile(rf"{re.escape(tid)}\.v(\d+)\.json")
    existing_versions: list[int] = []
    if annotations_dir.exists():
        for p in annotations_dir.iterdir():
            if p.is_file():
                m = pattern.fullmatch(p.name)
                if m:
                    existing_versions.append(int(m.group(1)))

    next_version = max(existing_versions, default=0) + 1
    path = annotations_dir / f"{tid}.v{next_version}.json"

    payload = {**ann, "version": next_version, "date": date}
    annotations_dir.mkdir(parents=True, exist_ok=True)
    with open(path, "x", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    return path


def load_history(annotations_dir: Path, trace_id: str) -> list[dict]:
    if not annotations_dir.exists():
        return []

    pattern = re.compile(rf"{re.escape(trace_id)}\.v(\d+)\.json")
    files: list[tuple[int, Path]] = []
    seen_versions: set[int] = set()

    for p in annotations_dir.iterdir():
        if p.is_file():
            m = pattern.fullmatch(p.name)
            if m:
                v = int(m.group(1))
                if p.name != f"{trace_id}.v{v}.json":
                    raise ValueError(
                        f"{p.name}: nome de arquivo de anotação não-canônico (zeros à esquerda não permitidos)"
                    )
                if v in seen_versions:
                    raise ValueError(
                        f"{p.name}: versão {v} duplicada encontrada para o trace {trace_id}"
                    )
                seen_versions.add(v)
                files.append((v, p))

    files.sort(key=lambda x: x[0])
    history: list[dict] = []
    for expected_version, p in files:
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, ValueError) as exc:
            raise ValueError(f"{p.name}: JSON corrompido: {exc}") from exc

        if not isinstance(data, dict):
            raise ValueError(f"{p.name}: conteúdo JSON deve ser um objeto")
        if data.get("trace_id") != trace_id:
            raise ValueError(
                f"{p.name}: trace_id interno ({data.get('trace_id')!r}) diverge do arquivo ({trace_id!r})"
            )
        if "version" not in data or not isinstance(data["version"], int) or isinstance(data["version"], bool):
            raise ValueError(f"{p.name}: campo 'version' ausente ou inválido")
        if data["version"] != expected_version:
            raise ValueError(
                f"{p.name}: versão no arquivo ({data['version']}) diverge do nome ({expected_version})"
            )
        if not _validate_date_str(data.get("date", "")):
            raise ValueError(f"{p.name}: data inválida {data.get('date')!r}")
        history.append(data)
    return history


def load_annotation(annotations_dir: Path, trace_id: str) -> dict | None:
    history = load_history(annotations_dir, trace_id)
    return history[-1] if history else None


