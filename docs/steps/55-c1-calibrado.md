# Passo 55: o C1 calibrado

Você anotou às cegas os 19 traces da extensão (passo 54). A amostra cega tem agora **49 traces**, e o relatório da rodada `haiku-skill-id-20261114` foi regenerado com eles ([reports/2026-11-15-haiku-skill-id-20261114.md](../../reports/2026-11-15-haiku-skill-id-20261114.md)).

## O que mudou

- **19 anotações** `kind: blind`, versão 1.
- **O relatório de 2026-11-15** foi regerado no mesmo nome, com a amostra de 49 (a versão anterior fica no histórico do git, no passo 52).

## O que observar

**Seus vereditos nos 49 cegos:** C1 com 31 `pass` e **18 `fail`**; C2 com 48 e 1; C3 com 40 e **9**; C4 com 5 `pass` e 44 `n/a`.

**O juiz contra você:**

| Critério | TPR | TNR | Aprovados / reprovados com veredito do juiz | Situação |
|---|---|---|---|---|
| C1 | 0,76 | 1,00 | 25 / 11 | **calibrado**, e acima do limiar (TPR 0,7, TNR 0,8) |
| C2 | 0,91 | 1,00 | 11 / 1 | não calibrado |
| C3 | 0,90 | 0,89 | 40 / 9 | não calibrado: **falta 1 reprovado** |
| C4 | — | — | 0 / 0 | não medido |

- **O C1 é o primeiro critério calibrado.** O `check-repo` agora cobra o limiar dele de verdade, e passa.
- **O C3 ficou a 1 reprovado da meta.** A previsão era de uns 4 novos reprovados; vieram 3. Com a fonte B ainda tendo 19 casos de teste livres, uma extensão de uns 5 traces deve fechar.
- **O C2 continua como limite declarado:** 1 reprovado em 49.

**Critério de concluído 3 (juiz calibrado contra a anotação humana):** atendido no C1; no C3, por um trace; no C2 e no C4, não atingível com estes dados, o que vai para os limites conhecidos.

## Extensão para o C3 (semente 20261116)

Mais 5 traces da rodada `haiku-skill-id-20261114`, sorteados entre os 19 casos de teste ainda livres, só com skill: `c008-406ca69f`, `c013-91ced274`, `c033-8489277a`, `c072-86e05ebf`, `c074-67da112f`. Dossiês em `traces/dossies/cega-ext2/`, fora do git, sem leitura pelo Claude. Os 5 já tinham julgamento: custo zero.

## Resultado: o C3 calibrado

Com os 5 anotados (54 cegos), o relatório foi regerado no mesmo nome:

| Critério | TPR | TNR | Aprovados / reprovados | Situação |
|---|---|---|---|---|
| C1 | 0,76 | 1,00 | 25 / 11 | calibrado, acima do limiar |
| C3 | **0,91** | **0,91** | 43 / **11** | **calibrado**, acima do limiar |
| C2 | 0,92 | 1,00 | 13 / 1 | não calibrado (limite) |
| C4 | — | — | 0 / 0 | não medido (limite) |

O `check-repo` cobra o limiar do C1 e do C3, e os dois passam. **Critério de concluído 3 atendido** nos critérios em que o juiz decide com frequência; o C2 e o C4 ficam como limites declarados.

## Pergunta de previsão

Em 5 traces novos da fonte B, quantos você vai reprovar no C3?
