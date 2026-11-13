# Passo 34: sorteio da amostra cega e da reanotação

Tarefa 19 do plano (revisões R3 e R8). Sorteia, com semente registrada, os traces que você anota às cegas (a única base do TPR/TNR do juiz) e, depois, os que você reanota para medir a concordância consigo mesmo.

**Quem escreveu:** entorno. O código e 28 testes foram escritos por um subagente Haiku 5.5 a partir do texto da tarefa; a sessão principal revisou, corrigiu a extensão da amostra e acrescentou 2 testes.

## O que mudou

- **[evals/sampling.py](../../evals/sampling.py):**
  - `draw_blind_sample(traces, cases, *, n=30, seed)`: só traces do conjunto de **teste**, com `status: ok`, **no máximo um por caso**, estratificados pela hipótese principal do caso (a mesma regra da divisão teste/desenvolvimento). Cada hipótese presente ganha pelo menos 1 trace; o resto é dividido em proporção ao número de casos, pelo maior resto.
  - `extend_blind_sample(current, ..., n_more, seed)`: acrescenta traces de casos que ainda não estão na amostra, sem tirar nem reordenar os que já estão. **Não exige cobrir toda hipótese**: a extensão serve para achar mais reprovados, e pedir 2 a mais tem de funcionar mesmo com 10 hipóteses.
  - `draw_consistency_sample(blind, *, n=10, seed)`: sorteia só de dentro da amostra cega.
  - `annotations/_samples.json`: as sementes e as listas, em JSON com chaves ordenadas. A amostra cega e a de consistência só podem ser registradas **uma vez**; as extensões se acumulam; a de consistência só aceita traces da amostra cega (com as extensões).
  - `python -m evals.sampling blind|extend|consistency --seed N [...]`: a semente é obrigatória.

**Decisão do entorno: um trace por caso.** Cada pergunta gera dois traces (com e sem a skill). Se os dois caíssem na amostra cega, a anotação do segundo lembraria a do primeiro e deixaria de ser cega. O custo: 30 traces cegos pedem 30 perguntas diferentes no conjunto de teste (com 100 perguntas, há 70 no teste).

## Como rodar

```bash
uv run pytest tests/test_sampling.py -v
```

Quando houver casos e traces:

```bash
uv run python -m evals.sampling blind --seed 20261113 --n 30
```

## O que observar

- **Vermelho antes:** os 28 testes do Haiku falharam com o stub; o teste da extensão pequena falhou antes da correção.
- **Suíte:** 30 testes em `tests/test_sampling.py`, **450** no total, verde duas vezes seguidas.
- **Corrigido na revisão:** a extensão exigia pelo menos um trace novo por hipótese restante. Com 10 hipóteses, não daria para acrescentar 3 traces, justamente quando faltam reprovados (R3). Agora só a amostra inicial exige cobrir todas.
- **Teste de mutação:** 14 mutações. Na primeira rodada, 2 sobreviveram:
  - dar a vaga que sobra ao **menor** resto em vez do maior: o teste de proporção (20/10/5, n=7) tinha restos zero. Ganhou teste com 7/5/3 e n=6;
  - não ordenar os casos antes de embaralhar: equivalente, porque a lista de elegíveis já vem ordenada.

  Agora 13 de 14 caem; a que sobra é a equivalente.

## Pergunta de previsão

Dos 30 traces cegos, quantos terão algum critério reprovado? E quantos reprovados haverá no C3, o critério que só o juiz decide?
