# Passo 01: decisões do núcleo (rascunho da spec)

## O que mudou

Nasceu o rascunho da spec em `docs/superpowers/specs/2026-11-10-p3-evals-design.md` com três decisões: o que é núcleo (formato de anotação, TPR/TNR e juiz), o formato da anotação (binário por critério, com C1 a C4) e a divisão entre código e juiz. Nenhum código foi escrito.

## Como rodar

Não há o que rodar. Leia o rascunho da spec e confira se cada decisão é o que você quis dizer.

## O que observar

- Os critérios C1 a C4 são o que você marcará como aprovado/reprovado em cada resposta. Algum falta ou sobra?
- Onde o código decide (C1, parte de C2 e C4), o juiz não precisa de calibração. Isso reduz o trabalho do juiz, mas aumenta o do extrator de citações e datas.

## Pergunta de previsão

Antes de anotar qualquer caso: em 10 respostas do modelo usando o server, quantas você acha que reprovam em C1 (citação sem lastro), e quantas em C3 (postura errada quando não há resposta)? Escreva os dois números antes da primeira rodada.
