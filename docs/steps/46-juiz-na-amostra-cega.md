# Passo 46: o primeiro juiz contra a anotação cega

Marco M8, primeira tentativa. Por sua decisão, um candidato só (o mais barato, `openai/gpt-6.1-terra`) e a escolha feita na própria amostra cega. Por isso, a medida abaixo tende a sair otimista; aqui ela saiu ruim, então o viés não muda a conclusão.

## O que mudou

- **30 julgamentos** em `judgments/<trace_id>.json`: 64 chamadas (C1 em 27 traces, C2 em 7 e C3 em 30), **US$ 0,3724**. Ledger em `runs/judge-terra-20261114.jsonl`, fora do git. O `check-repo` aceita os 30.
- **Nenhuma mudança de código.** O `config/run.json` não recebeu o juiz: ele não passou.

## O que observar

O "positivo" é `pass`: o TPR é a concordância nos traces que você aprovou, e o TNR, nos que você reprovou.

| Critério | Traces | TPR | TNR | Onde discordam |
|---|---|---|---|---|
| C1 | 27 | **0,06** (1 de 18) | 1,00 (9 de 9) | o juiz reprovou 17 que você aprovou |
| C2 | 7 | 1,00 (6 de 6) | 1,00 (1 de 1) | nenhum; amostra pequena demais para dizer muito |
| C3 | 30 | 0,88 (21 de 24) | **0,00** (0 de 6) | o juiz aprovou os 6 que você reprovou |

### C1: o juiz vê citações que o dossiê não mostrou

Nos 17, o juiz reprova por citações **em faixa** ("arts. 419 a 423 da LC 214/2025", "arts. 125 a 142") que as ferramentas não devolveram. O leitor de citações do dossiê (passo 32) **não reconhece faixas**: em `c001` e `c003`, a tabela de citações não tem nenhuma linha para elas. Você julgou pelo dossiê, então não viu essas citações.

A discordância é de régua, não só de juiz. A pergunta é sua: uma faixa de artigos citada de memória, sem lastro, reprova o C1?
- Se **sim**, o juiz está certo, e o dossiê precisa mostrar as faixas (entorno). As anotações desses traces seriam revistas (versão 2), com o dossiê corrigido.
- Se **não**, o `C1.md` precisa dizer que menção a faixa não é citação.

### C3: o juiz não sabe se o corpus responde

Nos 6, a sua nota é a mesma: "disse que o corpus não traz a resposta quando constava no corpus". O juiz aprova porque **as ferramentas não devolveram** o dispositivo, e o modelo admitiu isso. O juiz do C3 não recebe o gabarito (`answer_exists`); vê só o que foi devolvido. Para ele, "não encontrei" sempre parece honesto quando a busca falhou.

O C3 mede postura contra o **corpus**, não contra a busca. Sem o `answer_exists`, o juiz não tem como acertar esses casos. A mudança fica no `build_messages` (núcleo): passar ao C3 se o corpus responde (`sim`, `parcial`, `não`), sem a lista de dispositivos.

## Pergunta de previsão

Com o `answer_exists` no C3, quantos dos 6 reprovados o juiz vai pegar?
