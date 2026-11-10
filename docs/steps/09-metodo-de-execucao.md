# Passo 09: método de execução

## O que mudou

A spec ganhou a decisão D11: o entorno é implementado na conversa, em passos pequenos e com TDD, sem Meister; a implementação é delegada ao Haiku 5.5 sempre que possível, com revisão na sessão principal. O núcleo continua sendo escrito pelo usuário. Nenhum código foi escrito.

## Como rodar

Não há o que rodar. Releia D11 e liste quais partes do entorno você acha que são mecânicas o bastante para o Haiku (por exemplo, um adaptador com entrada e saída bem definidas) e quais exigem decisão (por exemplo, o ledger com teto de custo).

## O que observar

- Uma tarefa delegada precisa de enunciado autossuficiente. Dá para escrever o de uma tarefa pequena em 10 linhas? Se não, a tarefa está grande demais.
- Como saber que o Haiku fez o que foi pedido? A resposta deve ser: testes passando e diff lido, nunca só o relato dele.

## Pergunta de previsão

Qual parte do entorno você espera que o Haiku erre primeiro, e por quê? Escreva antes do primeiro passo de implementação e compare depois.
