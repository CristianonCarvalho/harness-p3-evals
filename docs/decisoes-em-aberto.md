# Decisões em aberto para a spec do P3

Nenhuma destas está decidida. A spec (`docs/superpowers/specs/`) nasce de uma sessão de brainstorming, uma decisão por vez, e cada resposta fica registrada lá. Aqui só está o mapa.

## Já decidido

- **Repositório novo e independente:** `harness-p3-evals`, sem fork do P2. O avaliador não deve depender do código do avaliado, e o P2 é acessado só pelo protocolo MCP, com a tag fixada.
- **Dados:** só públicos ou sintéticos; perguntas criadas por pessoas.

## Em aberto

| # | Decisão | Opções ou perguntas | Por que importa |
|---|---|---|---|
| 1 | **O que é o "núcleo" escrito à mão** | Sugestão: formato de anotação, métricas TPR/TNR e o juiz. Fica fora do núcleo: cliente HTTP, ledger, CI | O roadmap exige núcleo à mão na Fase 3, e o Claude só revisa |
| 2 | **Agente que produz os traces** | Reaproveitar o laço do P1, ou o SDK de agente do provedor, ou o Claude Code em modo não interativo | Define o que é um "trace" e o que se mede |
| 3 | **Com e sem skill** | Cada pergunta roda nas duas condições? | Mede o valor da skill (H11) |
| 4 | **Modelos** | Quais modelos são avaliados; qual é o juiz; o juiz é de uma família diferente do avaliado? | Juiz da mesma família tende a favorecer o próprio estilo |
| 5 | **Orçamento e conta do juiz** | Teto por rodada e por mês; conta e chave dedicadas, só por variável de ambiente | Nunca exibir chave; custo previsível |
| 6 | **Formato da anotação** | Aprovado/reprovado por critério, ou nota? Quais critérios (citação, data, "não sei" correto)? | Decide se TPR/TNR é calculável |
| 7 | **Conjunto de calibração do juiz** | Quantos casos anotados à mão, e como separar calibração de teste | Sem separação, o juiz "decora" |
| 8 | **Divisão do conjunto** | Desenvolvimento, calibração, regressão | Evita ajustar o prompt no conjunto em que se mede |
| 9 | **Camada determinística** | Quais checagens são código (citação existe, trecho é substring, data confere) e quais precisam do juiz | O que é código é grátis, repetível e roda no CI |
| 10 | **Regressão em CI** | O que roda a cada mudança (determinístico, offline) e o que roda sob demanda (modelos, pago); como o teto de custo é imposto | Meta de 12 meses do roadmap |
| 11 | **Local ou remoto** | Rodadas contra stdio (determinístico) ou a URL pública (tem limite de taxa e token) | O remoto cobre o caminho HTTP; o limite de taxa limita as rodadas |
| 12 | **Meister: sim ou não** | O P2 usou `meister orchestrate`; o núcleo à mão não cabe nele, o entorno talvez sim | O CLAUDE.md global manda perguntar antes de implementar por outro meio |
| 13 | **Hook do P2 e o server remoto** | Estender o matcher para `mcp__taxlaw-remoto__.*`? Mudança no P2, não no P3 | Afeta o caso H12 |
| 14 | **Relatório** | Formato do "antes/depois", registro de modelo, tag do P2, `corpus.versao`, preço usado | Critério de concluído do roadmap |
| 15 | **Taxonomia** | Começa vazia (codificação aberta nos traces) | O roadmap pede open e axial coding |

## Ordem sugerida

1. Brainstorming da spec, começando por 1, 6 e 9 (o que é núcleo, o que se anota, o que é código).
2. As 100 perguntas: escritas por pessoas, **antes** de ver respostas do modelo.
3. Primeira rodada pequena (10 casos), com **previsão escrita antes**.
4. Codificação aberta nos traces; só depois a taxonomia.
5. Juiz e calibração; depois a regressão em CI.
