# Passo 05: regressão em CI

## O que mudou

A spec ganhou a decisão D7: o CI roda só offline e protege o avaliador (núcleo, conta de TPR/TNR a partir de arquivos versionados, exigência de relatório antes/depois). A rodada paga com modelo e juiz fica sob demanda. Nenhum código foi escrito.

## Como rodar

Não há o que rodar. Releia a lista do que o CI faz em D7 e marque o que ele **não** consegue detectar.

## O que observar

- O CI não vê traces reais (ficam fora do git). Que tipo de erro isso deixa passar?
- Um PR pode trazer um relatório que não vem de uma rodada real. O que, além da revisão, poderia reduzir esse risco (por exemplo, registrar no relatório o `trace_id` dos traces usados)?

## Pergunta de previsão

Na primeira vez em que a regressão pegar uma queda de métrica, ela virá de uma mudança no prompt, no modelo ou na tag do P2? Escreva o palpite agora.
