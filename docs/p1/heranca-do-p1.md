# O que o P3 herda do P1

- **Repositório:** `CristianonCarvalho/harness-p1-agente-minimo`, em `../projeto01`.
- **Lido em:** 2026-11-10 (README e estrutura). Os arquivos `.env` do P1 **não** foram lidos nem copiados.
- **Regra:** copiar um módulo para o P3 é decisão da spec do P3, e o roadmap diz que o **núcleo** do P3 é escrito à mão. O cliente e o ledger **não** são o núcleo (são infraestrutura da rodada), mas essa fronteira é da spec.

## O que existe

| Módulo | O que faz | Interface | Serve ao P3 como |
|---|---|---|---|
| `agent/config.py` | Lê `.env` (formato `CHAVE=valor`) sem sobrescrever o ambiente | `load_config() -> Config` | configuração de chaves e modelo |
| `agent/client.py` | Uma chamada ao OpenRouter, HTTP puro com `httpx` | `chat(messages, tools, model) -> dict` | base para chamar o modelo avaliado e o juiz |
| `agent/ledger.py` | Registra eventos e soma tokens e custo por chamada | `Ledger(path)`; `.llm(...)`, `.tool(...)`, `.end(...)`; `.total_cost` | custo por caso e por rodada |
| `agent/loop.py` | Laço de tool use até uma condição de parada | `run(prompt, ctx, client, ledger) -> RunResult` | ponto de partida do agente que usa o server |
| `tasks/NN/` | Tarefa com `check.py` e `prediction.md` | `agent task`, `agent report` | o formato "previsão antes, resultado depois" |

Configuração do P1 (valores padrão): modelo `deepseek/deepseek-v4-flash-0731`, `AGENT_MAX_TURNS=20`, `AGENT_COST_CAP_USD=0.10` por execução.

## O que o P1 já ensinou (e vale aqui)

- **Previsão antes de rodar.** O P1 comparava `prediction.md` com o resultado e calculava a taxa de acerto. No roadmap, "previsão de falhas" é métrica do P3 (meta de 6 meses: acertar metade).
- **Teto de custo por execução** e registro no trace desde o início.
- **"Sem chamada de ferramenta" nem sempre é resposta final:** valide antes de encerrar.
- **Regra no código, não no prompt.**
- **Ledger com fallback de preços:** a tabela de preços muda; o relatório do P3 deve registrar o preço usado.

## O que não vale copiar sem pensar

- As três ferramentas do P1 (`read_file`, `write_file`, `run_command`) não são as do P3. O agente do P3 usa as **duas ferramentas do server do P2**, por MCP.
- O P1 fala só com o OpenRouter. A spec do P3 decide se o modelo avaliado e o juiz usam o mesmo provedor, e a conta e o orçamento de cada um.
- O cliente do P1 é síncrono, e uma rodada de 100 casos com repetições pode pedir paralelismo e *retry*, o que é decisão de projeto do P3.

## Como reaproveitar

Três opções para a spec, da mais acoplada à menos:
1. **Copiar** os módulos para o P3 (independência total, duplicação).
2. **Depender** do P1 como pacote por tag do git (menos código, acopla um repositório de estudo).
3. **Reescrever à mão** o que for núcleo e copiar só o que não for.

Recomendação provisória: a (3), a mesma lógica da independência do avaliador em relação ao avaliado. A decisão fica para a spec.
