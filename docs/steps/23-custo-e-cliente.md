# Passo 23: teto de custo, cliente e ledger herdados do P1

## O que mudou

- `evals/budget.py`: `BudgetGuard(limit_usd)` soma o custo de cada chamada e levanta `BudgetExceeded` ao **atingir ou passar** o teto (D10). A rodada para ao estourar.
- `evals/client.py` e `evals/ledger.py`: o cliente OpenRouter e o ledger de tokens e custo do P1, copiados sem mudar comportamento. O `.env` do P1 **não** foi lido nem copiado.
- `tests/test_client.py` e `tests/test_ledger.py`: 24 testes herdados do P1, adaptados.

## Como rodar

```bash
uv run pytest tests/test_client.py tests/test_ledger.py tests/test_budget.py -v
```

## O que observar

- **O plano supunha que os testes do P1 dependiam só do cliente e do ledger, e não era verdade:** eles também importavam `agent.cli` e `agent.config`. O Haiku parou e perguntou, e eu decidi copiar só o cliente e o ledger e **remover os 5 testes `test_cli_*`**, que testam o CLI do P1 e não o cliente nem o ledger. Os outros 24 ficaram intactos.
- Teste de mutação no teto de custo: não acumular, estourar só ao passar (`>` em vez de `>=`), nunca estourar e aceitar teto zero caem todas.
- O cliente e o ledger do P1 usam transporte falso e `sleep` injetado: nenhum teste chama rede.

## Pergunta de previsão

Quantos USD você espera que 100 chamadas curtas do juiz custem? Meça na piloto (M4) e compare.
