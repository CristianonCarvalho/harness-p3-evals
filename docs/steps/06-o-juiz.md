# Passo 06: o juiz

## O que mudou

A spec ganhou a decisão D8: o juiz é um modelo de outra família (não Claude), chamado via OpenRouter com o cliente do P1, com versão fixada, uma chamada por critério e sem ver o veredito humano. Nenhum código foi escrito.

## Como rodar

Não há o que rodar. Escolha à mão um critério (por exemplo, C3) e escreva em 5 linhas o que o juiz receberia e o que devolveria. É o esboço do prompt do juiz, que fará parte do seu núcleo.

## O que observar

- O que o juiz precisa ver para decidir C3 sem adivinhar? Se faltar algo no trace, volte ao formato (D5).
- Que tipo de resposta limítrofe você acha que o juiz vai errar? Esses são os casos a incluir na calibração.

## Pergunta de previsão

Qual será o TPR e qual será o TNR do juiz no primeiro teste? Escreva os dois números antes da primeira medição. Tendência comum: o TPR sai alto e o TNR baixo, porque o juiz é generoso.
