# Passo 38: a data de referência do caso só em AAAA-MM-DD

Passo fora do plano. Vem da revisão da Tarefa 5 (2026-11-11): ao escrever a validação da data da anotação, apareceu que `date.fromisoformat` aceita mais formas do que o projeto usa, e `validate_case` (passo 17) tinha o mesmo furo.

**Quem escreveu:** entorno. A correção e o teste foram escritos por um subagente Haiku 5.5; a sessão principal revisou.

## O que mudou

- **[evals/cases.py](../../evals/cases.py):** `gabarito.reference_date` precisa ser texto no formato exato `AAAA-MM-DD` (expressão regular) **e** uma data que existe (`date.fromisoformat`). A mensagem de erro é a mesma de antes. Um valor que não é texto vira erro, em vez de derrubar a validação com exceção.
- **[tests/test_cases.py](../../tests/test_cases.py):** 8 testes novos.

**Por que importa:** a data de referência vai na pergunta que o modelo recebe ("Data de referência: AAAA-MM-DD", passo 26) e é comparada, letra por letra, com a data do rascunho do gabarito (passo 33). Um caso com `"20261111"` passaria na validação e faria o rascunhador recusar todo rascunho por "data diferente".

## Como rodar

```bash
uv run pytest tests/test_cases.py -v
```

## O que observar

- **Vermelho antes:** 2 dos 8 testes falharam: `"20261111"` era aceito, e o número `20261111` (não texto) derrubava a validação com `TypeError`.
- **Correção de uma afirmação minha:** eu tinha listado `"2026-1-1"` (sem zeros) entre as formas que o `fromisoformat` aceita. Não aceita: o teste desse valor já passava antes. Ficou como proteção.
- **Suíte:** **566** testes, verde duas vezes seguidas; `check-repo` sem problemas.
- **Outros lugares:** o único outro uso de `fromisoformat` no código é o de `evals/annotation.py` (Tarefa 5), que já confere o formato antes.

## Pergunta de previsão

Quando você escrever as perguntas, em quantas a data de referência vai ser recusada na primeira validação?
