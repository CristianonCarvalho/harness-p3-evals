# Passo 54: a amostra cega estendida

Para o juiz ficar **calibrado** (10 aprovados e 10 reprovados por critério na sua anotação cega), faltavam 1 reprovado no C1 e 4 no C3. A amostra cega cresceu com **19 traces** que você nunca viu, nem com rascunho.

## O que mudou

Duas extensões em [`annotations/_samples.json`](../../annotations/_samples.json), ambas com a semente 20261115:

1. **9 da reserva da rodada base** (`haiku-20261114-b`, P2 `step-16`): todos os traces de teste da reserva do passo 51 cujo caso ainda não estava na amostra. Neles o modelo cita em prosa, então o juiz julga o C1, e é o C1 que precisa deles.
   - `c004`, `c007`, `c016`, `c029`, `c042`, `c062`, `c083`, `c084`, `c092`.
2. **10 da rodada com a skill pedindo o id** (`haiku-skill-id-20261114`, P2 `step-17`), só com skill, sorteados entre os 29 casos de teste ainda livres. Aqui o código decide quase todo o C1, então eles servem ao C3.
   - `c011`, `c014`, `c041`, `c046`, `c053`, `c056`, `c067`, `c076`, `c094`, `c097`.

**Como os 70 traces revisados ficaram de fora:** o comando `sampling extend` sorteia entre todos os traces de teste de uma pasta. Para ele só ver os candidatos permitidos, rodou sobre pastas temporárias, montadas com links só para a amostra atual e para os candidatos. Nenhum código mudou.

- **Dossiês:** os 19 estão em `traces/dossies/cega-ext/`, fora do git. **O Claude não leu nenhum** (R8).
- **Julgamentos:** os 19 já tinham julgamento do juiz congelado, das rodadas anteriores. Custo deste passo: **zero**.

## Como rodar

```bash
uv run python -m evals.cli annotate traces/dossies/cega-ext/c004-42bde01f.md --date 2026-11-15 --traces-dir traces/rounds
```

## O que observar

- Com 49 traces cegos, o C1 e o C3 devem passar a **calibrados** no próximo relatório, e o limiar (TPR 0,7, TNR 0,8) passa a ser cobrado pelo `check-repo`. Se o juiz ficar abaixo, o CI fica vermelho: é o eval funcionando.
- **Os 10 da fonte B são de outra versão do P2** (`step-17`). Para medir o juiz, isso não importa: a régua é a mesma e o juiz é o mesmo.

## Pergunta de previsão

Com os 49 cegos, o TNR do juiz no C3 vai ficar acima de 0,8?
