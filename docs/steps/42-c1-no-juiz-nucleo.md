# Passo 42: o juiz julga o C1 em prosa (núcleo)

Completa o passo 41. Escrito pelo usuário (núcleo); o Claude revisou.

## O que mudou

- **[evals/judge.py](../../evals/judge.py):**
  - `JUDGE_CRITERIA` com `C1`;
  - `criteria_for_trace` chama `check_c1` e pede o C1 ao juiz só quando o código devolve `needs_judge`, ou seja, citação só em prosa;
  - `build_messages` mostra `## Dispositivos Esperados` só no C1, lendo do topo do caso ou do `gabarito`; com a lista vazia, mostra uma frase fixa.
- **[config/judge_prompts/C1.md](../../config/judge_prompts/C1.md):** lastro, esperado e ambiguidade. **Regra do esperado: todos.** É a mesma regra do código, que reprova se faltar um. Assim o C1 não muda de régua conforme a resposta traga id ou prosa. O prompt ensina a ler os ids, como `LC214.art422.par1.incI`.
- **8 testes** novos em `tests/test_judge.py`.

## Como rodar

```bash
uv run pytest -q
```

```bash
uv run python -m evals.cli hash-prompts
```

## O que observar

- **Suíte:** 609 testes, verde duas vezes; `check-repo` sem problemas.
- **Teste de mutação:** 7 mutações, 6 caem. A que sobrevive (ignorar o gabarito aninhado em `criteria_for_trace`) é equivalente: o `check_c1` devolve `needs_judge` antes de olhar o esperado.
- **Hash dos prompts do juiz:** `3146df45d9fa…`. Vai para o `config/run.json` quando o modelo do juiz for escolhido.
- **Risco da regra "todos":** o gabarito lista o artigo e os filhos. Se, na anotação, você aprovar respostas que só não citaram um inciso, o problema está na lista do gabarito, não no juiz.

## Pergunta de previsão

Dos 17 traces da piloto com C1 em prosa, quantos o juiz vai reprovar com a regra "todos"?
