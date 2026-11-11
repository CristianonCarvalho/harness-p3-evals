# Spec: gabarito e anotação rascunhados por IA, com amostra cega

**Status: aprovada pelo usuário em 2026-11-11.** As mudanças da seção "O que muda na spec principal" já foram aplicadas em `2026-11-10-p3-evals-design.md` (notas **Revisão R**), no README e em `docs/roadmap/p3-no-roadmap.md`.

## O problema

A spec principal supõe que o usuário entende da reforma tributária: ele escreve o gabarito de cada caso (D13) e anota os 100 traces (D2). O usuário disse que **não conhece a legislação** e não consegue fazer nenhum dos dois sozinho.

Entregar tudo a uma IA quebra o critério 3 ("juiz calibrado contra a anotação humana"). Com uma IA como referência, o TPR e o TNR medem quanto duas IAs concordam: quando as duas erram do mesmo jeito, o número sobe e o erro some.

## O que foi decidido na conversa

| # | Pergunta | Resposta do usuário |
|---|---|---|
| 1 | Como anotar sem conhecer a legislação? | A IA rascunha, o usuário confirma |
| 2 | Vale também para o gabarito? | Sim: a IA rascunha a partir do corpus, a conferência sem modelo filtra, o usuário confirma |
| 3 | Uma amostra anotada às cegas calibra o juiz? | Sim, cerca de 30 traces |
| 4 | Qual IA rascunha? | Não respondeu; pediu o desenho completo para avaliar. Abaixo vai a recomendação (R4) |

## A ideia central

A anotação **não julga se a resposta está certa segundo o direito tributário**. Ela julga se a resposta é **fiel ao texto que o P2 devolveu e ao gabarito**. Com o gabarito pronto, quase todo veredito vira comparação. Por exemplo: o caso diz que a resposta não existe no corpus, e o modelo disse "não encontrei" ou inventou? A data da resposta é a do gabarito?

O conhecimento jurídico fica concentrado no **gabarito**. Lá ele tem duas proteções: o texto do corpus, que o usuário lê ao lado, e a conferência sem modelo, que já existe em D13.

O preço dessa escolha é declarado no README: **a verdade de referência do P3 é a fidelidade ao corpus, não a correção jurídica.** Um corpus incompleto ou um gabarito juridicamente ingênuo passam sem ser vistos.

## Decisões

### R1. As perguntas são do usuário

O usuário escreve as perguntas. A IA não escreve perguntas. As sementes de `docs/p2/casos-candidatos.md` só entram reescritas ou aprovadas por ele, como já dizia aquele arquivo.

Por quê: o roadmap pede **perguntas criadas por pessoas**, e as perguntas de um leigo são justamente as perguntas reais que o P2 vai receber. A falta de conhecimento jurídico atrapalha o gabarito, não a pergunta.

### R2. O gabarito: rascunho por IA a partir do corpus, antes de qualquer rodada

1. **Entrada do rascunho:** a pergunta e o **corpus inteiro** (`corpus/dispositivos.json` do P2 na tag fixada: 649 dispositivos, cerca de 360 mil caracteres). A IA não usa as ferramentas de busca do P2. Assim, uma falha da busca do P2 não vira falha do gabarito: se a busca não acha um dispositivo, o gabarito acha e o modelo avaliado reprova, que é o que se quer medir.
2. **Saída do rascunho:** os campos de D13 (`answer_exists`, `expected_provisions`, `reference_date`), mais uma justificativa curta que cita o trecho do dispositivo.
3. **Conferência sem modelo (D13), sem mudança:** um dispositivo inexistente ou uma data que não bate com `efeitos.desde` recusa o rascunho.
4. **Confirmação do usuário**, numa tela com a pergunta, o rascunho e o **texto completo** de cada dispositivo esperado. O que ele confere não exige especialista:
   - o texto do dispositivo responde à pergunta, numa leitura simples?
   - se o rascunho diz "não existe no corpus", a justificativa convence?
5. **Na dúvida, `disputed: true`.** O caso sai do cálculo do juiz, como D13 já prevê. Não se força uma confirmação.
6. **O gabarito é fechado antes das rodadas** e nunca vê resposta do modelo avaliado. A ferramenta de rascunho recusa rodar em caso que já tem trace.

### R3. A anotação: amostra cega e anotações revisadas

Há dois tipos de anotação, e o arquivo diz qual é cada uma.

| Tipo | Quantos | Como se faz | Para que serve |
|---|---|---|---|
| **Cega** | pelo menos 30 traces, sorteados **do conjunto de teste** (D6), estratificados por hipótese, com semente registrada | O usuário anota só com o dossiê (R6), sem ver rascunho nenhum | **Única base do TPR/TNR do juiz** (critério 3) |
| **Revisada** | os demais traces | A IA rascunha e o usuário confirma ou muda cada veredito | Análise de erros (codificação aberta e axial), ajuste do juiz no conjunto de desenvolvimento, total de 100 traces anotados (critério 2) |

Regras:
- **A amostra cega sai do conjunto de teste**, porque D6 só mede TPR/TNR ali.
- **O rascunho de um trace cego só é gerado depois** que a anotação cega dele está gravada. A ferramenta de rascunho recusa trace cego sem anotação. Esses rascunhos tardios não são lixo: comparados com a anotação cega, eles dão a **taxa de acerto do rascunhador**, que diz quanto confiar nas anotações revisadas.
- **Poucos reprovados:** D6 pede de 10 a 15 reprovados por critério que o juiz decide. Com 30 traces isso dificilmente acontece. Se faltar, primeiro a amostra cega cresce. Se ainda faltar, o critério é declarado **"não calibrado"** no relatório, como D6 já prevê para o C4.
- **O relatório mostra quantas anotações há de cada tipo.** O critério 2 é cumprido pelas 100 com o tipo declarado, sem esconder que a maioria foi revisada.

### R4. Quem rascunha: uma terceira família (recomendação)

O rascunhador do gabarito e da anotação é um modelo de **família diferente da avaliada** (Claude, D4) **e da do juiz** (D8). Por exemplo, juiz GPT e rascunhos Gemini, ou o contrário. Ele é chamado pelo cliente HTTP do P1 via OpenRouter, com versão exata fixada e registrada, chave só por variável de ambiente e teto de custo no ledger.

Por quê:
- **Diferente da avaliada:** um gabarito rascunhado por Claude tende a achar os mesmos dispositivos que o Claude avaliado acha e a errar onde ele erra.
- **Diferente do juiz:** se o rascunhador e o juiz fossem da mesma família, os dois errariam juntos, e o juiz pareceria melhor do que é nas anotações revisadas e no conjunto de desenvolvimento, onde ele é ajustado.
- **Contexto longo:** o modelo precisa receber o corpus inteiro (R2.1).

O modelo exato é escolhido depois de conferir o preço e o tamanho de contexto disponíveis no OpenRouter.

### R5. Medir a ancoragem

Quem revisa um rascunho tende a concordar com ele. Isso não se evita, mas se mede:
- o **rascunho é guardado** ao lado da anotação final, e nunca é sobrescrito;
- o relatório mostra **em quantos vereditos revisados o usuário mudou o rascunho**, e em quais critérios;
- compara **essa taxa de mudança com a taxa de erro do rascunhador na amostra cega** (R3). Exemplo: o rascunhador erra 20% na amostra cega, mas o usuário mudou só 2% dos rascunhos revisados. Isso indica ancoragem, e o relatório diz isso.

O mesmo vale para o gabarito: guarda-se o rascunho e conta-se quantos o usuário mudou ou marcou como `disputed`.

### R6. O dossiê (entorno)

Um comando gera, por trace, uma página com a pergunta, o gabarito confirmado, a resposta final do modelo e o texto completo de cada dispositivo que as ferramentas devolveram (a partir de `result_raw`).

- **O dossiê cego não mostra veredito nenhum:** nem do rascunho, nem do juiz, nem das checagens em código. Só fatos.
- O dossiê revisado mostra também o rascunho, marcado como tal.
- **O CPF/CNPJ sintético é mascarado no dossiê**, que pode ser aberto fora do terminal. A regra de D5 continua: nenhum número entra em arquivo versionado.

### R7. O que é núcleo e o que é entorno

- **Núcleo (continua do usuário):** o formato de anotação, incluindo como marcar o tipo (cega ou revisada) e onde guardar o rascunho; as métricas TPR/TNR, que passam a usar só as anotações cegas; e o juiz.
- **Entorno (Claude implementa, usuário revisa):** o rascunhador do gabarito e da anotação, o sorteio da amostra cega e o dossiê.
- **Ponto a confirmar:** o rascunhador de anotação é parecido com o juiz (lê o trace e devolve vereditos). Ele fica no entorno porque **não produz nenhum número que se reporta como medida**: quem sustenta o critério 3 é a amostra cega. O prompt dele usa as definições de critério de D2 sem reescrevê-las, e o usuário as revisa. Se o usuário preferir, o rascunhador passa para o núcleo.

## O que muda na spec principal, se aprovado

| Onde | Muda para |
|---|---|
| D1 | O rascunhador e o dossiê entram no entorno (R7) |
| D2, decisões da Tarefa 5 | A anotação diz o tipo (cega ou revisada); o rascunho é guardado à parte (R3, R5) |
| D5 | Nova pasta versionada para os rascunhos, com as mesmas regras de CPF/CNPJ |
| D6 | TPR/TNR medidos só na amostra cega, dentro do teste; ela cresce se faltarem reprovados (R3) |
| D8 | O juiz e o rascunhador são de famílias diferentes entre si (R4) |
| D13 | O gabarito é rascunhado por IA a partir do corpus e confirmado pelo usuário, antes das rodadas (R2) |
| Limites conhecidos | "Um único anotador" passa a ser "um anotador leigo, com rascunho de IA"; entram os limites abaixo |
| `docs/roadmap/p3-no-roadmap.md` | A frase "a anotação é de quem entende do assunto" ganha a ressalva de R2 |
| README | Declara que a referência é a fidelidade ao corpus, não a correção jurídica |

## Limites (entram no README)

- **A referência é a fidelidade ao corpus.** Nem o usuário nem o rascunhador são especialistas. Um gabarito juridicamente errado, mas coerente com o texto, passa.
- **A amostra cega é pequena.** Com cerca de 30 traces, os intervalos de TPR/TNR são largos, e alguns critérios podem ficar "não calibrados".
- **Ancoragem nas revisadas.** Ela é medida (R5), não eliminada.
- **O rascunhador também é um LLM.** Ele pode errar a leitura do corpus do mesmo jeito que o modelo avaliado, mesmo sendo de outra família. A conferência sem modelo pega dispositivos e datas inexistentes, não leitura errada.

## Alternativas descartadas

- **A IA anota tudo:** quebra o critério 3.
- **O usuário anota tudo sem rascunho:** ele disse que não consegue.
- **Gabarito de fontes oficiais** (perguntas e respostas da Receita, cartilhas): o usuário escolheu o rascunho pelo corpus. Pode voltar depois como conferência de uma parte dos gabaritos.
- **Rascunhador Claude:** compartilha os vieses do modelo avaliado, justamente no gabarito.
- **Rascunhador da mesma família do juiz:** os dois errariam juntos.

## Ainda em aberto

| Decisão | Gatilho |
|---|---|
| Modelo exato do rascunhador e do juiz | Conferir preço e contexto no OpenRouter, antes do passo do rascunhador |
| Tamanho final da amostra cega | Depois de anotar os 30 primeiros e contar os reprovados |
| Quanto tempo leva uma anotação cega | Teste com o dossiê de 1 trace, antes de sortear a amostra (previsão do passo 18) |

## Primeiro passo sugerido, se aprovado

Gerar o dossiê de um dos traces de confirmação que já existem e anotá-lo às cegas, medindo o tempo. Custa zero, porque não chama modelo, e testa a ideia central antes de qualquer outra peça.
