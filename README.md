# P3: suíte de avaliação do MCP server de legislação tributária

**Status: em preparação.** Ainda não há código. Este repositório será a suíte de evals do [P2](https://github.com/CristianonCarvalho/harness-p2-MCP) (um MCP server que responde sobre a reforma tributária com o dispositivo citado e a data de efeitos).

É o projeto **P3** do roadmap "Engenharia de Software com Agentes de IA" (Fase 3: Evals). A ideia central: **trocar de modelo ou de prompt gera um relatório numérico, não uma impressão.**

## Critério de concluído

1. Trocar de modelo ou prompt gera um relatório numérico.
2. 100 traces anotados.
3. Juiz LLM calibrado contra a anotação humana (TPR e TNR).
4. Toda mudança vem com antes/depois.
5. A regressão roda em CI a cada mudança.

## Onde está o quê

- [`CLAUDE.md`](CLAUDE.md): regras e contexto do projeto.
- [`docs/README.md`](docs/README.md): índice da documentação (roadmap, P2, P1 e decisões em aberto).

## Decisões e limites

Ainda não há. Este README ganha as seções "Decisões" e "Limites conhecidos" junto com a spec, e o texto "o que deu errado" quando houver o que contar.

## Dados

Só normas públicas e números **sintéticos**, gerados em tempo de execução. Nenhum dado de contribuinte, nem em perguntas, gabaritos, fixtures ou traces.
