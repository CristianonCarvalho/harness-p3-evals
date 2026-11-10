# Passo 27: o relatório

## O que mudou

`evals/report.py` produz o relatório de D12:

- `resolve_verdict`: o **código decide quando pode**; o juiz só decide o que o código deixou como `needs_judge`; sem nenhum dos dois, o veredito é `n/a` (pendente) e **nunca inventado**.
- `build_report`: taxa de aprovação **por condição e por critério**, com `n`, intervalo de Wilson e quem decidiu (código ou juiz). **A taxa principal usa só o conjunto de teste**; o de desenvolvimento vai para `dev_diagnostic`. Vereditos `n/a` ficam fora de `n` e são contados à parte em `excluded`.
- Seção do juiz com TPR/TNR e `calibrated`: só é verdadeiro com **10 ou mais** casos de cada classe e as duas taxas definidas.
- `compare`: antes/depois com a marca **"dentro do ruído"**, **"diferença real"** ou **"sem dados"**.
- `render_markdown`, `write_report` e `load_report`: o JSON é a fonte de verdade (chaves ordenadas, para o diff do git ficar legível) e o Markdown é gerado dele.

## Como rodar

```bash
uv run pytest tests/test_report.py -v
```

## O que observar

- **Divisão do trabalho:** eu escrevi os 19 testes (o desenho), e o Haiku implementou até ficarem verdes. O RED foi confirmado antes de passar a tarefa.
- Teste de mutação: 16 mutações (inverter a precedência código/juiz, misturar condições, incluir o desenvolvimento na taxa principal, contar `n/a` em `n`, inverter o ruído, não ordenar as chaves…), todas caem. Uma sobrevivia (aceitar TNR nulo com muitos reprovados) e ganhou um teste.
- Com 70 casos de teste, uma diferença de poucos pontos entre dois modelos sai marcada como "dentro do ruído". É isso que impede uma melhora de ser anunciada sem número.

## Pergunta de previsão

Entre Sonnet 5.5 e Haiku 5.5, em quantos dos quatro critérios você espera uma **diferença real**? Escreva o número antes da primeira rodada.
