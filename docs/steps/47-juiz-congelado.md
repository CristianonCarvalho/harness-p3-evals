# Passo 47: o juiz congelado

Marco M8. Depois do passo 46, você mudou o juiz em duas rodadas: primeiro uma faixa de artigos deixou de reprovar o C1 e o C3 passou a receber se o corpus responde; depois, o nome de uma norma sem dispositivo deixou de contar como citação. O juiz `openai/gpt-6.1-terra` rodou de novo nos 30 traces cegos a cada mudança, e o prompt foi **congelado** na terceira versão.

## O que mudou

- **[config/run.json](../../config/run.json):** `models: ["claude-haiku-5-5"]`, `judge_model: "openai/gpt-6.1-terra"`, `judge_prompts_sha256: 8885a7f4…`.
- **`judgments/`:** os 30 julgamentos da versão congelada, que substituem os do passo 46.
- **Custo das duas rodadas novas:** US$ 0,35 e US$ 0,38. O juiz, somando as três versões, custou US$ 1,10. Os julgamentos intermediários ficam em `runs/judges/`, fora do git.

## O que observar

O "positivo" é `pass`: o TPR é a concordância nos traces que você aprovou, e o TNR, nos que você reprovou.

| Critério | Traces | v1 (passo 46) | v2 (faixas; C3 com o gabarito) | v3 (congelada) |
|---|---|---|---|---|
| C1 | 27 | TPR 0,06 · TNR 1,00 | TPR 0,67 · TNR 1,00 | **TPR 0,78 · TNR 1,00** |
| C2 | 7 | 1,00 · 1,00 | 1,00 · 1,00 | **1,00 · 1,00** (só 1 reprovado) |
| C3 | 30 | TPR 0,88 · TNR 0,00 | TPR 0,88 · TNR 0,83 | **TPR 0,88 · TNR 0,83** |

**Discordâncias que ficaram (8):**
- **C1, juiz mais rigoroso (4):**
  - `c003` e `c081`: conteúdo específico tirado de uma faixa (as reduções de 60% e 30% atribuídas aos arts. 126 a 142, que não vieram das ferramentas). É a ressalva da regra 5, aplicada como escrita.
  - `c070`: o juiz achou citação à CF, art. 153, IV e VIII, que só apareceu como remissão no texto devolvido.
  - `c096`: a regra "todos os esperados" ao pé da letra (os incisos do art. 127 não foram citados um a um). Era uma das suas dúvidas.
- **C3 (4):**
  - `c050`: o juiz reprovou a postura por falta de consulta às ferramentas, o que é assunto do C1 e do C2. É erro do juiz.
  - `c052` e `c055`: o juiz viu, num, uma afirmação categórica com o corpus sem resposta e, no outro, um "falso não sei"; você aprovou os dois.
  - `c082`: você reprovou, e o juiz aprovou.

**Limites desta medida:**
- **Otimista:** o prompt foi ajustado olhando a própria amostra cega, em duas rodadas. Os ajustes foram de princípio (faixas, nome de norma, o campo de gabarito do C3), não de caso, mas a medida num conjunto novo deve sair um pouco pior.
- **Pequena:** são 9 reprovados no C1, 6 no C3 e 1 no C2. O intervalo de confiança é largo; o C2 não tem reprovados suficientes para dizer algo sobre o TNR.
- **C4:** não medido. Não houve caso H13, e no H12 o código decide.

## Pergunta de previsão

Na reanotação de consistência (alguns dias depois), em quantos dos 10 traces você vai mudar algum veredito?
