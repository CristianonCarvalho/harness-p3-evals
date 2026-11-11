# Passo 26: runner das rodadas

Tarefa 13 do plano. O runner roda um caso no Claude Code contra o P2, entrega a saída ao adaptador (passo 25), grava o trace e cobra o custo.

## O que mudou

- **[evals/runner.py](../../evals/runner.py)**:
  - `prepare_workdir(p2_dir, dest, *, with_skill, server)` copia o checkout do P2 (sem `.git`, `.venv`, `traces`) e grava `p3-mcp.json` só com o server do P2. Sem skill, apaga `.claude/skills/`; o hook fica nas duas condições.
  - `build_argv(model, *, server, max_budget_usd, mcp_config)` e `build_prompt(case, rng)`.
  - `run_case(...)` roda uma vez e devolve o caminho do trace.
  - `run_with_retries(...)` repete só o `erro` e para no terceiro seguido, marcando o caso para investigar (decisão 9 de D2). `estourou_limite` não se repete.
- **Adaptador:** passou a derivar o prefixo das ferramentas e o server exigido de `allowed_servers`, para aceitar o server remoto (`taxlaw-remoto`). Mais 2 testes.
- **31 testes** novos em `tests/test_runner.py` (nenhum chama o `claude`; um `run` falso devolve a fixture real).

### Onde o runner se afasta do desenho do plano

| Plano | Agora | Por quê |
|---|---|---|
| `--setting-sources project` isola | também `--strict-mcp-config`, `--mcp-config` só com o P2 e `--tools Skill,ToolSearch` | A amostra real mostrou o Google Drive do usuário e o `Bash` disponíveis com `--setting-sources project` |
| pergunta no argv | pergunta por **stdin** | `--allowedTools` aceita vários valores: uma pergunta no fim do argv seria lida como ferramenta |
| pergunta como está no caso | pergunta + `Data de referência: AAAA-MM-DD.` do gabarito | Na amostra o modelo usou a data do dia. Sem a data, a mesma pergunta mudaria de resposta conforme o dia da rodada |
| `run_case(..., p2_dir, workdirs, ...)` | `run_case(..., workdir, ...)` | O diretório é preparado uma vez por condição, não por caso: copiar o corpus a cada caso é caro e não muda nada |
| remoto lê URL e token | o `p3-mcp.json` guarda `${TAXLAW_REMOTE_URL}` e `${TAXLAW_HTTP_TOKEN}`, e o Claude Code expande na hora | Nada secreto vai para o disco. O runner recusa antes de rodar se faltar alguma das duas variáveis, sem imprimir valores |

**Decisão minha, reversível:** acrescentar a data de referência à pergunta. A alternativa é você escrever a data no texto de cada caso. A troca é uma linha em `build_prompt`.

**Condições gravadas no trace:** `skill` e `hook` vêm do diretório de fato usado, não de um parâmetro; `hook` só é verdadeiro no server local, porque o hook do P2 não cobre o remoto (H12). `corpus_version` é o início do SHA-256 de `corpus/dispositivos.json`.

**Tempo máximo:** 900 s por caso. Se estourar, o que foi lido vira um trace `erro`, com o motivo.

## Como rodar

```bash
uv run pytest tests/test_runner.py -v
```

## O que observar

- **Vermelho antes:** a coleta falhou porque o módulo não existia.
- **Suíte:** 173 testes, verde duas vezes seguidas.
- **Teste de mutação:** 37 mutações. Na primeira rodada, 3 sobreviveram:
  - uma era equivalente (minha checagem de diretório existente repetia a do `copytree`; removi a minha);
  - duas apontavam testes que faltavam: saída com byte inválido em UTF-8 depois de um timeout, que quebraria com exceção, e uma rodada "remota" que na verdade usou o server local, que passaria como `ok`. Escrevi os dois testes. Agora as 37 caem.

## Confirmação na prática (2026-11-11)

Três execuções reais pelo próprio runner, no Haiku 5.5, com o P2 na tag `step-16`, a pergunta "Qual o percentual do IBS?" e a data de referência 2026-11-11. Custo total: **US$ 0,0125**.

| Execução | Status | Ferramentas no init | Outras ferramentas usadas | Chamadas ao P2 | Custo |
|---|---|---|---|---|---|
| com skill | `ok` | `Skill`, `ToolSearch` e as 2 do taxlaw | `Skill`, `ToolSearch` | 4 | US$ 0,0065 |
| sem skill | `ok` | as mesmas 4 | só `ToolSearch` | 2 | US$ 0,0041 |
| teto de US$ 0,001 | `estourou_limite` | as mesmas 4 | `Skill` | 0 | US$ 0,0019 |

**Confirmado:**
1. **O isolamento funciona.** Nas três, o init mostrou só 4 ferramentas e só o server `taxlaw`. O Google Drive, o Claude Docs e o `Bash` da amostra do passo 25 sumiram.
2. **A skill só aparece na condição com skill.** Sem `.claude/skills/`, o modelo não chamou `Skill`. Com ela, chamou sozinho, de novo.
3. **`Skill` e `ToolSearch` são nomes aceitos por `--tools`.**
4. **O nome do limite é `error_max_budget_usd`**, e o `claude` sai com código 1. O runner manteve `estourou_limite`, como o teste `test_nonzero_exit_does_not_hide_a_limit` previa.
5. **As duas condições deram respostas da mesma natureza** ("não encontrei o percentual no corpus"), com a skill dobrando as chamadas ao P2. É só uma pergunta; não é medida.

**Achado novo:** o teto nativo **passa do limite**: com US$ 0,001, gastou US$ 0,0019. O Claude Code confere o teto entre um turno e outro. Por isso o `BudgetGuard` do P3, que soma o custo de cada trace e para a rodada, continua necessário, e o teto por caso deve ter folga.

**Ficaram sem confirmação nas três primeiras:**
- **A data de referência.** O modelo usou 2026-11-11 nas chamadas, mas essa era também a data do dia: não dava para saber se veio da pergunta ou do relógio. Descuido na escolha da data.
- **O hook.** Nada no trace mostrava se ele rodou. A pasta `.venv` criada no diretório de trabalho não prova nada, porque o próprio server do P2 também roda com `uv run`.

### Quarta execução: o hook e a data (US$ 0,0057)

O runner passou a usar `--include-hook-events`, e a pergunta levou a data **2030-01-01**. A saída bruta está em `traces/amostras/2026-11-11-stream-hook.jsonl`, fora do git, e virou a fixture `tests/fixtures/stream_hook.jsonl`.

- **A data vem da pergunta:** as três chamadas ao P2 usaram `data_referencia: "2030-01-01"`.
- **O hook roda:** cada chamada ao P2 gerou um `hook_started` e um `hook_response` (`hook_event: PreToolUse`, `hook_name: "PreToolUse:mcp__taxlaw__..."`, `outcome: "success"`, `exit_code: 0`). O evento não traz o id da chamada: chega entre o `tool_use` e o `tool_result`.

**O que mudou no adaptador:**
- Cada `hook_response` vai para `trace["hooks"]`. Os de `PreToolUse` são pareados, pela ordem e pelo nome da ferramenta, com a chamada ao P2 que cobriram: `event["hook"] = {"outcome", "exit_code"}`.
- **Se as condições declaram `hook: true`, toda chamada ao P2 tem de ter o seu hook**; senão, o trace é `erro`, com "hook declarado mas não rodou em N chamada(s)". Antes, `hook: true` era uma suposição tirada da existência de `.claude/settings.json`; agora é conferido no que aconteceu.
- Um hook `PostToolUse` não conta: o hook do P2 bloqueia CPF **antes** da chamada.

**Efeito nos testes:** a fixture antiga (`stream_ok.jsonl`) foi capturada sem `--include-hook-events`, então os testes que a usam passaram a declarar `hook: false`. Os testes do runner passaram a usar `stream_hook.jsonl`. 8 testes novos; 181 verdes duas vezes. Teste de mutação da parte nova: 10 mutações; uma sobreviveu (um hook `PostToolUse` seria aceito como cobertura) e ganhou teste. Agora as 10 caem.

**Custo total das quatro execuções de confirmação:** US$ 0,0182. Os traces estão em `traces/confirmacao/`, fora do git.

## Pergunta de previsão

Em quantos dos 10 primeiros casos da piloto o modelo chama o server com a skill ligada? E sem a skill?
