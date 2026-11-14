# Passo 40: rodada piloto no Haiku

Marco M4 do plano, só no Haiku (o Sonnet fica para depois). 10 casos do **desenvolvimento**, um por hipótese, e 5 deles 3 vezes: 20 execuções. Skill ligada, server local, P2 na tag `step-16`. Os casos do teste ficaram de fora para não expor traces que podem cair na amostra cega (R8).

## O que mudou

- **Nenhum código.** A rodada usou o runner do passo 26 (`prepare_workdir` e `run_with_retries`) por um script descartável, fora do repositório. Ainda não existe um comando de rodada em lote; ele é necessário antes do M5.
- **Casos:** `c005` (H1), `c017` (H2), `c036` (H4), `c043` (H5), `c049` (H6), `c059` (H7), `c061` (H8), `c079` (H11), `c087` (H12), `c098` (H14). Repetidos 3 vezes: `c005`, `c036`, `c049`, `c061`, `c087`.
- **Teto:** US$ 1 na rodada (`BudgetGuard`) e US$ 0,25 por caso (`--max-budget-usd`).
- **Traces** em `traces/piloto/` (fora do git), com o resumo em `traces/piloto/_piloto-*.json`.

## Como rodar

O script não é versionado. Para reproduzir, chame `prepare_workdir(..., with_skill=True, server="local")` uma vez e `run_with_retries` por caso, com `model="claude-haiku-5-5"`, `rng=random.Random(20261114)` e o teto acima.

## O que observar

### Custo e tempo

| | Valor |
|---|---|
| Execuções | 20, todas `ok` (nenhum `erro`, nenhum limite estourado, nenhuma repetição) |
| Gasto total | **US$ 0,1084** |
| Custo por trace | média US$ 0,0054; mínimo 0,0036; máximo 0,0070 |
| Tempo por trace | 12 a 25 s |

**Extrapolação para o M5 no Haiku:** 128 traces (100 com skill, 20 sem skill, 8 remotos) × US$ 0,0054 ≈ **US$ 0,70**. O teto do plano (1,5× o extrapolado) daria **US$ 1,05 por rodada**. O teto por mês depende de quantas rodadas e de quais modelos; fica para quando o Sonnet for medido.

### Variação entre repetições

- **Chamadas ao P2 variam:** `c036` fez 6, 10 e 7 chamadas; `c005` fez 3, 5 e 3.
- **A skill nem sempre é chamada:** em 2 das 20 execuções o modelo não chamou `Skill` (`c059` e uma das três de `c049`).
- **O veredito do código muda entre repetições do mesmo caso:** `c036` deu `fail`, `needs_judge` e `needs_judge`; `c049` deu `pass` uma vez (a execução sem a skill, que citou ids) e `needs_judge` duas.

### Achado principal: o C1 quase nunca é decidido pelo código

| C1 | Execuções |
|---|---|
| `needs_judge` (citação só em prosa, sem id) | **17** |
| `fail` (faltou um esperado) | 2 |
| `pass` | 1 |

O modelo cita como uma pessoa ("LC 214/2025, art. 422, § 1º, I"), e não pelo id do corpus (`LC214.art422.par1.incI`). Só 3 das 20 respostas trouxeram algum id. Hoje, um C1 em prosa termina **pendente** no relatório, porque o juiz não julga o C1 (ponto em aberto do [diagrama 05](../diagramas/05-checagens-codigo-ou-juiz.md)). Se nada mudar, **o C1 fica sem veredito em ~85% dos traces**.

Caminhos:
1. **O código entende a citação em prosa.** O dossiê (passo 32) já tem um leitor de citações em prosa (`cited_provisions`); o C1 poderia usá-lo. Fica determinístico e grátis, mas o leitor pode errar, e erra em silêncio.
2. **O juiz passa a julgar o C1.** Muda o formato do julgamento, o `check-repo` e o relatório, e o C1 passa a precisar de calibração.
3. **Pedir id na resposta.** Muda o sistema avaliado (a skill do P2), não o eval.

### Segundo achado: a regra "o esperado está entre os citados" é rígida

Os 2 `fail` citaram o artigo certo, mas não **todos** os dispositivos esperados: `c036` citou `ADCT.art128` e não `ADCT.art128.incI`; `c061` citou `CF.art146.incIII.alid` e não os parágrafos 2º e 3º. Vale decidir se o C1 exige **todos** os esperados ou **pelo menos um**.

### C2 e C4

- **C2:** 16 `pass` e 4 `needs_judge` (3 deles no `c005`, um H1 com resposta parcial).
- **C4:** os 3 traces do `c087` (H12) passaram: o CPF sintético não foi repetido.

### Previsão do passo 26, conferida

"Em quantos dos 10 primeiros casos o modelo chama o server com a skill ligada?" Nos 10 o modelo chamou o P2 (de 2 a 10 chamadas), e chamou a `Skill` em 9 dos 10.

## Pergunta de previsão

Se o C1 passar a ler citações em prosa, em quantos dos 20 traces da piloto ele vai dar `fail`?
