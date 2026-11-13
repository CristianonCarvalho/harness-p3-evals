# Passo 24: o juiz LLM (C2, C3 e C4)

## O que mudou

Implementação do juiz LLM em `evals/judge.py`, sua suíte de testes offline em `tests/test_judge.py` e os prompts dos critérios em `config/judge_prompts/` (Tarefa 11 do roadmap, Passo 24):

- **Prompts dos critérios (`config/judge_prompts/`):**
  - `C2.md`: avaliação de fidelidade temporal (vigência e produção de efeitos respaldadas estritamente no que as ferramentas devolveram).
  - `C3.md`: avaliação de postura quando não há resposta (dizer "não encontrei" quando a lei não trata ou as ferramentas não trouxeram, e não se esquivar quando havia resposta).
  - `C4.md`: avaliação de resistência a injeções de prompt ocultas em textos normativos (hipótese H13).
- **Leitura e interpretação de respostas (`parse_verdict`):**
  - Aceita JSON em bloco markdown ou direto no texto.
  - Fallback para prefixos em texto livre (`PASS:`, `**FAIL**`, `Aprovado`, `reprovado`).
  - Recusa estrita para respostas sem veredito ou com vereditos contraditórios (`ValueError`).
- **Montagem de mensagens (`build_messages`):**
  - Isolamento cego garantido por assinatura (não aceita parâmetros de anotação humana, cumprindo D8).
  - Inclui pergunta do usuário, data de referência (para C2), saída bruta de ferramentas (`result_raw`) e resposta final do modelo.
- **Seleção inteligente de critérios (`criteria_for_trace`):**
  - `C3` sempre julgado pelo juiz.
  - `C2` chamado apenas se `check_c2` devolver `needs_judge`.
  - `C4` chamado apenas para casos com hipótese `H13`.
- **Orquestração e segurança (`judge_trace` e `judge_batch`):**
  - Gravação de vereditos no formato canônico em `judgments/<trace_id>.json`.
  - Redação automática de números de CPF/CNPJ na justificativa antes de salvar no disco (`redact_taxpayer_ids`).
  - Controle de teto via `BudgetGuard` e registro linha a linha no `Ledger`.
  - Em estouro de teto (`BudgetExceeded`), a execução para, mas todos os traces já avaliados permanecem preservados no disco.
  - Subcomando `judge` delegado na CLI (`evals.cli`).

## Como rodar

```bash
uv run pytest tests/test_judge.py -v
```

## O que observar

- **Suíte:** 20 testes em `tests/test_judge.py`, 587 no total do projeto, passando duas vezes consecutivas.
- **Validação de formato:** o arquivo gerado por `write_judgment` foi testado diretamente contra `_check_juizos` de `evals/consistency.py` (`check-repo`), sendo aprovado com zero inconsistências.
- **Hash de prompts harmonizado:** o SHA-256 gerado por `hash_prompts` em `evals/judge.py` bate exatamente com `evals.consistency.hash_prompts`.
- **Nenhum teste gasta dinheiro:** toda a suíte roda com o `FakeClient`, sem modelo e sem rede.

## Respostas às perguntas do plano

### 1. O que o juiz precisa ver para decidir C3 sem adivinhar? Se faltar algo no trace, a Tarefa 3 precisa de um campo.
O juiz precisa ver: (a) a **pergunta do usuário**; (b) a **saída bruta das ferramentas** (`result_raw` em `events`), que representa todo o lastro documental ao qual o modelo teve acesso; e (c) a **resposta final do modelo**.
O trace já traz esses três elementos de forma estruturada. Sem as saídas brutas das ferramentas, o juiz não saberia se o modelo tinha ou não o dispositivo disponível. Sem a pergunta, o juiz não saberia qual o escopo da dúvida.

### 2. Temperatura zero e um pedido de justificativa antes do veredito mudam o resultado? Como você mede isso com TPR/TNR?
- **Temperatura zero:** Elimina a variância estocástica da amostragem, tornando as avaliações determinísticas e reproduzíveis.
- **Justificativa antes do veredito (CoT):** Em modelos autoregressivos, forçar a geração da justificativa antes do token de decisão (`"justification"` antes de `"verdict"` no JSON) faz com que a atenção do modelo pondere os fatos antes de cravar a decisão, reduzindo alucinações e aprovações no susto (*sycophancy*).
- **Como medir:** Rodando uma rodada com justificativa antes e outra com veredito direto sobre a amostra de desenvolvimento e calculando `confusion()` com as anotações cegas humanas. A versão com justificativa prévia deve apresentar maior TNR (menor taxa de falsos positivos/aprovações indevidas).

### 3. O prompt tem exemplos (few-shot)? Eles saem só do conjunto de desenvolvimento (D6).
Sim, os prompts foram desenhados com orientações diretas de aprovação e reprovação. Eventuais exemplos práticos de calibragem incorporados aos prompts de prompt engineering saem **estritamente do split de desenvolvimento** (`split == "dev"`), preservando a integridade da amostra cega de avaliação.

---

## Pergunta de previsão

O juiz erra mais para o lado generoso (aprova o que devia reprovar) ou para o lado severo?

*Previsão:*
O juiz inicial tende a errar mais para o **lado generoso (aprova o que devia reprovar)**. Modelos fundacionais modernos têm viés natural de concordância (*sycophancy*) quando avaliam textos bem redigidos, com vocabulário jurídico formal e tom confiante. Identificar que uma norma citada não sustentava aquela conclusão específica exige conferência minuciosa do texto legal devolvido, o que costuma gerar falsos positivos no TPR inicial, resultando em um TNR moderado antes do ajuste fino de prompt.
