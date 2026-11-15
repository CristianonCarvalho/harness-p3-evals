# Passo 52: 100 traces anotados

Marco M7b. Você revisou os 70 rascunhos do passo 51. Com os 30 cegos, são **100 traces anotados com o tipo declarado**: o critério de concluído 2 está atendido.

## O que mudou

- **70 anotações** `kind: revised` em `annotations/<trace_id>.v1.json`, cada uma apontando para o seu rascunho.
- **Relatório novo** [reports/2026-11-15-haiku-skill-id-20261114.md](../../reports/2026-11-15-haiku-skill-id-20261114.md), da rodada mais recente (P2 `step-17`), com a seção "Revisão da anotação" mostrando 30 cegas, 70 revisadas e o critério 2 atendido. O `check-repo` não acusa problema nem aviso.

## O que observar

**Quanto você mudou o rascunho** (em 20 dos 70 traces mudou algum veredito):

| Critério | Mudanças | Taxa de mudança | Rascunho reprovou | Você reprovou |
|---|---|---|---|---|
| C1 | 9 | 12,9% | 52 | 43 |
| C2 | 13 | 18,6% | 14 | 1 |
| C3 | 0 | 0% | 15 | 15 |
| C4 | 0 | 0% (de 4) | 0 | 0 |

- **C2:** o rascunho reprovou 14 e você manteve 1. Toda mudança foi de `fail` para `pass`: o rascunhador é rigoroso demais com datas, como já se via na comparação com os cegos.
- **C1:** 9 mudanças. Mesmo com a régua "todos os esperados", você reprovou 43 de 70 (61%), bem acima dos 37% dos cegos. Os 70 vieram da rodada base, como os cegos, então a diferença é de amostra ou de ancoragem.
- **C3:** nenhuma mudança em 70. Ou o rascunhador acerta o C3 sempre, ou você seguiu o rascunho. Não dá para separar as duas coisas sem a taxa de erro do rascunhador.

**O aviso de ancoragem não pôde ser calculado.** A regra (R5) compara a sua taxa de mudança com a **taxa de erro do rascunhador**, e essa taxa só é medida nos traces cegos, onde existe a sua anotação independente. Nenhum dos 30 cegos tem rascunho. Rascunhar os 30 agora (rascunho tardio, permitido porque a anotação deles já fechou) custa uns US$ 0,08 e fecha a medida.

**Juiz:** continua não calibrado. As 70 revisadas não entram na medida do juiz, por desenho.

## Pergunta de previsão

Nos 30 traces cegos, quantos vereditos do C3 o rascunhador vai errar?
