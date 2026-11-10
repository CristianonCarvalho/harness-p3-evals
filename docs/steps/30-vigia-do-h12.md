# Passo 30: o marcador vigia o H12

Passo fora do plano (que reserva os números até 29). Vem da conversa de desenho da Tarefa 5, decisão 6 em D2.

## O que mudou

`validate_case` ([evals/cases.py](../../evals/cases.py)) agora recusa um caso cuja pergunta tem `{CPF}` ou `{CNPJ}` e cuja hipótese não inclui H12. A mensagem diz o marcador e o porquê:

```
a pergunta tem {CPF} mas a hipotese nao inclui H12 (sem H12, o C4 nao se aplica e o vazamento nao e medido)
```

**Por quê:** pela decisão 5, o C4 se aplica quando o caso tem H12 ou H13. Se você planta um CPF na pergunta e esquece o H12, o C4 vira `n/a` em silêncio, e um vazamento de CPF nunca seria medido. A vigia transforma esse esquecimento em erro de validação.

**Só de ida:** um caso H12 sem marcador continua aceito. H13 não substitui H12: um caso com `{CPF}` e só H13 é recusado.

O teste antigo `test_question_with_taxpayer_number_is_rejected_but_placeholder_is_ok` passou a marcar H12 no caso com `{CPF}`, porque sem isso ele agora seria recusado, de propósito.

## Como rodar

```bash
uv run pytest tests/test_cases.py -v
```

## O que observar

- **Vermelho antes:** dos cinco testes novos, os dois de recusa falharam antes da implementação; os três de aceitação já passavam, como deviam.
- **Suíte:** 110 testes, verde duas vezes seguidas.
- **Teste de mutação:** 11 mutações, 9 caem. As 2 que sobrevivem são equivalentes: a mensagem cita H12 duas vezes (tirar uma não muda nada que se confira), e remover só `{CPF}` da pergunta antes da detecção de documento não muda o resultado, porque o marcador que sobra não tem dígitos.
- **Limite que continua:** o H13 não tem marcador na pergunta. Esquecer o H13 ainda desliga o C4 em silêncio.

## Pergunta de previsão

Quando você escrever os 100 casos, quantos vão ser recusados por essa vigia na primeira validação? Escreva o número antes e compare.
