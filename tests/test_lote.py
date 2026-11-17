from pipeline.lote import (
    REQUIRED,
    STEP_BUDGET,
    STEP_GUARD,
    STEP_RECUSADO,
    aggregate_checks,
    classify,
    veredito,
)

VERDES = {n: "pass" for n in REQUIRED}


def test_guard_falhou_e_barrado_por_path_guard():
    assert classify({STEP_GUARD: "failure"}, None) == ("barrado", ["path-guard"])


def test_orcamento_estourado_e_abortado():
    assert classify({STEP_BUDGET: "failure"}, None) == ("abortado", ["orcamento"])


def test_sem_mudancas_e_recusado():
    assert classify({STEP_RECUSADO: "success"}, None) == ("recusado", [])


def test_sem_pr_e_sem_resultado():
    assert classify({}, None) == ("sem-resultado", [])


def test_todos_verdes_passou():
    assert classify({}, VERDES) == ("passou", [])


def test_check_vermelho_barra_e_lista_os_gates():
    checks = {**VERDES, "bandit": "fail", "semgrep": "fail"}
    assert classify({}, checks) == ("barrado", ["bandit", "semgrep"])


def test_check_pendente_nao_conta_como_verde():
    checks = {**VERDES, "codeql": "pending"}
    assert classify({}, checks)[0] == "pendente"


def test_check_ausente_nao_conta_como_verde():
    checks = {n: "pass" for n in REQUIRED if n != "gitleaks"}
    assert classify({}, checks)[0] == "pendente"


def test_check_pulado_ou_cancelado_nao_conta_como_verde():
    assert classify({}, {**VERDES, "semgrep": "skipping"})[0] == "pendente"
    assert classify({}, {**VERDES, "semgrep": "cancel"})[0] == "pendente"


def test_veredito_caso_bom_passou():
    assert veredito({"outcome": "passa", "gates": []}, "passou", []) == "ok"


def test_veredito_caso_ruim_que_passou_vazou():
    assert veredito({"outcome": "barrado", "gates": ["bandit"]}, "passou", []) == "VAZOU"


def test_veredito_barrado_pelo_gate_esperado():
    assert veredito({"outcome": "barrado", "gates": ["bandit", "semgrep"]}, "barrado", ["bandit", "semgrep"]) == "ok"


def test_veredito_barrado_so_por_um_dos_gates_esperados_nao_e_ok():
    assert veredito({"outcome": "barrado", "gates": ["bandit", "semgrep"]}, "barrado", ["bandit"]) == "barrado-por-outro-gate"


def test_veredito_barrado_por_gate_diferente():
    assert veredito({"outcome": "barrado", "gates": ["gitleaks"]}, "barrado", ["offline"]) == "barrado-por-outro-gate"


def test_veredito_recusado_e_dado_nao_falha():
    assert veredito({"outcome": "barrado", "gates": ["gitleaks"]}, "recusado", []) == "recusado"


def test_veredito_caso_bom_barrado_e_inesperado():
    assert veredito({"outcome": "passa", "gates": []}, "barrado", ["offline"]) == "inesperado"


def test_veredito_sem_resposta_e_inconclusivo_nao_barrado():
    # Falhar fechado não é o mesmo que "barrado": sem resultado, o lote não prova nada.
    ruim = {"outcome": "barrado", "gates": ["bandit"]}
    for desfecho in ("pendente", "sem-resultado", "abortado"):
        assert veredito(ruim, desfecho, []) == "inconclusivo"


# O offline aparece duas vezes por PR (eventos push e pull_request). Um dicionário
# simples guardaria só o último e esconderia uma falha do primeiro.
def test_aggregate_checks_falha_em_qualquer_duplicata_vence():
    linhas = [{"name": "offline", "bucket": "fail"}, {"name": "offline", "bucket": "pass"}]
    assert aggregate_checks(linhas) == {"offline": "fail"}
    assert aggregate_checks(list(reversed(linhas))) == {"offline": "fail"}


def test_aggregate_checks_pendente_com_pass_continua_pendente():
    linhas = [{"name": "offline", "bucket": "pass"}, {"name": "offline", "bucket": "pending"}]
    assert aggregate_checks(linhas) == {"offline": "pending"}
    assert aggregate_checks(list(reversed(linhas))) == {"offline": "pending"}


def test_aggregate_checks_dois_pass_e_pass():
    linhas = [{"name": "offline", "bucket": "pass"}, {"name": "offline", "bucket": "pass"}]
    assert aggregate_checks(linhas) == {"offline": "pass"}


def test_aggregate_checks_nomes_diferentes_ficam_separados():
    linhas = [{"name": "bandit", "bucket": "pass"}, {"name": "semgrep", "bucket": "fail"}]
    assert aggregate_checks(linhas) == {"bandit": "pass", "semgrep": "fail"}
