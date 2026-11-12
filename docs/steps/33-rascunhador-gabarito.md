# Passo 33: o rascunhador do gabarito

Tarefa 18 do plano (revisões R2 e R4). Um modelo de outra família rascunha o gabarito de cada pergunta a partir do corpus inteiro do P2; o código confere o rascunho e recusa o que estiver errado. Quem confirma o gabarito é você.

**Modelo:** `deepseek/deepseek-v4.1-flash-1017` (família DeepSeek, versão com data, contexto de 1M, US$ 0,30/1,20 por milhão de tokens), decidido em 2026-11-12. O juiz será de outra família.

**Quem escreveu:** entorno. O código e os testes foram escritos por um subagente Haiku 5.5 a partir do texto da tarefa; a sessão principal revisou, acrescentou 5 testes e mudou o registro do rascunho (versão do corpus e do prompt) e o aviso de teto. O prompt do rascunhador ([`config/drafter_prompts/gabarito.md`](../../config/drafter_prompts/gabarito.md)) foi escrito pela sessão principal.

## O que mudou

- **[evals/drafter.py](../../evals/drafter.py):**
  - `draft_gabarito(case, corpus, *, client, model, guard, ledger, traces_dir, call_tool, prompt, reference_date, corpus_version)`:
    1. **recusa antes de chamar o modelo** se o caso já tem trace em `traces_dir` (busca recursiva, nome exato `<case_id>-<8 hex>.json`): o gabarito nunca vê resposta do modelo avaliado;
    2. manda ao modelo **só a pergunta, a data de referência e o corpus inteiro** (649 linhas `id | citação | efeitos | texto`, cerca de 45 mil tokens), nunca as ferramentas de busca do P2;
    3. registra o custo no ledger e cobra o teto;
    4. confere o rascunho e junta todos os problemas numa recusa só: formato do JSON, data igual à pedida, `validate_case`, **trechos literais** e, só se tudo isso passou, `verify_case` contra o P2.
  - `check_quotes`: cada trecho citado tem de estar, palavra por palavra, no texto de **alguma versão** do dispositivo (13 ids do corpus têm mais de uma versão no tempo). Só espaços e quebras de linha são normalizados. Cada id esperado precisa de pelo menos um trecho.
  - `write_draft`: grava `drafts/cases/<case_id>.v<N>.json`, nunca sobrescreve, número da versão pelo maior existente mais um.
  - `draft_batch`: um rascunho recusado não para o lote; o teto para o lote e a exceção leva uma nota com os rascunhos já gravados.
  - O rascunho gravado traz `corpus_version` (o mesmo hash do runner) e `prompt_sha`, e a justificativa e os trechos passam por `redact_taxpayer_ids`.
  - `python -m evals.drafter CASO.json --reference-date AAAA-MM-DD --model ... --p2-dir ../projeto02 --budget-usd 0.05`: sem `OPENROUTER_API_KEY` no ambiente, recusa sem chamar nada e sem imprimir valores.

**Decisões do entorno** (registradas também no plano):
- A **data de referência é parâmetro**, não escolha do modelo; um rascunho com outra data é recusado.
- `verify_case` recebe o `call_tool` injetado: na rodada real, o P2 de verdade (`make_p2_caller`); nos testes, um falso.
- `parse_draft` aceita o texto inteiro como JSON, ou um bloco ```json; prosa antes ou depois é recusada. A primeira execução real dirá se isso é estrito demais para o DeepSeek.
- **Custo jogado fora, aceito:** quando o teto estoura numa chamada, a resposta dessa chamada (já paga) não é gravada. Custa uns US$ 0,015.

## Como rodar

```bash
uv run pytest tests/test_drafter.py -v
```

## O que observar

- **Vermelho antes:** 44 testes do Haiku falharam por asserção (stub com as assinaturas) antes da implementação; os 2 de versão do corpus e de nota do teto falharam antes da mudança da sessão principal.
- **Suíte:** 49 testes em `tests/test_drafter.py`, **337** no total, verde duas vezes seguidas.
- **Teste de mutação:** 18 mutações. Na primeira rodada, 4 sobreviveram:
  - `fullmatch` trocado por `search` na busca de trace: um trace do caso `xc01` bloquearia o caso `c01`. Ganhou teste;
  - sem redigir CPF nos trechos: ganhou teste com um corpus sintético que contém um número gerado na hora;
  - versão por quantidade de arquivos em vez do maior número: só aparece com lacuna (v1 e v3). Ganhou teste;
  - `open(..., "w")` em vez de `"x"`: equivalente, porque o número é sempre novo; fica como defesa contra duas gravações simultâneas.

  Agora 17 de 18 caem; a que sobra é a equivalente.

## Confirmação na prática (2026-11-12)

Uma execução real, aprovada, com teto de US$ 0,05: a semente 4 de [`docs/p2/casos-candidatos.md`](../p2/casos-candidatos.md), "O que é cesta básica na reforma?", data de referência 2027-01-01, P2 na tag `step-16`. O caso e o rascunho ficaram fora do repositório (pasta temporária); o ledger, em `runs/`, fora do git.

| Medida | Valor |
|---|---|
| Tokens de entrada | 54.902 (a estimativa era uns 45 mil) |
| Tokens de saída | 2.788 |
| Custo (medido pelo OpenRouter) | **US$ 0,0107** |
| Tempo | 15 s |
| Resultado | **aceito** em todas as conferências |

**Confirmado:**
1. **O formato serve.** O DeepSeek respondeu num JSON que o `parse_draft` aceitou de primeira, sem texto em volta.
2. **Os trechos são literais.** Os 3 trechos citados passaram na comparação palavra por palavra com o texto do corpus, e o P2 confirmou que os 3 ids existem em 2027-01-01.
3. **O rascunho foi além da semente.** A semente apontava só `LC214.art125`; o rascunho trouxe também `EC132.art8` e o parágrafo único, que criam a Cesta Básica e remetem à lei complementar. Se isso é o gabarito certo, quem decide é você, na confirmação: é exatamente o tipo de mudança que a pergunta de previsão conta.
4. **A data veio igual**, e o registro traz `corpus_version` `c269388fb2bd` e `prompt_sha` `d2c9189eabee`.

**Custo para os 100 casos:** cerca de US$ 1,10, uns 25 minutos em série.

**Ficou sem confirmação:** um caso `nao` (sem resposta no corpus) e um caso com versões no tempo (semente 3). São os próximos a olhar quando as suas perguntas existirem.

## Pergunta de previsão

Em quantos dos 10 primeiros rascunhos você vai mudar algum campo ou marcar `disputed`?
