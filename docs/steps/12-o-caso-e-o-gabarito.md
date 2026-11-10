# Passo 12: o caso e o gabarito

## O que mudou

A spec ganhou a decisão D13: cada caso é um `cases/<id>.json` versionado, com pergunta, hipótese, parte da divisão, marcas de subconjunto e um gabarito mínimo estruturado (`answer_exists`, `expected_provisions`, `reference_date`, `disputed`), escrito antes de ver o modelo e conferido offline contra as ferramentas. A pendência anterior (formato do caso) foi resolvida, e a revisão deixou outra no lugar: a definição do C1. Nenhum código foi escrito.

## Como rodar

Não há o que rodar. Escolha 3 das sementes de `docs/p2/casos-candidatos.md` (uma de conteúdo, uma de "não sei" e uma de data) e escreva à mão o gabarito de cada uma no formato de D13. Não olhe a resposta do modelo antes.

## O que observar

- Foi fácil dizer `answer_exists` (sim, não ou parcial)? Onde ficou em dúvida, o caso provavelmente é `disputed`.
- Algum campo do gabarito faltou para você dizer o que é uma boa resposta? Esse campo falta no formato.

## Pergunta de previsão

Em quantos dos 3 casos você acha que o dispositivo esperado é o mesmo que o modelo vai citar? Escreva o número agora, sem rodar o modelo, e compare depois.
