# Passo 49: o primeiro relatório

Marco M9. O juiz congelado (passo 47) rodou nos 90 traces que faltavam, e o `make-report` (passo 48) gerou o primeiro relatório da rodada `haiku-20261114-b`.

## O que mudou

- **Juiz nos outros 90 traces:** US$ 1,24, ledger em `runs/judge-terra-v3-resto-20261114.jsonl`, fora do git. Agora `judgments/` tem os 120 traces, todos com o modelo e o hash do `config/run.json`.
- **[reports/2026-11-14-haiku-20261114-b.md](../../reports/2026-11-14-haiku-20261114-b.md)** e o `.json`. **Nenhum pendente.** O `check-repo` não acusa problema nem aviso: o relatório confere com o `config/run.json`, a recontagem do juiz bate, e o limiar não é cobrado porque nenhum critério está calibrado.

## O que observar

**Taxas de aprovação no teste** (Haiku, P2 `step-16`):

| Critério | Com skill (n=68) | Sem skill (n=14) |
|---|---|---|
| C1 citação | **52,9%** [41,2–64,3] | 28,6% [11,7–54,6] |
| C2 data | 95,6% [87,8–98,5] | 78,6% [52,4–92,4] |
| C3 postura | 75,0% [63,6–83,8] | 57,1% [32,6–78,6] |
| C4 segurança | 100% (n=6) | — |

- **O C1 é o ponto fraco do P2:** quase metade das respostas com skill falha na citação, e 61 dos 68 vereditos vieram do juiz, porque o modelo cita em prosa.
- **A skill parece ajudar em tudo, mas os intervalos se sobrepõem.** Com 14 casos sem skill, nenhuma das diferenças sai do ruído. É uma pista, não um resultado.
- **O C2 é quase todo código** (49 de 68), e o C3 é todo juiz.

**Custo total desta medida:**
- traces do Haiku: US$ 0,68 (é o "custo" do relatório, que conta só a rodada);
- juiz: US$ 1,24 nos 90 traces mais US$ 0,38 na amostra cega com o prompt congelado. As duas versões anteriores do juiz custaram mais US$ 0,72.

**Juiz:** não calibrado em nenhum critério (faltam reprovados na anotação). O relatório diz isso ao lado de cada número.

**Critério de concluído 2 (100 traces anotados): não atendido**, com 30. Faltam 70 anotações a partir do rascunho (M7b).

## Pergunta de previsão

Trocando o Haiku pelo Sonnet (M10), em quantos critérios a diferença sai do ruído?
