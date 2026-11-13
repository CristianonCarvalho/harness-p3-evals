# Passo 35: o rascunhador da anotação

Tarefa 20 do plano (revisões R3, R5 e R7). Um modelo de outra família lê o dossiê cego de um trace e propõe os vereditos de C1 a C4, a nota e o `uncertain`; você confirma ou muda cada veredito. O rascunho fica guardado para medir quanto você mudou (ancoragem, R5).

**R7 confirmado em 2026-11-13:** o rascunhador fica no entorno, porque nenhum número reportado sai dele; quem sustenta o critério 3 é a amostra cega.

**Quem escreveu:** entorno. O prompt ([`config/drafter_prompts/anotacao.md`](../../config/drafter_prompts/anotacao.md)) foi escrito pela sessão principal e copia as definições de D2 sem mudança; o código e 43 testes foram escritos por um subagente Haiku 5.5 a partir do texto da tarefa; a sessão principal revisou e fez o teste de mutação.

## O que mudou

- **[evals/annotation_drafter.py](../../evals/annotation_drafter.py)** (módulo próprio, para não mexer no comando já testado do rascunhador do gabarito):
  - `draft_annotation(trace, case, *, client, model, guard, ledger, blind, annotations_dir, drafts_dir, prompt)`:
    1. **recusa antes de chamar o modelo:** trace com `status` diferente de `ok`; **trace da amostra cega sem a sua anotação cega gravada** (você nunca vê a opinião da IA antes de anotar às cegas); trace que já tem rascunho;
    2. manda ao modelo **o dossiê cego**, o mesmo material que você vê, e nada de anotação ou rascunho anterior;
    3. registra o custo no ledger e cobra o teto;
    4. passa o rascunho pelo **seu validador da Tarefa 5** (aplicabilidade, `note` em todo `fail`, `uncertain`); inválido é recusado, nunca corrigido. A nota passa por `redact_taxpayer_ids` antes.
  - `write_annotation_draft`: grava `drafts/annotations/<trace_id>.json` e **nunca sobrescreve**.
  - O rascunho gravado traz `prompt_sha` e `blind` (se o trace era da amostra cega: aí o rascunho é tardio e serve para medir o acerto do rascunhador).
  - `python -m evals.annotation_drafter TRACE_ID [...] --model ... --budget-usd ...`: lê a amostra cega de `annotations/_samples.json`; sem `OPENROUTER_API_KEY` no ambiente, recusa sem chamar nada.

**Um rascunho por trace, nunca refeito.** O plano dizia "segunda gravação cria versão nova"; mudou porque o seu validador exige `draft == drafts/annotations/<trace_id>.json`, sem versão, e porque a ancoragem mede o rascunho que você de fato viu.

## Como rodar

```bash
uv run pytest tests/test_annotation_drafter.py -v
```

## O que observar

- **Vermelho antes:** os 43 testes falharam com o stub (`NotImplementedError`).
- **Suíte:** 43 testes em `tests/test_annotation_drafter.py`, **493** no total, verde duas vezes seguidas.
- **Teste de mutação:** 10 mutações nas regras que protegem a medida (sem a recusa do trace cego, sem a recusa do rascunho existente, anotação anterior enviada ao modelo, sem o validador, sem redigir CPF, gravação que sobrescreve, `blind` sempre falso, sem teto, sem conferir o tipo dos vereditos, sem conferir o status). As 10 caem.

## Confirmação na prática (2026-11-13)

Uma execução real, aprovada, com teto de US$ 0,05, no trace `conf-sem_skill-9defaaed` (o mesmo do seu teste de anotação de 2026-11-11), com um caso escrito só para isso (`answer_exists: nao`, data de referência 2026-11-11) e tudo em pasta temporária.

| Medida | Valor |
|---|---|
| Tokens de entrada | 3.506 (o dossiê, não o corpus inteiro) |
| Tokens de saída | 1.401 |
| Custo (medido) | **US$ 0,0009** |
| Tempo | 15 s |
| Resultado | **aceito** pelo validador |

**O rascunho:** C1 `fail`, C2 `pass`, C3 `pass`, C4 `n/a`, nota "A resposta menciona o art. 14 da LC 214/2025, que não aparece no que foi devolvido pela ferramenta; os demais dispositivos citados têm lastro. As datas de efeitos indicadas conferem com as devolvidas."

**Igual à sua anotação** desse trace nos quatro critérios. Não é medida: é um trace só, e um trace fácil, porque a tabela de citações do dossiê já mostra o art. 14 como "não aparece no que foi devolvido". Mas confirma o formato e que o rascunhador usa as tabelas.

**Custo para os 70 traces revisados:** cerca de US$ 0,06.

## Pergunta de previsão

Na amostra cega, em quantos por cento dos vereditos o rascunhador vai discordar de você? E em qual critério ele vai errar mais?
