# Passo 45: as 30 anotações cegas

Marco M7: você anotou os 30 traces da amostra cega (passo 44), só com o dossiê. Todas são `kind: blind`, versão 1.

## O que mudou

- **30 anotações** em `annotations/<trace_id>.v1.json`, gravadas pelo comando `annotate`. O `check-repo` não acusa problema (só os avisos esperados: `config/run.json` incompleto e ainda sem relatório).

## O que observar

| Critério | `pass` | `fail` | `n/a` | Em dúvida |
|---|---|---|---|---|
| C1 | 19 | **11** | 0 | 4 |
| C2 | 29 | **1** | 0 | 0 |
| C3 | 24 | **6** | 0 | 1 |
| C4 | 3 | **0** | 27 | 0 |

**A meta de ~10 reprovados por critério (R3) só foi atingida no C1.**
- **C3 (6 de 30):** com essa taxa, uns 20 traces a mais dariam os 10. O conjunto de teste tem 68 casos, e 30 já estão na amostra: há 38 de onde tirar.
- **C2 (1 de 30):** a taxa é baixa demais para estender a amostra até 10 reprovados; seriam centenas de traces. O TPR/TNR do juiz no C2 vai sair com uma classe pequena, e o relatório marca isso (`calibrated` falso onde a classe é pequena).
- **C4 (0 reprovados em 3):** o Haiku não repetiu nenhum CPF. Sem reprovado, não há como medir se o juiz pega uma falha; o C4 é quase todo decidido pelo código (o eco do número), e o juiz só entra no H13, que não está no conjunto.

**A regra "todos os esperados" pesou no C1:** 11 reprovados, e 4 dúvidas.

## Pergunta de previsão

Nos 11 traces que você reprovou no C1, quantos o juiz vai aprovar?
