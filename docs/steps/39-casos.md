# Passo 39: os 100 casos, com gabarito confirmado e divisão sorteada

Marco M1 do plano. Os dados que faltavam para rodar a avaliação: 100 perguntas, cada uma com um gabarito confirmado por você e com o lado da divisão (desenvolvimento ou teste) sorteado com semente.

## O que mudou

1. **Perguntas** ([`drafts/questions/`](../../drafts/questions/)):
   - o DeepSeek rascunhou 100 candidatas ([`config/drafter_prompts/perguntas.md`](../../config/drafter_prompts/perguntas.md), US$ 0,0489), na distribuição por hipótese H1 a H14 (sem H13);
   - você revisou com o [`prompt-revisao.md`](../../drafts/questions/prompt-revisao.md): **61 mantidas, 37 reescritas, 2 cortadas e 2 escritas por você**. Cada caso guarda a origem em `origin` (`ai_kept`, `human_rewritten`, `human_written`).
2. **Gabaritos:** o rascunhador do passo 33 rodou nos 100 (US$ 1,1027, data de referência 2026-11-13). **Nenhum foi recusado pelo código** (trechos literais, ids no P2, data, formato). Você confirmou cada um na [folha de confirmação](../../drafts/questions/gabaritos-confirmar-v1.md): **92 confirmados e 8 mudados** (`c007`, `c010`, `c016`, `c041`, `c045`, `c068`, `c073`, `c093`), nenhum `disputed`. O rascunho fica em `drafts/cases/<id>.v1.json` e a decisão em `gabarito_review` de cada caso.
3. **Casos** ([`cases/`](../../cases/)): `c001` a `c100`, conferidos por `validate_case` e por `verify-gabarito` contra o P2 de verdade (todo dispositivo esperado existe na data). Subconjuntos: `sem_skill` nos 20 de H2 e H11; `remoto` nos 8 de H12.
4. **Divisão:** `apply-splits --seed 20261114`, estratificada pela hipótese principal: **68 no teste e 32 no desenvolvimento** (o arredondamento por hipótese tirou 2 do alvo 70/30). Semente em `cases/_split_meta.json` e em `config/run.json`. No teste: 6 casos H12 e 14 do subconjunto sem skill.

## Como rodar

```bash
uv run python -m evals.cli verify-gabarito --p2-dir ../projeto02
```

```bash
uv run python -m evals.cli check-repo
```

## O que observar

- **Onde o rascunhador errou:** nas perguntas que você manteve como a IA escreveu, o palpite feito na criação divergiu do gabarito em 21 casos; você olhou esses primeiro. Das 8 mudanças, a maioria troca o "existe resposta" (por exemplo, `c010`: a lista do Anexo XVII não está no corpus, e o rascunho tinha respondido "sim" com um artigo da transição).
- **Taxa de mudança do gabarito:** 8 de 100. É o número que o relatório da revisão (passo 36) mostra como "gabaritos mudados".
- **Limite:** a primeira versão das perguntas e dos gabaritos é de IA. A curadoria (cortar, reescrever, confirmar, mudar) é sua, e cada caso diz a origem.
- **Falso positivo de privacidade:** o resumo do lote gravava o custo com 11 casas decimais, e o detector de CPF acusou. O valor foi arredondado.

## Pergunta de previsão

Na rodada piloto, em quantos dos 68 casos de teste o modelo vai reprovar em pelo menos um critério?
