# Passo 04: divisão dos 100 casos

## O que mudou

A spec ganhou a decisão D6: 30 casos de desenvolvimento e 70 de teste, divididos por caso, estratificados pelas hipóteses H1 a H14 e sorteados antes de anotar. O teste é congelado: só nele se mede TPR/TNR. Nenhum código foi escrito.

## Como rodar

Não há o que rodar. Para fixar o conceito de TPR/TNR, pegue 10 casos imaginários (por exemplo, 8 aprovados e 2 reprovados por você) e calcule à mão o TPR e o TNR de um juiz que aprova tudo.

## O que observar

- Um juiz que sempre aprova tem TPR 1,0 e TNR 0. Por que a taxa de acerto geral esconde isso?
- Com 2 reprovados, um erro do juiz muda o TNR em 50 pontos. Quantos reprovados o teste precisa ter para o TNR ser confiável?

## Pergunta de previsão

Entre as hipóteses H1 a H14, quais você espera que gerem mais respostas **reprovadas** no teste? Escreva as três antes da primeira rodada; elas dizem onde o P2 é mais fraco e onde pode faltar reprovado para medir o TNR.
