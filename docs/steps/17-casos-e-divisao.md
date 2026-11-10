# Passo 17: casos, gabarito e divisão sorteada

## O que mudou

`evals/cases.py` valida o caso e o gabarito (D13): hipóteses H1 a H14, `answer_exists` coerente com `expected_provisions`, ids no formato real do corpus, data ISO, e pergunta sem número de documento (só os marcadores `{CPF}` e `{CNPJ}`). Também sorteia a divisão desenvolvimento/teste (D6): **determinística para a mesma semente e estratificada pela primeira hipótese de cada caso**. `extract_ids` extrai ids de dispositivo de um texto.

## Como rodar

```bash
uv run pytest tests/test_cases.py -v
```

## O que observar

- Os testes do plano deixavam dois buracos, que o teste de mutação revelou: remover a barreira no fim do `ID_RE` e ignorar a estratificação **não derrubavam nenhum teste**. Acrescentei dois testes (`test_extract_ids_rejects_an_id_with_a_garbage_suffix` e `test_split_keeps_each_hypothesis_proportion`), e agora as duas mutações caem.
- Um teste que escrevi estava errado: `CF.art155.par3.xyz` é texto legítimo depois de um id válido, não um id quebrado. Corrigi o teste, não o código.
- `ID_RE` não é o formato da **anotação** (o núcleo, Tarefa 5, é seu): é só o formato do **caso**, que é entorno.

## Pergunta de previsão

Com 100 casos e 14 hipóteses, quantos casos de teste restam para a hipótese com menos casos? Com a distribuição que você escrever no M1, calcule antes de sortear.
