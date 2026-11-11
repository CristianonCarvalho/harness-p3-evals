# Módulos do pacote `evals`

Quem depende de quem, e quem escreve o quê. As setas vão de **quem usa** para **quem é usado**.

```mermaid
flowchart TB
    subgraph nucleo["Núcleo: escrito por você"]
        annotation["annotation<br/>formato da anotação"]
        metrics["metrics<br/>TPR e TNR"]
        judge["judge<br/>o juiz LLM"]
    end

    subgraph entorno["Entorno: Haiku implementa, a sessão principal confere"]
        privacy["privacy<br/>detecta e gera CPF/CNPJ"]
        trace["trace<br/>formato do trace"]
        cases["cases<br/>caso, gabarito, divisão"]
        checks["checks<br/>C1, C2, C4 em código"]
        stats["stats<br/>intervalo de Wilson"]
        gabarito["gabarito<br/>confere contra o P2"]
        budget["budget<br/>teto de custo"]
        client["client<br/>cliente OpenRouter"]
        ledger["ledger<br/>custo por chamada"]
        report["report<br/>relatório e antes/depois"]
        adapter["adapters/claude_code<br/>stream-json para trace"]
        runner["runner<br/>roda claude -p"]
        consistency["consistency<br/>checagens do CI"]
        cli["cli<br/>comandos"]
    end

    cases --> privacy
    checks --> cases
    report --> stats
    report --> checks
    annotation --> privacy
    judge --> client
    judge --> ledger
    judge --> budget
    judge --> privacy
    adapter --> trace
    runner --> adapter
    runner --> trace
    runner --> budget
    runner --> privacy
    consistency --> privacy
    consistency --> cases
    consistency --> annotation
    consistency --> metrics
    consistency --> report
    cli --> consistency
    cli --> gabarito
    cli --> report

    classDef feito fill:#d4edda,stroke:#28a745,color:#000
    classDef falta fill:#fff3cd,stroke:#ffc107,color:#000
    classDef seu fill:#f8d7da,stroke:#dc3545,color:#000

    class privacy,trace,cases,checks,stats,gabarito,budget,client,ledger,report,adapter feito
    class runner,consistency,cli falta
    class annotation,metrics,judge seu
```

## Legenda

- **Verde:** pronto, com testes passando.
- **Vermelho:** núcleo, **a escrever por você**. O Claude revisa, explica e pergunta, mas não implementa.
- **Amarelo:** entorno ainda por fazer.

## Princípios de desenho

- **Cada módulo tem uma só responsabilidade** e pode ser entendido sem ler os outros.
- **`trace` e `cases` não dependem de ninguém** além de `privacy`: o formato dos dados é a base, e nada o contorna.
- **`cli` só faz argparse** e chama as funções; nenhuma regra de negócio mora nele.
- **O núcleo depende só de peças pequenas** (`privacy`, `client`, `ledger`, `budget`): você escreve a parte que ensina, sobre uma base já testada.
