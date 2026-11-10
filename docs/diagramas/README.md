# Diagramas

Diagramas em [Mermaid](https://mermaid.js.org/): o GitHub os desenha direto no navegador, e o texto continua legível e versionável no `git diff`. Cada arquivo tem um diagrama e uma explicação curta.

| # | Diagrama | Responde a |
|---|---|---|
| 01 | [Visão geral](01-visao-geral.md) | Como uma pergunta vira um número no relatório? |
| 02 | [Uma execução](02-uma-execucao.md) | O que acontece, passo a passo, ao rodar um caso? |
| 03 | [Dados e arquivos](03-dados-e-arquivos.md) | O que vai ao git, o que não vai e por quê? |
| 04 | [O juiz e a calibração](04-o-juiz-e-a-calibracao.md) | Como saber quanto confiar no juiz? O que são TPR e TNR? |
| 05 | [Código ou juiz](05-checagens-codigo-ou-juiz.md) | Quem decide cada um dos quatro critérios? |
| 06 | [Condições das rodadas](06-condicoes-das-rodadas.md) | Com e sem skill, local e remoto: o que cada uma mede? |
| 07 | [CI e rodadas pagas](07-ci-e-rodadas-pagas.md) | O que roda a cada mudança e o que roda sob demanda? |
| 08 | [Módulos](08-modulos.md) | Quem depende de quem no código, e quem escreve o quê? |
| 09 | [Ordem das tarefas](09-ordem-das-tarefas.md) | O que já foi feito e o que bloqueia o resto? |
| 10 | [A anotação](10-anotacao.md) | Quando um critério é `n/a`? O que o validador recusa? |

Os conceitos que aparecem nos diagramas (trace, juiz, TPR, TNR, calibração, ruído…) estão explicados, com exemplos, em [Conceitos explicados](../../README.md#conceitos-explicados) no README.

## Como manter

Os diagramas **08** e **09** mostram o andamento (verde é feito). Quando uma tarefa do plano for concluída, troque a classe do nó correspondente de `falta` ou `seu` para `feito` e atualize a contagem no README.
