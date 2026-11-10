# Visão geral: de uma pergunta a um relatório

O caminho completo de um caso, do início ao número final. Cada caixa é explicada no glossário do [`README.md`](../../README.md#conceitos-explicados).

```mermaid
flowchart LR
    caso["Caso<br/>pergunta + gabarito"] --> runner["Runner<br/>claude -p"]

    subgraph p2["Sistema avaliado (o P2)"]
        direction TB
        modelo["Modelo Claude"] <--> server["Server MCP<br/>buscar e obter dispositivo"]
        skill["Skill"] -.-> modelo
        hook["Hook<br/>bloqueia CPF/CNPJ"] -.-> server
    end

    runner --> p2
    p2 --> trace["Trace (JSON)<br/>pergunta, chamadas,<br/>saídas brutas, resposta"]

    trace --> checks["Checagens em código<br/>C1, C2, C4"]
    checks -->|"decide: pass ou fail"| veredito["Vereditos<br/>por critério"]
    checks -->|"needs_judge"| juiz["Juiz LLM<br/>outra família de modelo"]
    juiz --> veredito

    voce["Você anota<br/>os traces à mão"] --> anotacao["Anotações<br/>(verdade de referência)"]
    anotacao --> metricas["TPR e TNR<br/>do juiz"]
    juiz --> metricas

    veredito --> relatorio["Relatório<br/>taxa de aprovação + intervalo"]
    metricas --> relatorio
```

## Como ler

- **Linha cheia** é o fluxo dos dados. **Linha pontilhada** é uma peça que atua sobre outra: a skill orienta o modelo, e o hook vigia as chamadas ao server.
- O que está no quadro **"Sistema avaliado"** é o P2. O P3 não o altera: só o observa.
- O **código** decide primeiro. O juiz só entra no que o código não consegue decidir (`needs_judge`).
- O juiz **nunca vê a anotação humana**. A anotação serve só para medir o juiz (TPR e TNR) e dizer quanto confiar nele.
- O relatório junta duas coisas: **o que o sistema acerta** (taxas por critério) e **quanto o juiz merece confiança** (TPR e TNR).
