# Passo 51: os 70 rascunhos para a anotação revisada

Marco M7b, primeira parte. Para chegar a 100 traces anotados (critério de concluído 2), você vai revisar 70 traces a partir de um rascunho da IA.

## O que mudou

- **Sorteio** (semente 20261115) dos 70 entre os 90 traces da rodada `haiku-20261114-b` fora da amostra cega, em [`drafts/selecao-revisao.json`](../../drafts/selecao-revisao.json): 41 do teste e 29 do desenvolvimento; 55 com skill e 15 sem skill. Os outros 20 ficam de **reserva** para estender a amostra cega.
- **Prompt do rascunhador** ([`config/drafter_prompts/anotacao.md`](../../config/drafter_prompts/anotacao.md)) alinhado à régua atual: no C1, todos os esperados, e faixa de artigos ou nome de norma não contam como citação; no C3, a referência é o `answer_exists` do gabarito.
- **Rascunhos:** 70 em `drafts/annotations/<trace_id>.json`, pelo DeepSeek (`deepseek/deepseek-v4.1-flash-1017`), por **US$ 0,19**.
- **Defeito no rascunhador ([evals/annotation_drafter.py](../../evals/annotation_drafter.py)):** em 4 traces, o raciocínio do DeepSeek gastou todo o `max_tokens` (4.096), e a resposta veio vazia (`finish_reason: length`). O lote inteiro quebrava com `AttributeError`. Agora:
  - resposta vazia recusa só aquele trace, com o motivo, e o lote segue;
  - o limite subiu para 16.000 tokens.
  
  Um teste novo falhou antes da correção; suíte: 664, verde duas vezes. Mesmo com o limite maior, 3 traces vieram vazios na primeira passada e saíram numa segunda tentativa (um deles usou 15.053 tokens).
- **Dossiês revisados:** os 70 estão em `traces/dossies/revisada/`, fora do git, com a seção "6. Rascunho da IA" preenchida e o formulário em branco (`kind: revised` e o caminho do rascunho já vêm escritos).

## Como rodar

```bash
uv run python -m evals.cli annotate traces/dossies/revisada/c002-d28018ad.md --date 2026-11-15 --traces-dir traces/rounds/haiku-20261114-b
```

## O que observar

**Vereditos do rascunho:**

| Critério | `pass` | `fail` | `n/a` |
|---|---|---|---|
| C1 | 18 | 52 | 0 |
| C2 | 56 | 14 | 0 |
| C3 | 55 | 15 | 0 |
| C4 | 4 | 0 | 66 |

O rascunho reprova bem mais que o juiz e que você nos 30 cegos (no C1, 74% contra 37%; no C2, 20% contra 3%). Se você mudar muitos desses vereditos, isso é o rascunhador errando, e o relatório mostra a taxa de mudança. Se você mudar pouco e o rascunhador errar muito, aparece o aviso de **possível ancoragem** (R5).

## Pergunta de previsão

Em quantos dos 70 rascunhos você vai mudar pelo menos um veredito?
