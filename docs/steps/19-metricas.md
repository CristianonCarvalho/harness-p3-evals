# Passo 19: métricas TPR, TNR e concordância consigo mesmo

## O que mudou

Implementação das métricas de calibração do juiz e concordância do anotador em `evals/metrics.py` e sua suíte de testes em `tests/test_metrics.py` (Tarefa 6 do roadmap, Passo 19):

- **Dataclasses imutáveis:**
  - `ConfusionMatrix`: armazena `tp`, `fn`, `fp`, `tn`, `tpr`, `tnr`, `n_pos`, `n_neg`, `n_na` e `n_disputed`.
  - `Agreement`: armazena `agree`, `total`, `n_na` e `rate` para cada critério avaliado.
- **`confusion(human, judge, criterion, *, disputed=frozenset()) -> ConfusionMatrix`:**
  - Pareamento por `trace_id` com o veredito humano como referência (classe positiva = aprovado/`pass`).
  - Ordem estrita de processamento:
    1. *Só cegas:* exige `kind == "blind"` para todas as anotações humanas (R3), levantando erro explícito ordenado caso receba anotação revisada ou com kind ausente.
    2. *Sem duplicatas:* detecta e recusa `trace_id` repetido na lista humana (prevenindo contaminação por histórico de versões).
    3. *Casos disputados:* traces em `disputed` são excluídos da calibração e contabilizados em `n_disputed` (D6/R3).
    4. *Formato e integridade do juiz:* confere apenas os traces ativos (não-disputados); exige dict `{critério: veredito}` e aponta erros explícitos ordenados para formato inválido ou ausência de veredito do critério. Traces disputados não exigem julgamento do juiz. Traces extras no juiz são ignorados com segurança.
    5. *Validação de vereditos:* aceita estritamente `("pass", "fail", "n/a")` usando tupla sequencial (protegendo contra `TypeError` em tipos não-hasháveis como listas vindas do modelo); vereditos inválidos geram `ValueError` detalhado e ordenado por `trace_id`.
    6. *Exclusão de `n/a`:* se qualquer um dos lados (humano ou juiz) marcar `n/a`, o par é excluído do cálculo e somado em `n_na`.
    7. *Divisão por zero segura:* se `n_pos == 0`, `tpr is None`; se `n_neg == 0`, `tnr is None`.
- **`self_agreement(first, second) -> dict[str, Agreement]` (R8):**
  - Mede a concordância do anotador consigo mesmo em duas rodadas cegas (reavaliação após intervalo).
  - Exige correspondência exata dos conjuntos de `trace_id` entre as duas listas (erro explícito caso um lado traga traces ausentes no outro).
  - Avalia os quatro critérios (`C1`, `C2`, `C3`, `C4`) de forma independente.
  - Veredito `n/a` idêntico nos dois lados soma em `n_na` e não infla a taxa de concordância.
  - Veredito `n/a` unilateral no mesmo trace gera erro explícito (indica anotações de casos incompatíveis ou com defeito de validação).

## Como rodar

```bash
uv run pytest tests/test_metrics.py -v
```

## O que observar

- **Suíte:** 31 testes em `tests/test_metrics.py`, 288 no total do projeto, passando duas vezes consecutivas.
- **TDD e sensibilidade a mutações (dentes comprovados):**
  - *TPR/TNR indefinidos:* `assert m.tnr is None` impediu que `0.0` passasse despercebido.
  - *Ordenação das mensagens:* listas invertidas no teste provaram que `sorted()` é mandatório.
  - *Juiz antes de disputed:* inverter a ordem fez o teste `8d` falhar, provando que casos disputados não exigem juiz.
  - *Validação de tipo do juiz:* uso de tupla em vez de `frozenset` evitou `TypeError` em listas arbitrárias no JSON.
  - *Concordância por critério:* mutação para "anotação inteira" quebrou `C1`, provando independência dos critérios.
  - *Exclusão de n/a duplo:* mutação contando `n/a` com `n/a` quebrou o teste de `C4`, provando que o acordo não é inflado artificialmente.
  - *Simetria:* comprovada invertendo `self_agreement(second, first) == self_agreement(first, second)`.

## Respostas às perguntas do plano

### 1. Por que o TNR de 0,5 com 2 reprovados é pouco informativo? Quantos reprovados o seu teste precisa ter?
Com apenas 2 casos negativos ($N_{neg} = 2$), acertar 1 resulta em $TNR = 0.5$, mas um único erro altera a métrica para $0.0$ ou $1.0$. O intervalo de confiança de Wilson (95%) para $1/2$ vai de aproximadamente $0.09$ a $0.91$, cobrindo quase toda a reta real e tornando a medição indistinguível de ruído aleatório. Conforme a decisão D6 da spec, são necessários **de 10 a 15 reprovados** para que o TNR tenha estabilidade mínima e poder de calibração.

### 2. Onde mora a regra "mínimo de 10 reprovados": aqui, ou no relatório (Tarefa 14)?
Mora no **relatório (Tarefa 14)**. O módulo `evals/metrics.py` é responsável pela aritmética e contabilidade rigorosa dos vereditos, calculando as taxas e expondo `n_neg` e `n_pos`. O relatório é quem detém a visão global do processo e a regra de negócio para diagnosticar e estampar "não calibrado" ou alertas de amostra insuficiente, sem travar medições intermediárias ou testes sintéticos com $N$ reduzido.

### 3. Se a sua concordância consigo mesmo no C3 for 8 de 10, que TNR faz sentido exigir do juiz no C3?
O teto de desempenho do juiz não pode superar a consistência do próprio padrão de referência humano (*human upper bound*). Se o anotador humano hesita ou discorda de si mesmo em 20% dos casos de C3 ("dizer não sei quando devia"), há uma margem de subjetividade/ruído inerente à tarefa. Exigir mais de $80\%$ de TNR do juiz significaria exigir que o modelo adivinhe o ruído humano. Logo, o TNR exigível do juiz deve ser balizado em **cerca de 80% (ou ligeiramente abaixo)**.

---

## Pergunta de previsão

Qual será o TPR e qual será o TNR do primeiro juiz?

*Previsão:*
- **TPR:** em torno de **0.85 a 0.90**. Modelos de linguagem tendem a ser lenientes (*sycophancy* e viés afirmativo), concordando facilmente com respostas que parecem plausíveis e completas.
- **TNR:** em torno de **0.55 a 0.65**. Detectar falhas sutis (como citação sem lastro no texto da norma ou data inventada que parece razoável) é muito mais difícil para o juiz inicial sem calibração específica de prompt e few-shot examples.
