# Passo 44: a amostra cega sorteada e os dossiês

Marco M7, primeira parte: o sorteio dos traces que você anota às cegas.

## O que mudou

- **Sorteio:** `python -m evals.sampling blind --seed 20261114 --n 30 --traces-dir traces/rounds/haiku-20261114-b`. Foram 30 traces, todos do conjunto de **teste**, um por caso (28 com skill e 2 sem skill), estratificados pela hipótese principal: H1 3, H2 3, H3 2, H4 3, H5 2, H6 2, H7 2, H8 3, H9 1, H10 1, H11 3, H12 3, H14 2. Registro em [`annotations/_samples.json`](../../annotations/_samples.json).
- **Dossiês:** os 30 foram gerados em `traces/dossies/cega/<trace_id>.md`, fora do git, cada um com o formulário ```` ```anotacao ````. **O Claude não leu nenhum** (R8).
- **Defeito no dossiê ([evals/dossier.py](../../evals/dossier.py)):** 3 dos 30 quebravam com `IndexError`. O P2 devolve às vezes um fundamento só com o nome da lei (`"LC 214/2025"`, sem artigo), e `_corpo_da_chave` supunha sempre uma vírgula depois da norma. Agora uma chave só com a norma não tem corpo e não casa com nenhuma citação. Um teste novo falhou antes da correção; suíte: 635, verde duas vezes. Para achar a causa, o Claude olhou só as chaves de fundamento desses 3 traces, não as respostas.

## Como rodar

Para cada dossiê, preencha o bloco ```` ```anotacao ```` e grave:

```bash
uv run python -m evals.cli annotate traces/dossies/cega/c001-bf331068.md --date 2026-11-14 --traces-dir traces/rounds/haiku-20261114-b
```

## O que observar

- **Reprovados por critério:** a calibração precisa de uns 10 reprovados em cada critério. Se faltarem, a amostra cresce com `sampling extend` (R3).
- **O H9 e o H10 têm 1 trace cada:** o peso deles na medida é pequeno.

## Pergunta de previsão

Dos 30 traces, em quantos você vai reprovar o C1?
