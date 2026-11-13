import json
from collections import Counter

import pytest

from evals.sampling import (
    eligible, draw_blind_sample, extend_blind_sample, draw_consistency_sample,
    load_samples, record_blind, record_extension, record_consistency,
    load_traces, main,
)

# 12+10+8+6+4 = 40 casos. Um em cada dez fica em desenvolvimento.
HIPOTESES = [("H1", 12), ("H2", 10), ("H3", 8), ("H4", 6), ("H5", 4)]


def make_trace(case_id: str, sufixo: str, status: str) -> dict:
    return {"trace_id": f"{case_id}-{sufixo}", "case_id": case_id, "status": status}


def make_world():
    """40 casos, 2 traces por caso (com e sem skill), alguns com status erro."""
    cases, traces = {}, []
    hs = [h for h, k in HIPOTESES for _ in range(k)]
    for i, h in enumerate(hs):
        cid = f"c{i:02d}"
        split = "teste" if i % 10 < 7 else "desenvolvimento"
        hyp = [h, "H5"] if i % 3 == 0 and h != "H5" else [h]
        cases[cid] = {"case_id": cid, "question": "pergunta?", "hypothesis": hyp,
                      "split": split}
        traces.append(make_trace(cid, f"00{i:06x}", "erro" if i % 9 == 0 else "ok"))
        traces.append(make_trace(cid, f"01{i:06x}", "erro" if i % 5 == 0 else "ok"))
    return cases, traces


def make_flat_world(tamanhos: dict[str, int]):
    """Casos de teste, um trace ok por caso, com o numero de casos por hipotese dado."""
    cases, traces = {}, []
    i = 0
    for h, k in tamanhos.items():
        for _ in range(k):
            cid = f"f{i:03d}"
            cases[cid] = {"case_id": cid, "question": "pergunta?", "hypothesis": [h],
                          "split": "teste"}
            traces.append(make_trace(cid, f"02{i:06x}", "ok"))
            i += 1
    return cases, traces


def by_id(traces):
    return {t["trace_id"]: t for t in traces}


def n_casos_elegiveis(traces, cases) -> int:
    return len({t["case_id"] for t in eligible(traces, cases)})


def write_corpus(base, cases, traces):
    cdir, tdir = base / "cases", base / "traces"
    cdir.mkdir(parents=True)
    tdir.mkdir(parents=True)
    for c in cases.values():
        (cdir / f"{c['case_id']}.json").write_text(json.dumps(c), encoding="utf-8")
    for t in traces:
        (tdir / f"{t['trace_id']}.json").write_text(json.dumps(t), encoding="utf-8")
    return cdir, tdir


# --- elegibilidade ---------------------------------------------------------

def test_eligible_keeps_only_teste_ok_known_cases_sorted():
    cases, traces = make_world()
    traces = traces + [make_trace("zzz", "03000000", "ok")]  # caso desconhecido
    el = eligible(traces, cases)
    assert el
    assert all(cases[t["case_id"]]["split"] == "teste" for t in el)
    assert all(t["status"] == "ok" for t in el)
    assert all(t["case_id"] != "zzz" for t in el)
    ids = [t["trace_id"] for t in el]
    assert ids == sorted(ids)


# --- amostra cega -----------------------------------------------------------

def test_blind_never_draws_development_traces():
    cases, traces = make_world()
    tb = by_id(traces)
    for seed in range(5):
        for tid in draw_blind_sample(traces, cases, n=10, seed=seed):
            assert cases[tb[tid]["case_id"]]["split"] == "teste"


def test_blind_never_draws_non_ok_traces():
    cases, traces = make_world()
    tb = by_id(traces)
    for seed in range(5):
        for tid in draw_blind_sample(traces, cases, n=10, seed=seed):
            assert tb[tid]["status"] == "ok"


def test_blind_has_at_most_one_trace_per_case():
    cases, traces = make_world()
    tb = by_id(traces)
    amostra = draw_blind_sample(traces, cases, n=20, seed=3)
    casos = [tb[t]["case_id"] for t in amostra]
    assert len(set(casos)) == len(casos) == 20


def test_same_seed_same_sample_whatever_the_input_order():
    cases, traces = make_world()
    a = draw_blind_sample(traces, cases, n=10, seed=7)
    b = draw_blind_sample(list(reversed(traces)), cases, n=10, seed=7)
    c = draw_blind_sample(traces, dict(reversed(list(cases.items()))), n=10, seed=7)
    assert a == b == c
    assert a == sorted(a)


def test_different_seed_gives_different_sample():
    cases, traces = make_world()
    assert (draw_blind_sample(traces, cases, n=10, seed=7)
            != draw_blind_sample(traces, cases, n=10, seed=8))


def test_every_stratum_is_present_when_n_covers_them():
    cases, traces = make_world()
    tb = by_id(traces)
    estratos = {cases[t["case_id"]]["hypothesis"][0] for t in eligible(traces, cases)}
    assert len(estratos) == 5
    amostra = draw_blind_sample(traces, cases, n=5, seed=11)
    presentes = {cases[tb[t]["case_id"]]["hypothesis"][0] for t in amostra}
    assert presentes == estratos


def test_n_below_number_of_strata_raises_with_both_numbers():
    cases, traces = make_world()
    with pytest.raises(ValueError, match="4") as exc:
        draw_blind_sample(traces, cases, n=4, seed=1)
    assert "5" in str(exc.value)


def test_proportional_allocation_with_minimum_one():
    cases, traces = make_flat_world({"H1": 20, "H2": 10, "H3": 5})
    tb = by_id(traces)
    amostra = draw_blind_sample(traces, cases, n=7, seed=5)
    contagem = Counter(cases[tb[t]["case_id"]]["hypothesis"][0] for t in amostra)
    assert contagem == Counter({"H1": 4, "H2": 2, "H3": 1})


def test_largest_remainder_gets_the_leftover_slot():
    # 7/5/3 casos e n=6: cotas 2,8 / 2,0 / 1,2. A vaga que sobra vai para o maior resto (H1).
    cases, traces = make_flat_world({"H1": 7, "H2": 5, "H3": 3})
    tb = by_id(traces)
    amostra = draw_blind_sample(traces, cases, n=6, seed=5)
    contagem = Counter(cases[tb[t]["case_id"]]["hypothesis"][0] for t in amostra)
    assert contagem == Counter({"H1": 3, "H2": 2, "H3": 1})


def test_small_stratum_takes_all_when_n_equals_total():
    cases, traces = make_world()
    el = eligible(traces, cases)
    total = n_casos_elegiveis(traces, cases)
    amostra = draw_blind_sample(traces, cases, n=total, seed=2)
    tb = by_id(traces)
    assert {tb[t]["case_id"] for t in amostra} == {t["case_id"] for t in el}


def test_n_more_than_existing_cases_raises_with_the_count():
    cases, traces = make_world()
    total = n_casos_elegiveis(traces, cases)
    with pytest.raises(ValueError, match=f"existem {total} casos elegiveis"):
        draw_blind_sample(traces, cases, n=total + 1, seed=1)


# --- extensao ---------------------------------------------------------------

def test_extend_keeps_current_as_prefix_and_adds_new_cases():
    cases, traces = make_world()
    tb = by_id(traces)
    current = draw_blind_sample(traces, cases, n=8, seed=1)
    extended = extend_blind_sample(current, traces, cases, n_more=5, seed=2)
    assert extended[:len(current)] == current
    assert len(extended) == 13
    novos = extended[len(current):]
    assert novos == sorted(novos)
    casos = [tb[t]["case_id"] for t in extended]
    assert len(set(casos)) == len(casos)


def test_extend_with_fewer_new_traces_than_strata_is_allowed():
    # Estender serve para achar mais reprovados: pedir 2 a mais com 5 hipoteses tem de funcionar.
    cases, traces = make_world()
    current = draw_blind_sample(traces, cases, n=8, seed=1)
    extended = extend_blind_sample(current, traces, cases, n_more=2, seed=2)
    assert extended[:len(current)] == current
    assert len(extended) == 10


def test_extend_rejects_current_ids_that_are_not_eligible():
    cases, traces = make_world()
    tb = by_id(traces)
    dev = next(t["trace_id"] for t in traces
               if cases[t["case_id"]]["split"] == "desenvolvimento")
    erro = next(t["trace_id"] for t in traces
                if t["status"] == "erro" and cases[t["case_id"]]["split"] == "teste")
    assert dev in tb and erro in tb
    with pytest.raises(ValueError):
        extend_blind_sample([dev], traces, cases, n_more=1, seed=1)
    with pytest.raises(ValueError):
        extend_blind_sample([erro], traces, cases, n_more=1, seed=1)


def test_extend_not_enough_cases_raises_with_the_count():
    cases, traces = make_world()
    current = draw_blind_sample(traces, cases, n=8, seed=1)
    restantes = n_casos_elegiveis(traces, cases) - len(current)
    with pytest.raises(ValueError, match=str(restantes)):
        extend_blind_sample(current, traces, cases, n_more=restantes + 1, seed=1)


# --- amostra de consistencia ----------------------------------------------

def test_consistency_is_sorted_subset_of_blind():
    cases, traces = make_world()
    blind = sorted(draw_blind_sample(traces, cases, n=20, seed=3))
    cons = draw_consistency_sample(blind, n=10, seed=4)
    assert len(cons) == 10
    assert set(cons) <= set(blind)
    assert cons == sorted(cons)


def test_consistency_more_than_blind_raises_with_counts():
    blind = [f"c{i:02d}-00000000" for i in range(10)]
    with pytest.raises(ValueError, match="11") as exc:
        draw_consistency_sample(blind, n=11, seed=1)
    assert "10" in str(exc.value)


def test_consistency_rejects_duplicates_in_blind():
    blind = ["c01-00000000", "c01-00000000", "c02-00000000"]
    with pytest.raises(ValueError):
        draw_consistency_sample(blind, n=2, seed=1)


# --- persistencia -----------------------------------------------------------

BLIND_IDS = ["c01-00000001", "c02-00000002", "c03-00000003"]


def test_record_blind_writes_and_refuses_second_draw(tmp_path):
    path = tmp_path / "annotations" / "_samples.json"
    record_blind(path, seed=1, n=3, trace_ids=BLIND_IDS)
    assert load_samples(path) == {
        "blind": {"seed": 1, "n": 3, "trace_ids": BLIND_IDS}}
    with pytest.raises(ValueError):
        record_blind(path, seed=2, n=3, trace_ids=BLIND_IDS)


def test_record_extension_before_blind_raises(tmp_path):
    with pytest.raises(ValueError):
        record_extension(tmp_path / "s.json", seed=1, n_more=1,
                         trace_ids_added=["c04-00000004"])


def test_record_extension_appends(tmp_path):
    path = tmp_path / "s.json"
    record_blind(path, seed=1, n=3, trace_ids=BLIND_IDS)
    record_extension(path, seed=2, n_more=1, trace_ids_added=["c04-00000004"])
    record_extension(path, seed=3, n_more=1, trace_ids_added=["c05-00000005"])
    ext = load_samples(path)["extensions"]
    assert [e["trace_ids_added"] for e in ext] == [["c04-00000004"], ["c05-00000005"]]


def test_record_consistency_must_be_inside_blind_and_extensions(tmp_path):
    path = tmp_path / "s.json"
    record_blind(path, seed=1, n=3, trace_ids=BLIND_IDS)
    record_extension(path, seed=2, n_more=1, trace_ids_added=["c04-00000004"])
    with pytest.raises(ValueError):
        record_consistency(path, seed=5, n=2,
                           trace_ids=["c01-00000001", "c09-00000009"])
    record_consistency(path, seed=5, n=2, trace_ids=["c01-00000001", "c04-00000004"])
    assert load_samples(path)["consistency"]["trace_ids"] == ["c01-00000001", "c04-00000004"]


def test_record_consistency_twice_raises(tmp_path):
    path = tmp_path / "s.json"
    record_blind(path, seed=1, n=3, trace_ids=BLIND_IDS)
    record_consistency(path, seed=5, n=1, trace_ids=["c01-00000001"])
    with pytest.raises(ValueError):
        record_consistency(path, seed=6, n=1, trace_ids=["c02-00000002"])


def test_file_is_sorted_json_with_trailing_newline(tmp_path):
    path = tmp_path / "s.json"
    record_blind(path, seed=1, n=3, trace_ids=BLIND_IDS)
    texto = path.read_text(encoding="utf-8")
    assert texto.endswith("\n")
    dados = json.loads(texto)
    assert texto == json.dumps(dados, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def test_load_samples_of_missing_file_is_empty(tmp_path):
    assert load_samples(tmp_path / "nao_existe.json") == {}


# --- carga dos traces -------------------------------------------------------

def test_load_traces_ignores_other_json_and_reads_subfolders(tmp_path):
    (tmp_path / "sub").mkdir()
    (tmp_path / "c01-aaaa0001.json").write_text(
        json.dumps(make_trace("c01", "aaaa0001", "ok")), encoding="utf-8")
    (tmp_path / "sub" / "c02-bbbb0002.json").write_text(
        json.dumps(make_trace("c02", "bbbb0002", "erro")), encoding="utf-8")
    (tmp_path / "_split_meta.json").write_text('{"seed": 1}', encoding="utf-8")
    (tmp_path / "notes.json").write_text('{"x": 1}', encoding="utf-8")
    ids = sorted(t["trace_id"] for t in load_traces(tmp_path))
    assert ids == ["c01-aaaa0001", "c02-bbbb0002"]


# --- CLI --------------------------------------------------------------------

def test_main_blind_extend_consistency_happy_path(tmp_path, capsys):
    cases, traces = make_world()
    cdir, tdir = write_corpus(tmp_path, cases, traces)
    out = tmp_path / "annotations" / "_samples.json"
    args = ["--traces-dir", str(tdir), "--cases-dir", str(cdir), "--out", str(out)]

    assert main(["blind", "--seed", "1", "--n", "8", *args]) == 0
    impressos = capsys.readouterr().out.splitlines()
    assert impressos == load_samples(out)["blind"]["trace_ids"]
    assert len(impressos) == 8

    assert main(["extend", "--seed", "2", "--n-more", "4", *args]) == 0
    novos = capsys.readouterr().out.splitlines()
    assert len(novos) == 4
    assert load_samples(out)["extensions"][0]["trace_ids_added"] == sorted(novos)

    assert main(["consistency", "--seed", "3", "--n", "5", *args]) == 0
    cons = capsys.readouterr().out.splitlines()
    assert load_samples(out)["consistency"]["trace_ids"] == sorted(cons)
    assert len(cons) == 5


def test_main_error_goes_to_stderr_and_returns_1(tmp_path, capsys):
    cases, traces = make_world()
    cdir, tdir = write_corpus(tmp_path, cases, traces)
    out = tmp_path / "_samples.json"
    args = ["--traces-dir", str(tdir), "--cases-dir", str(cdir), "--out", str(out)]
    assert main(["blind", "--seed", "1", "--n", "8", *args]) == 0
    capsys.readouterr()
    assert main(["blind", "--seed", "1", "--n", "8", *args]) == 1
    assert capsys.readouterr().err.strip() != ""


def test_main_without_seed_exits(tmp_path):
    with pytest.raises(SystemExit):
        main(["blind"])
