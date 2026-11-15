# Passo 53: a medida de ancoragem

Completa o passo 52. O rascunhador rodou nos 30 traces cegos (rascunho tardio: a anotação deles já estava fechada), por **US$ 0,11**. Quatro respostas vieram vazias por limite de tokens e saíram numa segunda tentativa. Agora dá para medir a taxa de erro do rascunhador contra a sua anotação independente, e, com ela, a ancoragem (R5).

## O que mudou

- **30 rascunhos** em `drafts/annotations/`, marcados `blind: true`. O `check-repo` não acusa problema.
- Nenhum código mudou. O próximo relatório já mostra estas tabelas.

## O que observar

**O rascunhador contra você nos 30 cegos:**

| Critério | Concorda | Taxa de erro |
|---|---|---|
| C1 | 18 de 30 | **40%** |
| C2 | 22 de 30 | 27% |
| C3 | 30 de 30 | 0% |
| C4 | 3 de 3 | 0% |

**Ancoragem nos 70 revisados** (alerta quando a sua taxa de mudança é menor que metade da taxa de erro do rascunhador):

| Critério | Sua taxa de mudança | Erro do rascunhador | Alerta |
|---|---|---|---|
| C1 | 12,9% | 40,0% | **possível ancoragem** |
| C2 | 18,6% | 26,7% | — |
| C3 | 0% | 0% | — |
| C4 | 0% | 0% | — |

- **C3 sem mudança está explicado:** o rascunhador acertou os 30 cegos no C3. Não mudar nada era o esperado.
- **C1 tem possível ancoragem.** Nos cegos, o rascunhador erra 4 em 10 no C1, quase sempre reprovando a mais. Nos 70 revisados, você mudou 1 em 8. Se o erro dele nos revisados fosse o mesmo dos cegos, uns 28 vereditos estariam errados, e você corrigiu 9. Isso explica os 61% de reprovação no C1 dos revisados, contra 37% nos cegos.

**O que isso afeta e o que não afeta:**
- **Não afeta** o TPR/TNR do juiz, que usa só as anotações cegas.
- **Afeta** a confiança nos vereditos de C1 das 70 revisadas: elas contam para o critério 2 (100 anotados, com o tipo declarado), mas o C1 delas deve ser lido como "provavelmente rigoroso demais".
- **Correção possível:** reanotar às cegas o C1 de uma parte dos 70 (sem ver o rascunho) e medir quanto muda. É o mesmo mecanismo da reanotação de consistência.

## Pergunta de previsão

Reanotando às cegas o C1 de 10 dos 70 revisados, em quantos você vai mudar o veredito?
