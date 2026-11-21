# Passo 58: o check-repo confere o hash dos prompts do juiz

Correção feita depois do fechamento do P3. A lacuna apareceu no ensaio do lote do P4 (ver [relatório do lote](../../../projeto04/docs/relatorio-lote.md), seção "Lacuna encontrada no próprio P3"): editar só o texto de `config/judge_prompts/C1.md` passava em todos os gates.

## O que mudou

- **[evals/consistency.py](../../evals/consistency.py):** a função `_check_prompts_run` compara o `judge_prompts_sha256` de `config/run.json` com `hash_prompts(config/judge_prompts)`. Se os hashes não batem, é um problema do `check-repo`. Se a pasta não existe, é um aviso. A checagem roda mesmo sem relatório.
- **[tests/test_consistency.py](../../tests/test_consistency.py):** o teste `test_prompt_editado_sem_relatorio_novo_falha` cobre o caso: o relatório e o `run.json` batem, o prompt muda, e o check precisa acusar.

## Antes e depois

- **Antes:** o teste novo falhou com `0 == 1`, ou seja, nenhum problema para um prompt editado. Essa era a lacuna.
- **Depois:** o teste passa, e a suíte tem 755 testes verdes (754 antes, mais o novo).
- **No repositório real:** com `config/judge_prompts/C1.md` editado, `check-repo` mostra o problema e sai com 1. Com o arquivo restaurado, sai com 0. A edição foi desfeita com `git checkout`.

## Como rodar

```bash
# Suíte completa (offline)
python3 -m pytest -q

# Consistência do repositório
python3 -m evals.cli check-repo
```

## O que observar

- Se você editar um prompt e não rodar um relatório novo, o `check-repo` falha e diz que falta um relatório novo.
- A checagem lê os mesmos arquivos que `hash_prompts`: `config/judge_prompts/*.md`, em ordem de nome.
- Se a pasta `config/judge_prompts` sumir enquanto o `run.json` declara um hash, o check não falha, só avisa. Essa escolha mantém os testes antigos, que usam um hash fictício sem pasta.

## Pergunta de previsão

Antes de rodar: você edita `C2.md` e não toca em `run.json` nem em `reports/`. O `check-repo` passa ou falha? Por quê?
