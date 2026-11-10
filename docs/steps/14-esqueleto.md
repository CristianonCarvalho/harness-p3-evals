# Passo 14: esqueleto do projeto

## O que mudou

Nasceu o pacote Python `evals` (`pyproject.toml`, `evals/__init__.py`), com `pytest` e `pytest-timeout` (teste que pode pendurar tem tempo máximo de 30 s). O `.gitignore` ganhou `workdirs/`, `.claude/settings.local.json` e `.superpowers/`. Primeiro código do projeto, feito pelo Haiku 5.5 e conferido na sessão principal.

## Como rodar

```bash
uv sync
uv run pytest -q
```

Se você mudar `evals/` e o `uv` não perceber, rode `uv sync --reinstall-package evals`: o `uv` só reconstrói o pacote local quando o `pyproject.toml` muda.

## O que observar

- O teste falhou duas vezes antes de passar: a primeira por falta do pacote, a segunda porque o `.venv` ainda tinha o build vazio. A segunda falha não é do código, é de cache.
- `annotations/`, `judgments/`, `cases/`, `reports/` e `config/` **não** estão no `.gitignore`: são versionados.

## Pergunta de previsão

Quantos módulos de `evals/` você espera que precisem de rede para serem testados? Esperado: nenhum.
