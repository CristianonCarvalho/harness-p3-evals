# Passo 43: o comando de rodada em lote

A piloto (passo 40) rodou por um script descartável. Para o M5, a rodada passa a ser um comando do projeto: `run-round`.

## O que mudou

- **[evals/round.py](../../evals/round.py)** (novo):
  - três condições:

    | Condição | Casos | Server | Skill |
    |---|---|---|---|
    | `com_skill` | todos | local | sim |
    | `sem_skill` | subconjunto `sem_skill` | local | não |
    | `remoto` | subconjunto `remoto` | remoto | sim |

  - `plan_round(cases, conditions)`: pares (condição, caso), por condição e depois por `case_id`;
  - `run_round(...)`: um diretório de trabalho por condição, um teto (`BudgetGuard`) para a rodada inteira, uma semente para os números sintéticos, e um resumo em `traces/rounds/<round_id>/_round.json`. Os traces vão para `traces/rounds/<round_id>/<condição>/`;
  - recusa uma rodada cujo diretório já existe, para não misturar traces, e confere as variáveis do server remoto antes de rodar qualquer coisa.
- **CLI:** `python -m evals.cli run-round`. O código de saída é 1 se o teto parou a rodada ou se algum caso ficou para investigar; com `--dry-run`, só conta.
- **23 testes** em `tests/test_round.py`. Programado pelo Haiku e revisado pelo Claude, que acrescentou 2 testes (abaixo).

## Como rodar

```bash
uv run python -m evals.cli run-round --model claude-haiku-5-5 --p2-dir ../projeto02 --p2-tag step-16 --budget-usd 1.05 --per-case-usd 0.25 --dry-run
```

Sem `--dry-run`, roda e gasta. A condição `remoto` exige `TAXLAW_REMOTE_URL` e `TAXLAW_HTTP_TOKEN` no ambiente.

## O que observar

- **Suíte:** 632 testes, verde duas vezes (634 depois da correção abaixo).
- **Teste de mutação:** 9 mutações. Duas sobreviveram na primeira passada e ganharam teste:
  - a condição `remoto` rodando com as ferramentas do server local: passaria como `ok`, com o número errado;
  - a semente ignorada: a mesma rodada daria CPF/CNPJ sintéticos diferentes a cada vez.
  
  Agora as 9 caem.
- **`--dry-run` nos casos reais:** 100 com skill, 20 sem skill e 8 remotos, num total de 128.

## A rodada completa no Haiku (2026-11-14)

**Primeira tentativa: 120 `erro`, US$ 0.** O comando passava ao `claude` o `--mcp-config` com caminho **relativo** (`workdirs/...`) e, ao mesmo tempo, `cwd=workdir`. Lá dentro, o caminho não existia, e o `claude` saía com código 1, sem `init`. A piloto não viu isso porque usou caminho absoluto. O runner também descartava o `stderr`, então o trace dizia só "stream sem evento init".

**Correções em [evals/runner.py](../../evals/runner.py):**
- o `--mcp-config` agora vai sempre absoluto;
- num erro de saída, o fim do `stderr` do `claude` vai para `errors` do trace.

Mais 2 testes, que falharam antes da correção. Suíte: 634, verde duas vezes.

**Lição:** 120 casos marcados para investigar não pararam a rodada. Sem gasto, o custo foi só tempo; um próximo passo é parar a rodada depois de alguns casos seguidos para investigar.

**Segunda tentativa (`haiku-20261114-b`):**

| Condição | Traces | Status | Custo médio | Custo máximo | Chamadas ao P2 (média) | Chamou a skill |
|---|---|---|---|---|---|---|
| com skill | 100 | 100 `ok` | US$ 0,0057 | US$ 0,0092 | 4,2 | 87 |
| sem skill | 20 | 20 `ok` | US$ 0,0050 | US$ 0,0063 | 4,2 | 0 |

**Total: US$ 0,675** de um teto de US$ 1,05. Nenhuma repetição por `erro` e nenhum caso para investigar. A condição remota (8 casos) ficou de fora: faltam `TAXLAW_REMOTE_URL` e `TAXLAW_HTTP_TOKEN` no ambiente.

## Pergunta de previsão

Na rodada remota, os 8 casos vão sair `ok` na primeira tentativa?
