# Passo 37: gravar a anotação a partir do dossiê

Tarefa 22 do plano. Fecha o caminho da anotação: o dossiê (passo 32) mostra o trace e traz o formulário; este comando lê o formulário preenchido e grava a anotação com a `write_annotation` do passo 18. Sem ele, os vereditos seriam copiados à mão para o JSON.

**Quem escreveu:** entorno. O código e 27 testes foram escritos por um subagente Haiku 5.5 a partir do texto da tarefa; a sessão principal rodou o fluxo de ponta a ponta num trace real, corrigiu a separação das mensagens do validador e acrescentou 2 testes.

## O que mudou

- **[evals/annotate.py](../../evals/annotate.py):**
  - `parse_dossier_annotation(markdown, *, source)`: lê o bloco ` ```anotacao ` e devolve a anotação no formato do passo 18, **sem** `version` nem `date`. Não decide nada: um `"sim"` passa como escrito, e quem recusa é o validador.
  - Erros de **estrutura** saem todos juntos, com o arquivo e a linha (`traces/dossies/x.md:57: C2 em branco`): chave ausente, repetida ou desconhecida, linha sem `chave: valor`, veredito, `trace_id` ou `kind` em branco, bloco ausente, duplicado ou sem a cerca de fechamento. Uma chave desconhecida é ecoada sem número de documento.
  - `uncertain` aceita vazio, `C2`, `C2, C3` ou `[C2 C3]`; `note` é tudo o que vem depois de `note:` até o fim do bloco, em várias linhas.
  - `annotate(...)` acha o trace (em qualquer subpasta), o caso pelo `case_id` do trace e chama `write_annotation`.
  - `python -m evals.annotate DOSSIE.md --date AAAA-MM-DD [--annotations-dir annotations] [--traces-dir traces] [--cases-dir cases]`. A data é obrigatória: nunca vem do relógio.
- Os testes geram os dossiês com o próprio `build_dossier`: se o formulário mudar de um lado e não do outro, eles quebram.

## Como rodar

O fluxo de uma anotação:

```bash
uv run python -m evals.dossier <trace_id> > traces/dossies/<trace_id>.md
```

Preencha o bloco `anotacao` no fim do arquivo e grave:

```bash
uv run python -m evals.annotate traces/dossies/<trace_id>.md --date AAAA-MM-DD
```

Os testes:

```bash
uv run pytest tests/test_annotate.py -v
```

## O que observar

- **Vermelho antes:** os 27 testes do Haiku falharam com o stub (por `NotImplementedError`, não por asserção).
- **Suíte:** 29 testes em `tests/test_annotate.py`, **420** no total, verde duas vezes seguidas.
- **Ponta a ponta num trace real** (o `conf-sem_skill-9defaaed` da confirmação, em pasta temporária, com um caso escrito só para isso):
  1. o dossiê gerado pelo comando, preenchido com `C2: sim`, foi recusado com a mensagem do validador (`C2: veredito inválido 'sim' (use 'pass', 'fail' ou 'n/a')`) e nada foi gravado;
  2. trocado para `pass`, gravou `conf-sem_skill-9defaaed.v1.json` com a nota de duas linhas, `kind: blind` e a data passada.
- **Corrigido na revisão:** o comando separava os erros do validador em `"; "`, mas a mensagem de CPF do validador tem `"(CPF/CNPJ); remova"` dentro, e virava duas linhas. Agora só separa onde começa outro erro (`<trace_id>: ...`). Ganhou teste.
- **Teste de mutação:** 13 mutações (12 de estrutura e a da separação). Na primeira rodada, 1 sobreviveu: sem a conferência da cerca de fechamento, o bloco aberto quebraria com exceção em vez de erro claro. Ganhou teste. Agora as 13 caem.

## Pergunta de previsão

No M7, quantos dossiês o comando vai recusar na primeira tentativa? E quantas dessas recusas vão ser de estrutura (formulário) e quantas do validador (conteúdo)?
