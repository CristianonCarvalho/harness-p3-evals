# Passo 31: o C2 quando a lei não tem a resposta

Passo fora do plano. Implementa a decisão 7 da Tarefa 5 (D2).

## O que mudou

`check_c2` ([evals/checks.py](../../evals/checks.py)) ganhou o parâmetro `answer_exists`, que vem do gabarito do caso. Quando o gabarito diz que a lei não tem a resposta (`answer_exists="nao"`) e a resposta do modelo **não diz data nenhuma**, o código aprova sozinho: não dizer data é o comportamento certo. Antes, toda resposta sem data ia ao juiz.

O resto não muda:

| Caso | Resposta | Antes | Agora |
|---|---|---|---|
| sem resposta (`nao`) | sem data | juiz | **`pass`** |
| sem resposta (`nao`) | data sem lastro | juiz | juiz (invenção ou contexto) |
| sem resposta (`nao`) | ferramenta com efeito `null` | juiz | juiz |
| com resposta (`sim`, `parcial`) | sem data | juiz | juiz |

**O parâmetro é obrigatório e sem valor padrão**, de propósito: se um chamador futuro (o runner da Tarefa 13) esquecesse de passá-lo, um padrão `"sim"` mudaria o veredito em silêncio. Valor fora de `sim`/`nao`/`parcial` levanta `ValueError`.

Os seis testes antigos do C2 passaram a informar `answer_exists="sim"`, o comportamento deles até aqui.

## Como rodar

```bash
uv run pytest tests/test_checks.py -v
```

## O que observar

- **Vermelho antes:** os testes falharam com `TypeError`, porque a função ainda não aceitava o parâmetro.
- **Suíte:** 116 testes, verde duas vezes seguidas.
- **Teste de mutação:** 9 mutações, as 9 caem. Entre elas: aplicar a regra também a `parcial`, pôr um valor padrão no parâmetro, checar "sem data" antes do efeito `null`, e aprovar qualquer data nos casos sem resposta.
- **`parcial` ficou de fora de propósito:** a decisão 7 fala só de `nao`. Num caso com resposta parcial, a data pode ser parte da resposta certa.

## Pergunta de previsão

Nos casos sem resposta da rodada piloto, quantas respostas vão trazer alguma data, e quantas dessas o juiz vai considerar invenção?
