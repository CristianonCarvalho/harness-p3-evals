# Passo 10: o relatório

## O que mudou

A spec ganhou a decisão D12: o relatório é um JSON versionado (fonte de verdade, lido pelo CI) mais um Markdown gerado a partir dele. Traz cabeçalho de reprodução, taxa de aprovação por critério e condição com n e intervalo, quem decidiu cada número, o TPR/TNR do juiz, o custo, e a marca "dentro do ruído" na comparação antes/depois. Nenhum código foi escrito.

## Como rodar

Não há o que rodar. Esboce à mão, em papel, a tabela do relatório para um modelo e dois critérios, com números inventados, e inclua o n e o intervalo.

## O que observar

- Com 70 casos de teste e uma taxa de 80%, qual é a ordem de grandeza do intervalo? Com ela, uma diferença de 4 pontos entre dois modelos é real ou é ruído?
- O que mais você precisaria no cabeçalho para reproduzir a rodada daqui a seis meses?

## Pergunta de previsão

Entre Sonnet 5.5 e Haiku 5.5, em quantos dos quatro critérios você espera uma **diferença real** (maior que o ruído)? Escreva o número antes da primeira rodada.
