# Passo 25: adaptador do stream-json do Claude Code

Tarefa 12 do plano. O adaptador lê a saída de `claude -p --output-format stream-json` e devolve um trace no formato do P3 (D5). Tudo o que vem depois (anotação, checagens, juiz, relatório) lê só esse formato.

## O que mudou

- **[evals/adapters/claude_code.py](../../evals/adapters/claude_code.py):** `parse_stream(lines, *, case_id, question, conditions, trace_id, allowed_tools, allowed_servers, synthetic_ids=None)`. Nunca levanta por causa do conteúdo do stream: linha ruim, stream cortado ou evento estranho viram `status: "erro"`, com o motivo em `errors`.
- **Fixtures** em `tests/fixtures/`, tiradas da execução real de 2026-11-11, reduzidas aos campos que o adaptador lê, sem `session_id`, caminhos locais nem servers da conta do usuário. O texto da skill foi encurtado, mas mantém um id que as ferramentas não devolveram (`CF.art156-A.par1`).
- **27 testes** novos em `tests/test_claude_code_adapter.py`.

### Onde o adaptador se afasta do esqueleto do plano

O esqueleto foi escrito antes da amostra real. Os achados dela (Tarefa 12 do plano) mudaram cinco coisas:

| Esqueleto | Agora | Por quê |
|---|---|---|
| `events` guarda toda ferramenta | só `mcp__taxlaw__*`; `Skill` e `ToolSearch` vão para `other_tools`, sem resultado | O texto da skill traz ids. Em `events`, ele seria lastro falso para o C1. Há um teste que prova isso com `check_c1` |
| nenhuma checagem de isolamento | `allowed_tools` e `allowed_servers` **obrigatórios**; ferramenta ou server fora da lista, ou taxlaw desconectado, vira `erro` | `--setting-sources project` deixou o Google Drive do usuário e o `Bash` disponíveis ao modelo |
| `input_tokens` do evento | soma da entrada sem cache, da escrita e da leitura de cache; as três parcelas ficam guardadas | O evento trazia `input_tokens: 10` para uma entrada real de cerca de 194 mil |
| limite atingido vira `erro` | `error_max_budget_usd` e `error_max_turns` viram `estourou_limite` | Decisão 8 de D2: limite é comportamento do modelo, não falha de infraestrutura |
| `tool_result` com erro some | `is_error` fica no evento, e o trace continua `ok` | Erro de ferramenta (argumento inválido) é parte do que o modelo fez |

O trace também ganhou `errors` (lista de motivos) e `source.tools`/`source.mcp_servers` (o que a execução de fato tinha). `validate_trace` aceita campos extras.

## Como rodar

```bash
uv run pytest tests/test_claude_code_adapter.py -v
```

## O que observar

- **Vermelho antes:** a coleta falhou porque o módulo não existia.
- **Suíte:** 144 testes, verde duas vezes seguidas.
- **Teste de mutação:** 25 mutações. Na primeira rodada, 3 sobreviveram, e as 3 apontavam testes que faltavam: em todos os testes de stream ruim havia mais de um defeito ao mesmo tempo, e um encobria o outro. Escrevi um teste para cada defeito isolado (linha ruim num stream completo, stream cortado limpo antes do `result`, JSON que não é objeto). Agora as 25 caem.
- **O que não foi conferido em dado real:** os nomes `error_max_budget_usd` e `error_max_turns`. A amostra terminou com `success`. Vale capturar uma execução que estoure o teto de propósito (centavos) antes da rodada piloto.
- **O que o adaptador não resolve:** a data de referência. O modelo escolheu a data do dia (achado 4). Isso se resolve na pergunta do caso ou no runner (Tarefa 13), não aqui.

## Pergunta de previsão

A previsão da Tarefa 3 perguntava qual campo do trace daria mais trabalho ao adaptador. O que deu trabalho não foi um campo: foi **o que não é do P2 entrar no trace como se fosse** (ferramentas da conta, a skill, o `ToolSearch`). Compare com o que você previu.

Nova previsão: na rodada piloto, com o runner isolando a execução, quantos dos 10 traces vão sair com `status` diferente de `ok`?
