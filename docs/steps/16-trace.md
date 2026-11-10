# Passo 16: formato do trace

## O que mudou

`evals/trace.py` valida o trace (D5), gera o `trace_id` e grava um JSON por execução **sem nunca sobrescrever** (modo `"x"`): o trace é imutável. Com `status: "ok"`, todo evento precisa de `result_raw`; em execução interrompida (`erro`, `estourou_limite`) ele pode faltar, porque a execução morreu no meio.

## Como rodar

```bash
uv run pytest tests/test_trace.py -v
```

## O que observar

- Teste de mutação feito na conferência: trocar o modo `"x"` por `"w"` derruba o teste de não-sobrescrita; exigir `result_raw` também em execução interrompida derruba o teste da execução interrompida.
- O trace real vive em `traces/`, fora do git. O que vai ao git são fixtures sintéticas pequenas.

## Pergunta de previsão

Qual campo do trace você acha que o adaptador do Claude Code terá mais dificuldade de preencher? Compare com o resultado na Tarefa 12.
