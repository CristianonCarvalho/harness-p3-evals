import random
from pathlib import Path

from evals.privacy import (
    find_taxpayer_ids, redact_taxpayer_ids, make_synthetic_cpf,
    make_synthetic_cnpj, is_valid_cpf, is_valid_cnpj, scan_files,
)


def _fmt_cpf(d: str) -> str:
    return f"{d[:3]}.{d[3:6]}.{d[6:9]}-{d[9:]}"


def test_generated_cpf_is_valid_and_has_11_digits():
    rng = random.Random(1)
    for _ in range(50):
        cpf = make_synthetic_cpf(rng)
        assert len(cpf) == 11 and cpf.isdigit()
        assert is_valid_cpf(cpf)


def test_generated_cnpj_is_valid_and_has_14_digits():
    rng = random.Random(2)
    for _ in range(50):
        cnpj = make_synthetic_cnpj(rng)
        assert len(cnpj) == 14 and cnpj.isdigit()
        assert is_valid_cnpj(cnpj)


def test_finds_bare_and_formatted_cpf():
    cpf = make_synthetic_cpf(random.Random(3))
    assert find_taxpayer_ids(f"meu cpf {cpf} ok") == [cpf]
    assert find_taxpayer_ids(f"meu cpf {_fmt_cpf(cpf)} ok") == [_fmt_cpf(cpf)]


def test_finds_bare_cnpj():
    cnpj = make_synthetic_cnpj(random.Random(4))
    assert find_taxpayer_ids(f"cnpj {cnpj}") == [cnpj]


def test_does_not_flag_dates_ids_or_hashes():
    texto = "2030-06-01 CF.art156-A.par1.incIX LC214.art125 c269388fb2bd53b0a326d2b8b516c592478e3a41d8f2c3bceb0bf51caaf41e3a"
    assert find_taxpayer_ids(texto) == []


def test_redact_removes_the_number():
    cpf = make_synthetic_cpf(random.Random(5))
    out = redact_taxpayer_ids(f"o numero {cpf} apareceu")
    assert cpf not in out and "[número removido]" in out


def test_scan_files_reports_offending_file(tmp_path: Path):
    cpf = make_synthetic_cpf(random.Random(6))
    ruim = tmp_path / "ruim.md"
    ruim.write_text(f"vazou {cpf}", encoding="utf-8")
    bom = tmp_path / "bom.md"
    bom.write_text("nada aqui", encoding="utf-8")
    assert [p for p, _ in scan_files([ruim, bom])] == [ruim]
