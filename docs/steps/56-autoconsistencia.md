# Passo 56: a medida de autoconsistência (Marco M7c)

Marco M7c do plano. A reanotação mede o quanto você concorda consigo mesmo: 10 traces sorteados da amostra cega inicial foram reanotados às cegas, sem abrir a primeira anotação nem olhar o juiz.

O resultado estabelece o teto empírico da avaliação: se o ser humano concordasse consigo em apenas 70%, um juiz automático com TPR de 76% estaria no limite do instrumento. Com a taxa real medida, sabe-se se eventuais divergências são do juiz ou da régua.

## O que mudou

- **Amostra de consistência sorteada** entre os 30 traces cegos iniciais (`seed: 20261116`), registrada em `annotations/_samples.json`:
  `c001-bf331068`, `c026-35d1d57d`, `c037-3949b772`, `c045-158020e0`, `c057-8b19d225`, `c064-d1fd467b`, `c070-b292e410`, `c088-b6933b29`, `c091-02c45939`, `c100-7551baff`.
- **Dossiês cegos** gerados em `traces/dossies/consistencia/` (fora do git), sem mostrar vereditos anteriores.
- **10 anotações gravadas** em `annotations/consistency/<trace_id>.v1.json`, preservando intactas as anotações primárias de benchmark em `annotations/*.v1.json`.
- **Relatório atualizado:** [reports/2026-11-15-haiku-skill-id-20261114.md](../../reports/2026-11-15-haiku-skill-id-20261114.md) com a seção de autoconsistência preenchida.

## Como rodar

```bash
# Rodar todos os testes automatizados
python3 -m pytest

# Verificar a consistência completa do repositório e dos relatórios
python3 -m evals.cli check-repo
```

## O que observar

**Tabela de autoconsistência (10 traces reanotados):**

| Critério | Concordância | Total avaliado | n/a mútuo | Taxa |
|---|---|---|---|---|
| **C1 (Citação)** | 10 | 10 | 0 | **100,0%** |
| **C2 (Data)** | 10 | 10 | 0 | **100,0%** |
| **C3 (Não sei)** | 10 | 10 | 0 | **100,0%** |
| **C4 (Segurança)** | 2 | 2 | 8 | **100,0%** |

- **Concordância perfeita (100%):** nenhum veredito mudou entre a primeira anotação cega e a reanotação.
- **Estabilidade da régua:** o resultado demonstra que os critérios (exigência de todos os dispositivos esperados em C1, descarte de menções genéricas ou faixas, confronto de C3 com o gabarito) são claros e determinísticos na aplicação humana.
- **Validação do juiz:** indica que o TPR de 76,0% do juiz no C1 e o TPR de 90,7% no C3 refletem sobretudo a acurácia do juiz, e não ruído da anotação humana. Ressalvas: 10 em 10 tem intervalo de 95% de 72% a 100%, e a reanotação veio 2 dias depois da primeira, então parte da concordância pode ser memória.

**Situação dos critérios de conclusão do projeto:**
- **Critério 1 (relatório numérico):** atendido.
- **Critério 2 (100 traces anotados):** atendido com folga (124 traces: 54 cegos + 70 revisados).
- **Critério 3 (juiz calibrado):** atendido em C1 e C3 (C2 e C4 como limites conhecidos).
- **Critério 4 (antes/depois):** demonstrado no Passo 50.
- **Critério 5 (regressão em CI):** verde e ativo.

## Pergunta de previsão

No P4 (onde a suíte do P3 atuará como gate em CI para PRs abertos por agentes), qual dos quatro critérios (C1, C2, C3 ou C4) tem maior probabilidade de reprovar um PR com mudanças na prompt ou na skill?
