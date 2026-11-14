# Passo 41: o juiz pode julgar o C1 (entorno)

A piloto (passo 40) mostrou que 17 de 20 respostas citam só em prosa, e o C1 ficaria pendente. Decisão de 2026-11-14: **o juiz julga o C1 quando o código devolve `needs_judge`** (registrada no [diagrama 05](../diagramas/05-checagens-codigo-ou-juiz.md)). Este passo é só o entorno; o juiz (núcleo) ainda não gera C1.

## O que mudou

- **[evals/review_report.py](../../evals/review_report.py):** `JUDGE_CRITERIA` passou a ter `C1`. O relatório da revisão mede o TPR/TNR do juiz no C1 e conta à parte os traces sem veredito do juiz no C1.
- **[evals/consistency.py](../../evals/consistency.py):** o `check-repo` aceita `C1` num julgamento (a lista vem de `review_report`); a mensagem de critério fora do juiz diz "use C1, C2, C3 ou C4". A recontagem do relatório também confere o C1.
- **Testes:** 7 novos, 2 casos novos num `parametrize`; o caso que esperava a recusa do `C1` virou aceitação.
- Programado pelo Haiku, revisado pelo Claude.

## O que falta (núcleo, seu)

- `evals/judge.py`: `JUDGE_CRITERIA` com `C1`; `criteria_for_trace` acrescenta `C1` quando `check_c1` dá `needs_judge`; `build_messages` passa os `expected_provisions` do gabarito só no C1.
- `config/judge_prompts/C1.md`, com a decisão: o esperado conta se **todos** forem citados, ou **pelo menos um**.
- Enquanto isso, um julgamento real não traz C1, e o relatório da revisão mostra o C1 como "sem juiz".

## Como rodar

```bash
uv run pytest -q
```

```bash
uv run python -m evals.cli check-repo
```

## O que observar

- **Suíte:** 601 testes, verde duas vezes.
- **Teste de mutação:** 3 mutações, as 3 caem (tirar o `C1` da lista: 8 falhas; voltar a mensagem antiga: 1; aceitar qualquer valor no `C1`: 2).

## Pergunta de previsão

Dos 17 traces da piloto com C1 em prosa, quantos o juiz vai reprovar?
