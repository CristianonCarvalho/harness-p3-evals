# Projeto 3 (P3): suíte de avaliação do MCP server de legislação tributária

## Roadmap

Este projeto é o **P3** de um roadmap de estudo em Engenharia de Software com Agentes de IA.

[`docs/roadmap/p3-no-roadmap.md`](docs/roadmap/p3-no-roadmap.md) resume o que importa ao P3. Antes de decidir escopo ou critério, leia esse resumo.

- **Fase 3: Evals.** Objetivo: medir qualidade em vez de opinar.
- **Tópicos:** análise de erros (codificação aberta e axial), juiz LLM medido por TPR/TNR, conjuntos de regressão, testes de propriedade, benchmarks como SWE-bench e seus limites.
- **Recursos:** Husain e Shankar, "Building eval systems that improve your AI product", e o blog hamel.dev; curso pago deles no Maven (opcional).
- **Projeto:** **suíte de evals para o P2**: 100 perguntas reais anotadas, taxonomia de erros, juiz LLM calibrado, regressão em CI.
- **Dados:** perguntas criadas por pessoas.
- **O que prova:** qualidade medida.

### Critério de concluído

1. **Trocar de modelo ou prompt gera um relatório numérico, não uma impressão** (critério da Fase 3).
2. **100 traces anotados** (critério da Fase 3; "100 casos" na métrica de evals do roadmap).
3. **Juiz LLM calibrado** contra a anotação humana (TPR e TNR medidos).
4. **Toda mudança vem com antes/depois.**
5. **A regressão roda em CI a cada mudança** (meta de 12 meses do roadmap).

Escopo pode ser cortado; o critério de concluído, não.

## Regras do roadmap que valem aqui

- **Só dados públicos ou sintéticos. Nunca dados de contribuinte**, nem em perguntas, gabaritos, fixtures, traces ou relatórios. Casos com CPF/CNPJ usam números **sintéticos gerados em tempo de execução**, nunca escritos no repositório.
- **Repositório público**, com README de decisões e limites e um texto curto explicando o que deu errado.
- **Fundamentos sem delegação.** O roadmap diz: *"Nas fases 1 e 3, escreva o núcleo à mão e use o agente só para revisar."* No P3, isso muda o método usado no P2: **o núcleo é escrito pelo usuário, e o Claude revisa, explica, pergunta e prepara o entorno**, mas não o implementa. O que conta como núcleo (a sugestão é: o formato de anotação, as métricas TPR/TNR e o juiz) será definido na spec, antes de qualquer código.
- **Modo aprendizado:** para conteúdo novo, prefira explicações e perguntas a respostas prontas.

## O que o P3 avalia, e por que depende do P2 e do P4

- **O sistema avaliado é o P2:** um MCP server de legislação (EC 132/2023 e capítulos da LC 214/2025) com duas ferramentas, uma skill e um hook. A resposta que importa é a do **modelo usando o server**, com e sem a skill.
- **O P2 foi desenhado para ser avaliado** (CLAUDE.md do P2): toda resposta traz o dispositivo e a data de efeitos em formato estruturado e verificável; as ferramentas são determinísticas e testáveis offline; "não encontrei" é uma resposta válida; o texto da norma é dado, não instrução.
- **O P4** usa o P3: o pipeline "agente abre PR, gates decidem" exige "testes, SAST, evals e revisão humana verdes", e o red team de prompt injection mira o P2. Os casos de segurança do P3 (CPF/CNPJ e texto de norma com instrução) são a ponte.

Detalhes do P2 em [`docs/p2/`](docs/p2/): o contrato das ferramentas, o estado e as versões a fixar, os limites do P2 convertidos em hipóteses a medir e as perguntas candidatas.

## Herança

- **P1** (`../projeto01`, repo `CristianonCarvalho/harness-p1-agente-minimo`): o cliente HTTP (`agent/client.py`, OpenRouter) e o ledger de tokens e custo (`agent/ledger.py`), mais o formato de tarefa com `check.py` e `prediction.md`. Ver [`docs/p1/heranca-do-p1.md`](docs/p1/heranca-do-p1.md).
- **P2** (`../projeto02`, repo `CristianonCarvalho/harness-p2-MCP`): o server, o cliente de terminal e as lições de engenharia (abaixo).

## Forma de trabalho (a que deu certo no P1 e no P2)

- Passos pequenos; cada um é um commit com tag `step-NN` e uma nota em `docs/steps/NN-nome.md` com as seções `## O que mudou`, `## Como rodar`, `## O que observar`, `## Pergunta de previsão`.
- Spec em `docs/superpowers/specs/`, planos em `docs/superpowers/plans/`.
- Previsão antes de rodar, comparada com o resultado depois.
- Mensagens ao usuário e notas em português; identificadores de código em inglês.
- **Testes offline:** nenhum teste do `pytest` chama modelo nem rede, e a suíte passa igual de qualquer diretório; nada de `conftest.py` nem truque que faça um teste passar sem corrigir o problema. As **rodadas de avaliação**, que chamam modelos e custam dinheiro, são comandos separados, com ledger e teto de custo.

Lições do P2 (ver `../projeto02/docs/o-que-deu-errado.md`), que valem no P3:

- Regra que importa fica no código, não só no prompt. O harness decide o que acontece quando o modelo erra.
- Um eval vale o que a anotação vale: confira o juiz contra anotação humana antes de confiar nele.
- Protótipo no dado real antes de planejar; teste de mutação para ver se os testes têm dentes.
- Teste que pode pendurar tem tempo máximo, e teste intermitente é defeito: rode a suíte mais de uma vez.
- Mensagem de erro é interface. Limites por resposta (tokens, número de chamadas) e registro no trace desde o início, não depois da primeira conta alta.

## Segredos

- `.env` no `.gitignore` desde o primeiro commit; nunca commitar `.env`, traces ou execuções locais.
- Nunca exibir chaves (`OPENROUTER_API_KEY`, `ANTHROPIC_API_KEY`, `TAXLAW_HTTP_TOKEN` ou outras) em saída, log, nota ou commit. O token do server remoto do P2 só entra por variável de ambiente.

## Execução

Este projeto ainda não tem `.meister/` nem `meister.config.yaml`. Configure o MeisterRouter antes de implementar, ou pergunte ao usuário qual método usar; e lembre que o núcleo do P3 é escrito à mão (regra acima). Documentação (`docs/**`, `*.md`) pode ser editada direto.
