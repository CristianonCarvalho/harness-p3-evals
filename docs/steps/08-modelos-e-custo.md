# Passo 08: modelos avaliados e teto de custo

## O que mudou

A spec ganhou a decisão D10: dois modelos Claude (Sonnet 5.5 como base e Haiku 5.5 como troca), e o teto de custo definido depois de uma rodada piloto de 10 casos, sem valor chutado. A piloto também mede a variação entre execuções repetidas. Nenhum código foi escrito.

## Como rodar

Não há o que rodar. Confira em `claude --help` se há uma opção de modelo (`--model`) e de limite de custo ou de turnos para o modo não interativo. Anote o que encontrou; é o que o entorno da rodada vai usar.

## O que observar

- Dá para fixar o ID exato do modelo no modo não interativo? Sem isso o relatório não reproduz.
- Existe um limite nativo de custo ou de número de turnos? Se não, o ledger do P3 precisa impor o teto sozinho.

## Pergunta de previsão

Qual será a diferença entre Sonnet e Haiku na taxa de reprovação em C1 (citação com lastro)? Escreva o sentido e um tamanho aproximado antes da primeira rodada.
