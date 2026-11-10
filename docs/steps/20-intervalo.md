# Passo 20: intervalo de incerteza (Wilson)

## O que mudou

`evals/stats.py` calcula o **intervalo de Wilson a 95%** (decisão adiada de D12, tomada aqui) e diz se dois intervalos se sobrepõem. Funciona com n pequeno e com taxas perto de 0 ou 1, onde o intervalo normal dá valores impossíveis. É o que permite o relatório marcar uma diferença como "dentro do ruído" ou "diferença real".

## Como rodar

```bash
uv run pytest tests/test_stats.py -v
```

## O que observar

- Teste de mutação: trocar o `z`, tirar a correção do centro, inverter a sobreposição ou deixar `n == 0` devolver um intervalo derruba um teste cada.
- **Duas mutações não caem, e é esperado:** tirar o `max(0.0, …)` e o `min(1.0, …)`. O intervalo de Wilson nunca sai de [0, 1] matematicamente, então essas travas só protegem contra erro de ponto flutuante, e isso não se observa em teste sem artifício. Fica como defesa e não como comportamento testado.
- Com 56 de 70 (80%), o intervalo vai de 0,69 a 0,88: meia-largura de cerca de 9 pontos.

## Pergunta de previsão

Com 70 casos e 80% de aprovação, de quanto é a meia-largura do intervalo? Resultado: cerca de 9 pontos. Uma diferença de 4 pontos entre dois modelos é ruído.
