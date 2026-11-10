# Passo 03: formato do trace

## O que mudou

A spec ganhou a decisão D5: um JSON por execução, gerado por um adaptador por fonte, com cabeçalho (`source`, `model`, `conditions`), eventos com a saída bruta das ferramentas, resposta final e uso. A anotação fica em arquivo separado e o trace é imutável. Nenhum código foi escrito.

## Como rodar

Não há o que rodar. Leia o bloco de D5 na spec e tente preencher à mão, em um papel, um trace de uma pergunta qualquer.

## O que observar

- O que você sentiu falta ao preencher à mão? Esse campo provavelmente falta no formato.
- `conditions` cobre o que muda entre rodadas que você quer comparar?
- `annotations/` versionada e `traces/` ignorada: confere com o que você quer publicar no repositório?

## Pergunta de previsão

Dos campos de um trace, qual você acha que o adaptador do Claude Code terá mais dificuldade de preencher a partir do `stream-json`? Escreva o palpite antes de ver um stream real.
