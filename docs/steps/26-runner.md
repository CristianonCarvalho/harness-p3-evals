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

## O que ainda não foi conferido na prática

O passo 5 do plano pede **uma execução real com skill e uma sem**, no Haiku, para conferir:
1. que `--strict-mcp-config` e `--tools` de fato tiram o Google Drive e o `Bash` do init;
2. que a ferramenta `Skill` aparece só na condição com skill;
3. que o hook do P2 carrega com `--setting-sources project` (ele roda `uv run` no diretório copiado, sem `.venv`, então a primeira execução pode demorar);
4. que `Skill` e `ToolSearch` existem com esses nomes em `--tools`;
5. os nomes dos limites (`error_max_budget_usd`), estourando o teto de propósito.

Custo estimado: três execuções curtas, alguns centavos. Pede a sua aprovação.

## Pergunta de previsão

Em quantos dos 10 primeiros casos da piloto o modelo chama o server com a skill ligada? E sem a skill?
