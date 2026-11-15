# Passo 50: o primeiro antes e depois (skill pedindo o id)

Marco M10. A troca: uma linha na skill do P2 (tag `step-17`, commit `1a02e55` no P2) pede que toda citação leve o `id` do dispositivo entre crases. O resto não mudou: o mesmo Haiku, os mesmos 120 casos, a mesma semente e o mesmo juiz congelado.

## O que mudou

- **P2:** a seção "Formato da resposta" da skill (`consultar-reforma-tributaria/SKILL.md`). Commit e tag locais no P2, sem push.
- **Rodada `haiku-skill-id-20261114`:** 120 traces `ok`, US$ 0,67. **Juiz:** US$ 1,06. Julgamentos novos em `judgments/`.
- **`config/run.json`:** `p2_tag` passou a `step-17`.
- **[reports/2026-11-14-haiku-skill-id-20261114.md](../../reports/2026-11-14-haiku-skill-id-20261114.md)**, sem pendentes; `check-repo` sem problemas.

## O que observar

**Comparação no teste** (`report.compare`):

| Condição | Critério | Antes (`step-16`) | Depois (`step-17`) | Marca |
|---|---|---|---|---|
| com skill | C1 | 52,9% | 44,1% | dentro do ruído |
| com skill | C2 | 95,6% | 95,6% | dentro do ruído |
| com skill | C3 | 75,0% | 70,6% | dentro do ruído |
| com skill | C4 | 100% | 100% | dentro do ruído |
| sem skill | C1 | 28,6% | 0,0% | dentro do ruído |
| sem skill | C2 | 78,6% | 71,4% | dentro do ruído |
| sem skill | C3 | 57,1% | 64,3% | dentro do ruído |

**Nenhuma diferença real.** A skill nova não melhorou a citação; o número até caiu, dentro do ruído.

**O que a troca mudou de fato: quem decide o C1.** Com o id na resposta, o código passou a decidir o C1 em vez do juiz:

| C1, com skill | código | juiz |
|---|---|---|
| antes | 7 | 61 |
| depois | **60** | 8 |

E o código reprova quase só por um motivo: dos 47 `fail` do código nos 100 traces com skill, **44 são "esperado ausente"** (não citou todos os dispositivos do gabarito) e só 3 são "sem lastro". O modelo cita o que a ferramenta devolveu; o que falta é citar **todos** os esperados. A regra "todos" (passo 42) é o que mais pesa no C1.

**Dois cuidados na leitura:**
- **O instrumento mudou junto.** Antes o C1 era medido quase todo pelo juiz (TPR 0,78 contra você); depois, pelo código. Parte da queda pode ser só a diferença entre as duas réguas, não uma piora do modelo.
- **O ruído é grande.** Na condição **sem skill**, a mudança da skill não tem efeito nenhum (a skill nem está lá), e mesmo assim o C1 foi de 4 em 14 para 0 em 14. Isso é o tamanho da variação entre duas rodadas iguais com 14 casos.

**Critério de concluído 1 e 4:** a troca gerou um relatório numérico e um antes/depois com marca de ruído. A resposta foi "não dá para afirmar diferença", o que é um resultado.

## Pergunta de previsão

Se a regra do C1 passasse a "pelo menos um esperado", quanto subiria a taxa do C1 com a skill nova?
