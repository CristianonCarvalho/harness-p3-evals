"""Testes do transcritor do formulario (evals/annotate.py). Nada aqui chama modelo ou rede; tudo fica em tmp_path."""
import json
import random
import re
from pathlib import Path

import pytest

from evals.annotate import FormError, annotate, find_trace, main, parse_dossier_annotation
from evals.annotation import load_annotation
from evals.dossier import build_dossier
from evals.privacy import make_synthetic_cpf

TID = "c01-aaaa1111"
DATA = "2026-11-12"


def make_trace(**over) -> dict:
    base = {
        "trace_id": TID, "case_id": "c01", "status": "ok",
        "source": {"harness": "claude-code", "version": "x"},
        "model": "modelo-x",
        "conditions": {"skill": True, "hook": True, "server": "local",
                       "p2_tag": "step-16", "corpus_version": "abc"},
        "question": "Desde quando a CBS pode ser cobrada?",
        "events": [],
        "final_answer": "Resposta sem citacoes.",
        "usage": {"input_tokens": 1, "output_tokens": 2, "cost_usd": 0.0, "duration_ms": 10},
    }
    base.update(over)
    return base


def make_case(**over) -> dict:
    base = {
        "case_id": "c01", "question": "Desde quando a CBS pode ser cobrada?",
        "hypothesis": ["H4"], "split": None, "subsets": [],
        "gabarito": {"answer_exists": "sim", "expected_provisions": ["ADCT.art126"],
                     "reference_date": "2027-01-01", "disputed": False},
    }
    base.update(over)
    return base


def setup_env(tmp_path: Path, trace: dict | None = None, case: dict | None = None) -> dict:
    """Grava trace e caso em tmp_path e devolve os argumentos de diretorio para annotate/main."""
    trace = trace or make_trace()
    case = case or make_case()
    sub = tmp_path / "traces" / "2026-11"
    sub.mkdir(parents=True)
    (sub / f"{trace['trace_id']}.json").write_text(json.dumps(trace, ensure_ascii=False), encoding="utf-8")
    cases = tmp_path / "cases"
    cases.mkdir()
    (cases / f"{case['case_id']}.json").write_text(json.dumps(case, ensure_ascii=False), encoding="utf-8")
    return {"traces_dir": tmp_path / "traces", "cases_dir": cases,
            "annotations_dir": tmp_path / "annotations"}


def gera(trace=None, case=None, *, mode="cega", draft=None, draft_path=None) -> str:
    """Dossie gerado pelo proprio build_dossier: se o formato divergir, os testes quebram."""
    return build_dossier(trace or make_trace(), case or make_case(), mode=mode,
                         draft=draft, draft_path=draft_path)


def preencher(md: str, **valores) -> str:
    """Preenche o formulario por substituicao: 'CHAVE:' vira 'CHAVE: valor' na linha da chave."""
    for chave, valor in valores.items():
        md, n = re.subn(rf"^{chave}:.*$", lambda m: f"{chave}: {valor}".rstrip(), md,
                        count=1, flags=re.M)
        assert n == 1, f"linha {chave}: ausente no formulario"
    return md


def grava_dossie(tmp_path: Path, md: str) -> Path:
    path = tmp_path / "traces" / "dossies" / f"{TID}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(md, encoding="utf-8")
    return path


def numero_da_linha(md: str, linha: str) -> int:
    """Numero (1-based) da primeira linha do arquivo que e exatamente igual a 'linha'."""
    return md.split("\n").index(linha) + 1


def nada_gravado(annotations_dir: Path) -> bool:
    return not annotations_dir.exists() or not any(annotations_dir.iterdir())


def kw(env: dict) -> dict:
    return {"annotations_dir": env["annotations_dir"], "traces_dir": env["traces_dir"],
            "cases_dir": env["cases_dir"]}


def preenchido_cega(**extra) -> str:
    base = dict(C1="fail", note="A resposta não cita o dispositivo devolvido.", C2="pass", C3="pass")
    base.update(extra)
    return preencher(gera(), **base)


# 1. Cega preenchida corretamente -> v1 com os veredictos certos
def test_cega_preenchida_grava_v1(tmp_path):
    env = setup_env(tmp_path)
    dossie = grava_dossie(tmp_path, preenchido_cega())

    path = annotate(dossie, date=DATA, **kw(env))

    assert path == env["annotations_dir"] / f"{TID}.v1.json"
    ann = load_annotation(env["annotations_dir"], TID)
    assert ann["verdicts"] == {"C1": "fail", "C2": "pass", "C3": "pass", "C4": "n/a"}
    assert ann["note"] == "A resposta não cita o dispositivo devolvido."
    assert ann["uncertain"] == []
    assert ann["kind"] == "blind"
    assert ann["draft"] is None
    assert ann["version"] == 1
    assert ann["date"] == DATA


# 2. Rodar duas vezes no mesmo dossie -> v1 e v2
def test_mesmo_dossie_duas_vezes_gera_v1_e_v2(tmp_path):
    env = setup_env(tmp_path)
    dossie = grava_dossie(tmp_path, preenchido_cega())

    p1 = annotate(dossie, date=DATA, **kw(env))
    p2 = annotate(dossie, date=DATA, **kw(env))

    assert p1 == env["annotations_dir"] / f"{TID}.v1.json"
    assert p2 == env["annotations_dir"] / f"{TID}.v2.json"
    assert p1.exists() and p2.exists()


# 3. Veredito em branco -> FormError com o nome do criterio e a linha certa; nada gravado
def test_veredito_em_branco_aponta_linha_e_nao_grava(tmp_path):
    env = setup_env(tmp_path)
    md = preencher(gera(), C1="fail", note="x", C2="", C3="pass")
    dossie = grava_dossie(tmp_path, md)
    n = numero_da_linha(md, "C2:")

    with pytest.raises(FormError) as exc:
        annotate(dossie, date=DATA, **kw(env))

    assert f"{dossie}:{n}: C2 em branco" in str(exc.value)
    assert nada_gravado(env["annotations_dir"])


# 4. Veredito "sim" -> erro do validador repassado; nada gravado
def test_veredito_invalido_passa_erro_do_validador(tmp_path):
    env = setup_env(tmp_path)
    dossie = grava_dossie(tmp_path, preenchido_cega(C1="sim"))

    with pytest.raises(ValueError) as exc:
        annotate(dossie, date=DATA, **kw(env))

    msg = str(exc.value)
    assert "C1" in msg and "'sim'" in msg
    assert nada_gravado(env["annotations_dir"])


# 5. Nota com CPF sintetico -> erro do validador, sem repetir o numero; nada gravado
def test_nota_com_cpf_e_recusada_sem_ecoar_o_numero(tmp_path):
    env = setup_env(tmp_path)
    cpf = make_synthetic_cpf(random.Random(5))
    dossie = grava_dossie(tmp_path, preenchido_cega(note=f"A resposta citou o CPF {cpf}."))

    with pytest.raises(ValueError) as exc:
        annotate(dossie, date=DATA, **kw(env))

    msg = str(exc.value)
    assert "note" in msg
    assert cpf not in msg
    assert nada_gravado(env["annotations_dir"])


# 6. Revisada -> kind "revised" e o caminho do rascunho
def test_revisada_grava_kind_revised_com_draft(tmp_path):
    env = setup_env(tmp_path)
    draft = {"C1": "fail", "C2": "pass", "C3": "pass", "C4": "n/a"}
    dpath = f"drafts/annotations/{TID}.json"
    md = gera(mode="revisada", draft=draft, draft_path=dpath)
    md = preencher(md, C1="fail", note="Citação sem lastro.", C2="pass", C3="pass")
    dossie = grava_dossie(tmp_path, md)

    annotate(dossie, date=DATA, **kw(env))

    ann = load_annotation(env["annotations_dir"], TID)
    assert ann["kind"] == "revised"
    assert ann["draft"] == dpath


# 7. Markdown sem o bloco anotacao -> FormError "ausente"; nada gravado
def test_sem_bloco_anotacao_e_erro(tmp_path):
    env = setup_env(tmp_path)
    dossie = grava_dossie(tmp_path, "# Dossiê\n\nsem formulário nenhum\n")

    with pytest.raises(FormError, match="ausente"):
        annotate(dossie, date=DATA, **kw(env))

    assert nada_gravado(env["annotations_dir"])


# 8. Chave repetida e chave desconhecida -> FormError com as duas, cada uma com a sua linha
def test_chave_repetida_e_desconhecida_sao_reportadas_com_linha(tmp_path):
    env = setup_env(tmp_path)
    linhas = preenchido_cega().split("\n")
    i_c1 = linhas.index("C1: fail")
    linhas.insert(i_c1 + 1, "C1: pass")            # segunda C1, logo abaixo da primeira
    i_c4 = linhas.index("C4: n/a")
    linhas.insert(i_c4 + 1, "C5: pass")            # chave que nao existe
    md = "\n".join(linhas)
    dossie = grava_dossie(tmp_path, md)
    n_repetida = md.split("\n").index("C1: pass") + 1
    n_desconhecida = md.split("\n").index("C5: pass") + 1

    with pytest.raises(FormError) as exc:
        annotate(dossie, date=DATA, **kw(env))

    msg = str(exc.value)
    assert len(exc.value.errors) >= 2
    assert f"{dossie}:{n_repetida}: " in msg and "C1" in msg and "repetida" in msg
    assert f"{dossie}:{n_desconhecida}: " in msg and "C5" in msg
    assert nada_gravado(env["annotations_dir"])


# 9. Nota com varias linhas e uma em branco no meio: preservada com as quebras
def test_nota_multilinha_preserva_quebras(tmp_path):
    env = setup_env(tmp_path)
    nota = "primeira linha\n\nterceira linha"
    dossie = grava_dossie(tmp_path, preenchido_cega(note=nota))

    annotate(dossie, date=DATA, **kw(env))

    assert load_annotation(env["annotations_dir"], TID)["note"] == nota


# 10. Variantes de uncertain
@pytest.mark.parametrize("valor, esperado", [
    ("", []),
    ("C2", ["C2"]),
    ("C2, C3", ["C2", "C3"]),
    ("[C2 C3]", ["C2", "C3"]),
])
def test_uncertain_variantes(valor, esperado):
    md = preencher(gera(), C1="fail", note="dúvida registrada", C2="pass", C3="pass", uncertain=valor)

    assert parse_dossier_annotation(md, source="x")["uncertain"] == esperado


# 11. Trace ou caso inexistente -> main devolve 1 com mensagem clara no stderr
def test_trace_nao_encontrado_retorna_1(tmp_path, capsys):
    env = setup_env(tmp_path)
    dossie = grava_dossie(tmp_path, preenchido_cega())
    vazio = tmp_path / "vazio"
    vazio.mkdir()

    rc = main([str(dossie), "--date", DATA, "--annotations-dir", str(env["annotations_dir"]),
               "--traces-dir", str(vazio), "--cases-dir", str(env["cases_dir"])])

    assert rc == 1
    err = capsys.readouterr().err
    assert "trace não encontrado" in err and f"{TID}.json" in err
    assert nada_gravado(env["annotations_dir"])


def test_caso_nao_encontrado_retorna_1(tmp_path, capsys):
    env = setup_env(tmp_path)
    dossie = grava_dossie(tmp_path, preenchido_cega())
    sem_casos = tmp_path / "sem-casos"
    sem_casos.mkdir()

    rc = main([str(dossie), "--date", DATA, "--annotations-dir", str(env["annotations_dir"]),
               "--traces-dir", str(env["traces_dir"]), "--cases-dir", str(sem_casos)])

    assert rc == 1
    assert "caso não encontrado" in capsys.readouterr().err
    assert nada_gravado(env["annotations_dir"])


def test_main_sucesso_imprime_caminho_e_retorna_0(tmp_path, capsys):
    env = setup_env(tmp_path)
    dossie = grava_dossie(tmp_path, preenchido_cega())

    rc = main([str(dossie), "--date", DATA, "--annotations-dir", str(env["annotations_dir"]),
               "--traces-dir", str(env["traces_dir"]), "--cases-dir", str(env["cases_dir"])])

    assert rc == 0
    assert f"{TID}.v1.json" in capsys.readouterr().out


# 12. --date e obrigatoria: nunca vem do relogio
def test_main_sem_date_falha_no_argparse(tmp_path):
    env = setup_env(tmp_path)
    dossie = grava_dossie(tmp_path, preenchido_cega())

    with pytest.raises(SystemExit) as exc:
        main([str(dossie), "--annotations-dir", str(env["annotations_dir"]),
              "--traces-dir", str(env["traces_dir"]), "--cases-dir", str(env["cases_dir"])])

    assert exc.value.code != 0
    assert nada_gravado(env["annotations_dir"])


# 13. O dict analisado nunca traz version nem date
def test_dict_analisado_nao_tem_version_nem_date():
    resultado = parse_dossier_annotation(preenchido_cega(), source="x")

    assert set(resultado) == {"trace_id", "verdicts", "note", "uncertain", "kind", "draft"}
    assert set(resultado["verdicts"]) == {"C1", "C2", "C3", "C4"}
    assert "version" not in resultado and "date" not in resultado


# --- estrutura do formulario (extras de decisao) ----------------------------------------

def test_parse_valores_e_draft_vazio_vira_none():
    resultado = parse_dossier_annotation(preenchido_cega(), source="x")

    assert resultado["trace_id"] == TID
    assert resultado["kind"] == "blind"
    assert resultado["draft"] is None
    assert resultado["verdicts"]["C1"] == "fail"
    assert resultado["note"] == "A resposta não cita o dispositivo devolvido."


def test_veredito_e_mantido_como_escrito():
    resultado = parse_dossier_annotation(preenchido_cega(C2="Pass"), source="x")

    assert resultado["verdicts"]["C2"] == "Pass"


def test_chave_ausente_e_reportada_sem_linha():
    linhas = [ln for ln in preenchido_cega().split("\n") if not ln.startswith("uncertain:")]

    with pytest.raises(FormError) as exc:
        parse_dossier_annotation("\n".join(linhas), source="x")

    assert any("uncertain" in e and "ausente" in e for e in exc.value.errors)


def test_linha_sem_dois_pontos_e_reportada_com_linha():
    md = preenchido_cega().replace("C2: pass\n", "C2: pass\nsolto\n", 1)
    n = md.split("\n").index("solto") + 1

    with pytest.raises(FormError) as exc:
        parse_dossier_annotation(md, source="x")

    assert f"x:{n}: " in str(exc.value)


def test_trace_id_e_kind_em_branco_sao_erros():
    md = preencher(gera(), C1="fail", note="x", C2="pass", C3="pass", kind="", trace_id="")

    with pytest.raises(FormError) as exc:
        parse_dossier_annotation(md, source="x")

    msg = str(exc.value)
    assert "trace_id em branco" in msg
    assert "kind em branco" in msg


def test_bloco_duplicado_e_erro():
    md = preenchido_cega()
    bloco = re.search(r"```anotacao\n.*?\n```", md, re.S).group(0)

    with pytest.raises(FormError):
        parse_dossier_annotation(md + "\n" + bloco + "\n", source="x")


def test_chave_desconhecida_com_cpf_nao_ecoa_o_numero():
    cpf = make_synthetic_cpf(random.Random(9))
    md = preenchido_cega().replace("C4: n/a\n", f"C4: n/a\n{cpf}: x\n", 1)

    with pytest.raises(FormError) as exc:
        parse_dossier_annotation(md, source="x")

    assert cpf not in str(exc.value)


def test_find_trace_duplicado_e_erro(tmp_path):
    for sub in ("a", "b"):
        (tmp_path / sub).mkdir()
        (tmp_path / sub / f"{TID}.json").write_text("{}", encoding="utf-8")

    with pytest.raises(ValueError):
        find_trace(tmp_path, TID)


def test_find_trace_inexistente_e_erro(tmp_path):
    with pytest.raises(FileNotFoundError):
        find_trace(tmp_path, TID)


# --- da revisao da sessao principal -------------------------------------------------

def test_bloco_sem_cerca_de_fechamento_e_erro_claro():
    md = preenchido_cega()
    corte = md.rindex("```")  # a cerca que fecha o bloco anotacao
    with pytest.raises(FormError) as exc:
        parse_dossier_annotation(md[:corte], source="x")
    assert "fechamento" in str(exc.value)


def test_erro_do_validador_com_ponto_e_virgula_sai_numa_linha_so(tmp_path, capsys):
    # A mensagem de CPF do validador tem "(CPF/CNPJ); remova": nao pode virar duas linhas.
    env = setup_env(tmp_path)
    cpf = make_synthetic_cpf(random.Random(6))
    dossie = grava_dossie(tmp_path, preenchido_cega(note=f"Citou {cpf}."))
    codigo = main([str(dossie), "--date", DATA,
                   "--annotations-dir", str(env["annotations_dir"]),
                   "--traces-dir", str(env["traces_dir"]), "--cases-dir", str(env["cases_dir"])])
    err = capsys.readouterr().err
    assert codigo == 1
    linha = next(ln for ln in err.splitlines() if "CPF/CNPJ" in ln)
    assert "remova" in linha
    assert cpf not in err
