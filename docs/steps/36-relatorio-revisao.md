# Passo 36: o relatório da revisão

Tarefa 21 do plano (revisões R3, R5 e R8). O relatório de avaliação ganha uma seção, **"Revisão da anotação"**, que torna visível o próprio processo de anotação: quantas anotações de cada tipo, quanto o juiz concorda com as cegas, quanto o rascunhador acerta, se há sinal de ancoragem, quanto você concorda consigo mesmo e o que mudou nas correções.

**Quem escreveu:** entorno. O código e 18 testes foram escritos por um subagente Haiku 5.5 a partir do texto da tarefa; a sessão principal revisou, corrigiu o cálculo do juiz para traces que ele não julgou e acrescentou 2 testes.

## O que mudou

- **[evals/review_report.py](../../evals/review_report.py):**
  - `build_review(...)`, função pura, devolve:

    | Parte | O que mede | Sobre quais anotações |
    |---|---|---|
    | `counts` | cegas, revisadas, total; se o critério 2 (100 traces com o tipo declarado) está cumprido | última versão de cada trace |
    | `judge_blind` | TPR e TNR do juiz em C2, C3 e C4, com quantos traces ficaram sem veredito do juiz | última versão dos traces da amostra cega que continuam cegos |
    | `drafter_accuracy` | acerto do rascunhador da anotação, por critério | rascunho tardio contra a **primeira** versão da anotação cega |
    | `anchoring` | quanto você mudou o rascunho nos traces revisados, ao lado do erro do rascunhador; **"possível ancoragem"** quando muda menos que a metade do que ele erra | última versão dos traces revisados com rascunho |
    | `self_agreement` | concordância consigo mesmo, por critério | primeira versão contra a reanotação |
    | `corrections` | quantos traces cegos foram corrigidos; TPR e TNR com as primeiras e com as últimas versões | histórico dos traces cegos |
    | `gabaritos` | quantos gabaritos rascunhados você mudou; quantos casos estão `disputed` | rascunho mais recente contra o gabarito do caso |

    Sem juiz ainda, as partes que dependem dele saem vazias, com o motivo.
  - `render_review_markdown(review)` e `collect_review_inputs(...)`, que lê tudo do disco.
- **[evals/report.py](../../evals/report.py):** `render_markdown` acrescenta a seção quando o relatório traz `review`.

**Decisão do entorno: a reanotação de consistência fica em `annotations/consistency/`.** O formato da Tarefa 5 não tem campo de "propósito"; se a reanotação fosse uma nova versão em `annotations/`, o relatório a confundiria com uma correção da anotação cega. Na pasta separada, a primeira versão em `annotations/` é a anotação original, as seguintes são correções, e a reanotação fica à parte. O comando de gravar já aceita `--annotations-dir annotations/consistency`.

## Como rodar

```bash
uv run pytest tests/test_review_report.py -v
```

## O que observar

- **Vermelho antes:** 17 dos 18 testes do Haiku falharam com o stub (o de constantes passava); o teste do juiz parcial falhou antes da correção.
- **Suíte:** 20 testes em `tests/test_review_report.py`, **513** no total, verde duas vezes seguidas.
- **Corrigido na revisão:** pela spec (D3), o juiz só decide o que o código deixou para ele, então muitos traces não terão veredito do juiz em C2 ou C4. A função de métricas da Tarefa 6 recusa trace sem veredito do juiz com erro, e o relatório quebraria na primeira rodada real. Agora, por critério, entram só os traces que o juiz julgou, e a tabela mostra quantos ficaram de fora (coluna "sem veredito do juiz").
- **Teste de mutação:** 11 mutações nas regras da seção. Na primeira rodada, 2 sobreviveram:
  - `<=` em vez de `<` na regra da ancoragem: mudar **exatamente** a metade do erro não é "menos que a metade". Ganhou teste da fronteira;
  - aceitar erro do rascunhador igual a zero: equivalente, porque nenhuma taxa de mudança é menor que zero.

  Agora 10 de 11 caem; a que sobra é a equivalente.

## Pergunta de previsão

O relatório vai marcar "possível ancoragem" em algum critério? Em qual?
