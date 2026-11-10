# O P3 no roadmap

- **Fonte:** roadmap de estudo em Engenharia de Software com Agentes de IA (Fase 3: Evals).
- **O que isto é:** um resumo do que o roadmap diz sobre o P3 e o que depende dele. As frases entre aspas são do próprio roadmap.

## A tese

O P3 é a parte de avaliação (evals) do roadmap: medir qualidade em vez de opinar.

Duas premissas do diagnóstico que pesam no P3:
1. **"Nota 5 em uso diário não é domínio."** No estudo da METR (jul/2025), desenvolvedores experientes ficaram 19% mais lentos com IA e acreditavam estar 20% mais rápidos. A autoavaliação precisa de medição, e o eval é essa medição.
2. O gargalo não é prompt: o DORA 2025 mostra que a IA amplifica a maturidade de engenharia que já existe.

## Fase 3: Evals

| Item | O que o roadmap diz |
|---|---|
| Objetivo | Medir qualidade em vez de opinar |
| Critério de concluído da fase | 100 traces anotados; juiz LLM calibrado; toda mudança vem com antes/depois |
| Tópicos | análise de erros (codificação aberta e axial), juiz LLM medido por TPR/TNR, conjuntos de regressão, testes de propriedade, benchmarks como SWE-bench e seus limites |
| Recursos | Husain e Shankar, ["Building eval systems that improve your AI product"](https://www.lennysnewsletter.com/p/building-eval-systems-that-improve) e o blog hamel.dev; curso pago deles no Maven (opcional). Nas fontes do roadmap, também o [FAQ sobre evals](https://feeds.simonwillison.net/2025/Jul/3/faqs-about-ai-evals) (via Simon Willison) |
| Projeto | P3 |
| Concluído | "trocar de modelo ou prompt gera um relatório numérico, não uma impressão" |

## O P3 na tabela de projetos de portfólio

| # | Projeto | Fase | Dados | O que prova |
|---|---|---|---|---|
| P3 | Suíte de evals para o P2: 100 perguntas reais anotadas, taxonomia de erros, juiz LLM calibrado, regressão em CI | 3 | Perguntas criadas por pessoas | Qualidade medida |

**Atenção ao campo "Dados":** o roadmap diz que as perguntas são **criadas por pessoas**. As perguntas candidatas em [`../p2/casos-candidatos.md`](../p2/casos-candidatos.md) foram escritas durante a construção do P2 e servem de ponto de partida, mas as 100 perguntas anotadas devem vir de pessoas reais, e a anotação (o que é uma boa resposta) é de quem entende do assunto.

**Regra para todos os projetos:** "repositório público (exceto P5), README com decisões e limites, e um texto curto explicando o que deu errado."

## Como o roadmap mede o P3

| Métrica | Como medir | Meta em 6 meses | Meta em 12 meses |
|---|---|---|---|
| Evals | Casos anotados e regressões detectadas | 100 casos | Regressão roda em CI a cada mudança |
| Previsão de falhas | Antes de rodar o agente, anotar o que vai dar errado; comparar | Acerta metade | Acerta a maioria e sabe por quê |
| Projetos com critério atendido | Checklist da fase | P1, P2 e P3 iniciado | P1 a P5 |
| Segurança | Ataques testados e mitigados | — | 10 documentados |

Sinais de que o estudo está funcionando, os que tocam o P3: "Explica por que um agente falhou sem rodar de novo, e o conserto funciona." e "Diz 'não use agente aqui' com argumento técnico, e acerta."

## Regras do roadmap que valem no P3

- **Fundamentos sem delegação.** *"Nas fases 1 e 3, escreva o núcleo à mão e use o agente só para revisar. O estudo da Anthropic sobre formação de habilidade mostra que delegar tudo reduz domínio."*
- **Modo aprendizado.** Para conteúdo novo, prefira explicações e perguntas a respostas prontas.
- **Corte o escopo, não o critério de concluído.**

## O que estudar a fundo, e o que não

| Categoria | Exemplos | Como tratar |
|---|---|---|
| Durável (fato) | Como LLMs falham; contexto como recurso finito; **evals**; prompt injection como problema estrutural; testes, arquitetura, CI/CD | Estudar a fundo |
| Muda rápido (tendência) | Recursos de Claude Code e Kiro; versões da spec MCP; formatos de skills e hooks; ranking de modelos | Aprender o conceito, consultar a doc oficial na hora de usar |
| Pode ficar obsoleto (opinião) | Truques de prompt; frameworks de orquestração pesados; técnicas de RAG muito específicas | Não se especializar |

Consequência para o P3: o **método** (análise de erros, juiz calibrado, regressão) é o que dura. Os modelos, os preços e os nomes das ferramentas mudam, então os relatórios do P3 devem registrar a versão de tudo que mediram.

## Depois do P3: o P4

Fase 4, "Segurança e CI/CD" (semanas 29–38, 70 h), com o P4: pipeline "agente abre PR, gates decidem" em um repositório Java ou Python, **mais red team de prompt injection no P2**.

- Tópicos: OWASP LLM Top 10 (2026) e Agentic Top 10; lethal trifecta; sandbox e permissões mínimas; segredos; supply chain; GitHub Actions ou equivalente; agente em CI com gates; tracing com OpenTelemetry; orçamento de tokens.
- Concluído: *"um PR aberto por agente só chega à branch principal com testes, SAST, evals e revisão humana verdes."*
- **O P3 entrega o "evals" desse gate**, e o red team do P4 reaproveita os casos de segurança do P3.
