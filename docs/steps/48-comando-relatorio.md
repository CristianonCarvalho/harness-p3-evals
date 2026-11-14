# Passo 48: o comando que gera o relatório

Marco M9, primeira parte. O [evals/report.py](../../evals/report.py) já montava e formatava o relatório (passo 27), mas nenhum comando juntava os dados reais.

## O que mudou

- **[evals/make_report.py](../../evals/make_report.py)** (novo), com o comando `python -m evals.cli make-report`:
  - lê os traces de uma rodada (`--round-dir traces/rounds/<id>`), os casos, os julgamentos e a anotação;
  - só os traces `ok` entram; os outros são contados por status;
  - a condição vem do trace: `remoto` se o server é remoto, senão `com_skill` ou `sem_skill`;
  - por critério, o **código decide quando pode** e o juiz só entra no `needs_judge`:
    - C1 e C2: código, e o juiz quando o código devolve `needs_judge`;
    - C3: sempre o juiz;
    - C4: só em H12 e H13;
  - **julgamento obsoleto não conta:** se o modelo ou o hash dos prompts do julgamento difere do `config/run.json`, o julgamento é ignorado e contado em `stale_judgments`;
  - o TPR/TNR do juiz usa a mesma conta da recontagem do `check-repo`, então os dois números são sempre iguais;
  - o cabeçalho traz o que o `check-repo` compara com o `config/run.json`, e mais os pendentes por critério;
  - grava `reports/<data>-<round_id>.json` e `.md`, e recusa sobrescrever.
- **22 testes** em `tests/test_make_report.py`. Programado pelo Haiku e revisado pelo Claude.

## Como rodar

```bash
uv run python -m evals.cli make-report --round-dir traces/rounds/haiku-20261114-b --date 2026-11-14
```

## O que observar

- **Suíte:** 659 testes, verde duas vezes.
- **Teste de mutação:** 7 mutações, as 7 caem (ignorar o remoto, ignorar o juiz no C3, C4 em todo caso, H13 sem instrução, aceitar traces com `erro`, não contar julgamento obsoleto, somar custo de trace com `erro`).
- **Pendentes na rodada `haiku-20261114-b`:** o juiz só julgou os 30 da amostra cega, então, nos 120 traces, ficam pendentes 82 no C1, 27 no C2 e 90 no C3. Para fechar as taxas, o juiz precisa rodar nos outros 90.

## Pergunta de previsão

Depois do juiz nos 120, qual vai ser a taxa de aprovação no C1 da condição com skill, no conjunto de teste?
