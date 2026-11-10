# Passo 15: privacidade (CPF/CNPJ)

## O que mudou

`evals/privacy.py` detecta sequências com formato de CPF (11 dígitos) ou CNPJ (14), com ou sem pontuação, sem olhar o dígito verificador (conservador de propósito), redige o número e **gera números sintéticos válidos em tempo de execução**. Nenhum número de documento é escrito no repositório, nem nos testes. O `pyproject.toml` ganhou `pythonpath = ["."]`, para o `pytest` importar sempre do código-fonte e nunca de uma cópia instalada.

## Como rodar

```bash
uv run pytest tests/test_privacy.py -v
```

## O que observar

- Os testes geram o número com `make_synthetic_cpf(random.Random(semente))` e o validam com `is_valid_cpf`. É o jeito de testar sem escrever um CPF.
- Teste de mutação feito na conferência: trocar a regra do dígito verificador (`return 0 if resto < 2 else 11 - resto` por `return 11 - resto`) derruba 3 testes. Os testes têm dentes.
- Limite conhecido: um número com espaços entre os dígitos (`123 456 789 01`) **não** é detectado, como o hook do P2 também não vê números disfarçados.

## Pergunta de previsão

Em quantos arquivos do repositório você esperava que `scan_files` achasse algo? Resultado: nenhum, em 31 arquivos varridos.
