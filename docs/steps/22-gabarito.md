# Passo 22: conferência do gabarito contra o P2

## O que mudou

`evals/gabarito.py` confere o gabarito de um caso (D13) chamando as ferramentas do P2 **sem modelo nenhum**: para cada dispositivo esperado, pergunta ao `obter_dispositivo` se ele existe na data de referência e se as ferramentas devolvem `efeitos`. Um gabarito que não passa é recusado. `make_p2_caller` monta o comando real do cliente do P2 (`uv run python client/taxlaw_client.py --json obter <id> --data <data>`); nos testes, o subprocesso é sempre um falso.

Também nasceu `tests/__init__.py`, para que os testes importem `make_case` de `tests/test_cases.py` sem `conftest.py`.

## Como rodar

```bash
uv run pytest tests/test_gabarito.py -v
```

A conferência de verdade (M3) roda como comando, com um checkout do P2 na tag fixada, e fica para a Tarefa 15.

## O que observar

- Os testes do plano eram fracos: **7 de 8 mutações sobreviviam**. Quase só olhavam a mensagem de erro e o início do comando. Escrevi cinco testes (argumentos da chamada, `encontrado: false` com `efeitos` soltos, código de saída 1 vs 2, ferramenta desconhecida, `--json` e timeout), e as oito caem agora.
- A spec (D13) fala em conferir "o `efeitos.desde` do caso", mas o gabarito não guarda uma data esperada. A conferência confere que o dispositivo **existe na data** e que as ferramentas **devolvem `efeitos`**. Se você quiser um `efeitos.desde` esperado no gabarito, é uma mudança em D13.

## Pergunta de previsão

Quantos dos gabaritos que você escrever à mão vão falhar na primeira conferência? Escreva o número antes do M3 e compare.
