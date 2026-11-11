# Ordem das tarefas e andamento

As 21 tarefas do [plano de implementação](../superpowers/plans/2026-11-10-p3-evals.md), com as dependências entre elas e o que já foi feito. As tarefas 17 a 21 nasceram da [revisão do rascunho por IA](../superpowers/specs/2026-11-11-p3-rascunho-por-ia-design.md) (2026-11-11).

```mermaid
flowchart LR
    t1["1. Esqueleto"] --> t2["2. Privacidade"]
    t2 --> t3["3. Trace"]
    t2 --> t4["4. Casos e divisão"]
    t4 --> t8["8. Checagens C1, C2, C4"]
    t7["7. Intervalo de Wilson"] --> t14["14. Relatório"]
    t8 --> t14
    t4 --> t9["9. Gabarito vs P2"]
    t1 --> t10["10. Custo + cliente P1"]

    t2 --> t5["5. Anotação<br/>NÚCLEO"]
    t1 --> t6["6. TPR e TNR<br/>NÚCLEO"]
    t3 --> t11["11. Juiz<br/>NÚCLEO"]
    t10 --> t11
    t5 --> t11

    t3 --> t12["12. Adaptador<br/>Claude Code"]
    t12 --> t13["13. Runner"]
    t10 --> t13

    t5 --> t15["15. CI e check-repo"]
    t6 --> t15
    t14 --> t15
    t15 --> t16["16. README final"]

    t8 --> t17["17. Dossiê"]
    t4 --> t17
    t9 --> t18["18. Rascunhador<br/>do gabarito"]
    t10 --> t18
    t4 --> t19["19. Amostra cega"]
    t5 --> t20["20. Rascunhador<br/>da anotação"]
    t17 --> t20
    t19 --> t20
    t6 --> t21["21. Relatório<br/>da revisão"]
    t14 --> t21
    t20 --> t21
    t21 --> t15

    classDef feito fill:#d4edda,stroke:#28a745,color:#000
    classDef falta fill:#fff3cd,stroke:#ffc107,color:#000
    classDef seu fill:#f8d7da,stroke:#dc3545,color:#000

    class t1,t2,t3,t4,t7,t8,t9,t10,t12,t13,t14 feito
    class t15,t16,t17,t18,t19,t20,t21 falta
    class t5,t6,t11 seu
```

## Legenda

- **Verde:** feito, com commit e tag `step-NN`.
- **Vermelho:** núcleo, a escrever por você.
- **Amarelo:** entorno ainda por fazer.

## Onde estão os bloqueios

| Tarefa | Espera por |
|---|---|
| 11 (juiz) | 5 (anotação), porque o juiz e a anotação precisam falar o mesmo formato de veredito |
| 15 (CI) | 5 e 6, porque o CI valida anotações e recalcula TPR/TNR; e 21, porque confere rascunhos e anotações cegas |
| 18 (rascunhador do gabarito) | escolher o modelo do rascunhador e o do juiz (famílias diferentes) |
| 20 (rascunhador da anotação) | 5 (o validador), 17 e 19; e a confirmação de que fica no entorno (R7) |
| 21 (relatório da revisão) | 6 e 20 |

## Fora do plano

- **Passo 30:** `validate_case` recusa `{CPF}`/`{CNPJ}` na pergunta sem H12 (decisão 6 da Tarefa 5).
- **Passo 31:** `check_c2` aprova sozinho o caso sem resposta quando o modelo não diz data (decisão 7).
- **Desenho da Tarefa 5 fechado** (decisões 1 a 14 em D2, contrato reescrito no plano em 2026-11-11); o nó 5 segue vermelho porque o código é seu.

## Depois das tarefas: os marcos

O código sozinho não entrega o critério de concluído. O que entrega são os marcos que dependem de você: **escrever as 100 perguntas e confirmar os gabaritos rascunhados**, **a rodada piloto**, **anotar os traces**, **calibrar o juiz** e **o primeiro antes/depois**. Estão no fim do plano.
