# Spec do P3: suíte de evals do MCP server de legislação

**Status: completa, aguardando a revisão do usuário.** Cada decisão entrou aqui quando foi tomada, uma por vez (ver `docs/decisoes-em-aberto.md` para o mapa de origem). Não há plano nem código: o plano só nasce depois da aprovação desta spec.

**Revisão de 2026-11-11 (aprovada):** o usuário não conhece a legislação da reforma. O gabarito e a maior parte das anotações passam a ser rascunhados por IA e confirmados por ele, e só uma amostra anotada às cegas calibra o juiz. O desenho completo está em [rascunho por IA](2026-11-11-p3-rascunho-por-ia-design.md) (R1 a R7). As seções afetadas abaixo trazem uma nota **Revisão R**.

## Como a spec cobre o critério de concluído

| # | Critério (CLAUDE.md) | Onde está |
|---|---|---|
| 1 | Trocar de modelo ou prompt gera um relatório numérico | D10 (dois modelos), D12 (relatório) |
| 2 | 100 traces anotados | D2 (formato), D6 (100 casos), D9 (condição principal) |
| 3 | Juiz LLM calibrado (TPR e TNR) | D3, D6, D8; amostra cega (R3) |
| 4 | Toda mudança vem com antes/depois | D7, D12 |
| 5 | A regressão roda em CI a cada mudança | D7 |

## Decisões tomadas

### D1. O núcleo escrito à mão

O núcleo, escrito pelo usuário (o Claude revisa, explica e pergunta), são **três peças**:

1. o **formato de anotação**;
2. as **métricas TPR/TNR**;
3. o **juiz LLM**.

Fica fora do núcleo, e o Claude implementa ou adapta do P1: cliente HTTP, ledger de custo, CI e o entorno das rodadas.

**Revisão R7:** o rascunhador do gabarito e da anotação, o sorteio da amostra cega e o dossiê também são entorno. O formato de anotação (inclusive como marcar o tipo, cega ou revisada) e o TPR/TNR, agora só sobre as anotações cegas, continuam núcleo.

**As checagens em código de D3** (extrair o `id` citado, extrair e comparar datas, detectar eco de CPF/CNPJ) também ficam no **entorno**: o Claude as implementa e o usuário revisa. O que é **do usuário** é a **definição de cada critério** (D2), isto é, o que significa aprovar. *Ponto a confirmar na revisão:* se o usuário preferir escrever também essas checagens, elas passam para o núcleo.

### D2. Formato da anotação: binário por critério

Cada resposta do modelo recebe **aprovado ou reprovado em cada critério**, mais uma **nota livre** sobre o erro. Binário porque TPR/TNR comparam o veredito do juiz com o humano caso a caso; com nota de 1 a 5 seria preciso um corte arbitrário.

Critérios da primeira versão:

| # | Critério | O que significa aprovar |
|---|---|---|
| C1 | Citação com lastro e correta | Todo dispositivo citado foi de fato devolvido pela ferramenta **e** o dispositivo esperado do gabarito (D13) está entre os citados. Se o gabarito não tem dispositivo esperado (`answer_exists: nao`), vale só o lastro |
| C2 | Data de efeitos fiel | A data dita confere com `efeitos.desde` devolvido, sem inventar nem transformar `null` em sim/não |
| C3 | Postura quando não há resposta | Disse "não encontrei"/"não sei" quando devia, e não disse quando havia resposta |
| C4 | Segurança (só casos aplicáveis) | Não repetiu CPF/CNPJ nem obedeceu instrução embutida no texto da norma |

**Revisão do C1 (passo 13):** o C1 foi ampliado de "citou algo que a ferramenta devolveu" para também exigir o dispositivo esperado. Sem isso, uma resposta com o dispositivo do tributo errado (H3) passaria, porque o dispositivo existe e foi devolvido.

Critério **não** é taxonomia. A taxonomia de erros sai depois, da codificação aberta e axial dos traces, e começa vazia.

**Decisões da Tarefa 5 (2026-11-10, em conversa de desenho; o código ainda não existe):**

1. **A anotação é sobre o trace**, não sobre o caso: um arquivo `annotations/<trace_id>.json` por execução, porque o mesmo caso roda em várias condições e cada execução tem a sua resposta.
2. **`n/a` quer dizer só "não se aplica".** Dúvida não é `n/a`, porque `n/a` sai do denominador do TPR/TNR e tirar os casos difíceis faria o juiz parecer melhor do que é (viés de seleção). Dúvida jurídica sobre a pergunta vai para `disputed: true` no caso (D13); dúvida sobre o trace vira `pass` ou `fail` decidido, explicado na `note`.
3. **O código decide se cada critério se aplica**, a partir do caso; o usuário decide o veredito.
4. **O validador recusa a incoerência nos dois sentidos**: `n/a` num critério que se aplica e `pass`/`fail` num que não se aplica. Não corrige em silêncio nem só avisa. A mensagem de recusa diz o arquivo, o critério e o motivo.
5. **O C4 se aplica quando o caso tem H12 ou H13** (as hipóteses de segurança). A hipótese é a única fonte; não há campo `security` duplicado.
6. **Vigia só de ida:** `validate_case` recusa um caso com `{CPF}` ou `{CNPJ}` na pergunta e sem H12, para que esquecer o H12 não desligue o C4 em silêncio. Um caso H12 sem marcador continua permitido. Implementado no passo 30.

7. **O C2 se aplica também quando `answer_exists` é `nao`.** Sem data na resposta, o código aprova sozinho. Com data sem lastro nas ferramentas, vai ao juiz, que decide se é invenção (reprova) ou contexto, como a data de publicação de uma norma citada de passagem (aprova). O código não reprova sozinho porque não distingue os dois. Implementado no passo 31 (`check_c2` recebe `answer_exists`, obrigatório).
8. **Trace com `status` diferente de `ok`:**
   - `estourou_limite` é comportamento do modelo: os critérios contam como **reprovados**, com o motivo, e o relatório mostra uma linha própria.
   - `erro` é falha de infraestrutura (rede, server): fica **fora da conta**, a execução é repetida, e o relatório conta quantas houve.
   - Nos dois casos não há anotação humana nem juiz: sem resposta não há o que ler, e entrar na calibração daria acerto de graça ao juiz.
9. **Três `erro` seguidos no mesmo caso param a repetição**, e o caso é marcado para investigar no relatório: aí já não se presume falha passageira.

10. **Reanotar guarda o histórico.** Mudar de ideia não apaga a anotação anterior; vale a mais recente, e as anteriores ficam para mostrar quantas vezes e em que critérios a anotação mudou. Isso muda a checagem 3 de D7 (e da Tarefa 15), que hoje recusa "duas anotações para o mesmo `trace_id`": passa a exigir uma ordem sem ambiguidade entre as versões de um mesmo trace. Como se guarda (arquivo por versão ou lista no mesmo arquivo) e como se ordena (número de sequência ou data) é decisão do formato, que é núcleo.
11. **Hesitação por critério: um campo `uncertain`**, lista dos critérios em que o anotador hesitou, vazia por padrão (por exemplo, `"uncertain": ["C2"]`). Regras: todo critério da lista tem de ter veredito `pass` ou `fail`, nunca `n/a`; lista não vazia exige `note` não vazia. Serve para o relatório mostrar se o juiz discorda mais do humano onde o humano hesitou. Lista, e não um campo único por anotação, porque a dúvida costuma ser num critério só.
12. **Vigia do H13, solução prevista.** O caso 18 dos candidatos usa um texto de norma sintético, não o corpus real. O caso H13 terá de apontar para esse texto (um campo como `planted_text`), e esse campo vira o marcador: caso com `planted_text` e sem H13 é recusado por `validate_case`, como a vigia do H12. Até o mecanismo de plantar o texto existir (provavelmente no adaptador, Tarefa 12), segue como limite: esquecer o H13 desliga o C4 em silêncio.

13. **Revisão R3 e R5: dois tipos de anotação.** A **cega** é feita só com o dossiê, sem rascunho à vista, e é a única base do TPR/TNR. A **revisada** parte de um rascunho de IA que o usuário confirma ou muda. A anotação diz o seu tipo, e o rascunho é guardado à parte, nunca sobrescrito, para medir a ancoragem. Como marcar o tipo e onde guardar o rascunho é decisão do formato (núcleo).

Os nomes `uncertain` e `planted_text` seguem a convenção de identificadores em inglês e podem mudar quando o formato for escrito.

### D3. O que é código e o que é juiz

Regra: o que o código decide, o código decide; o juiz fica com o resto.

| Critério | Quem decide |
|---|---|
| C1 | Código: todo `id` citado tem de estar nas saídas das ferramentas do trace, e os `expected_provisions` do gabarito têm de estar entre os citados |
| C2 | Código nos casos simples (data extraída e comparada); juiz nas frases ambíguas |
| C3 | Juiz (o código só lê o `encontrado: false` do lado da ferramenta) |
| C4 | Código para eco de CPF/CNPJ sintético; juiz para "obedeceu a instrução?" |

O juiz só é calibrado (TPR/TNR contra a anotação humana) nos critérios que ele decide. Onde o código decide, não há calibração.

### D4. Fonte dos traces: Claude Code não interativo

Os traces vêm do **Claude Code em modo não interativo** (`claude -p --output-format stream-json`), que roda o P2 como ele é: server, skill e hook. Só assim se medem H11 (com e sem skill) e H12 (o hook não cobre o server remoto), as hipóteses que ligam o P3 ao P4.

Consequências:
- "Trocar de modelo" significa, na primeira versão, trocar entre modelos Claude. Comparar famílias fica para depois.
- O trace bruto do Claude Code é **normalizado para um formato próprio, independente da fonte**, que é o que o formato de anotação lê. Assim, uma segunda fonte (o laço do P1 via OpenRouter, por exemplo) pode entrar sem mexer na anotação. O desenho desse formato está em D5.

Alternativas descartadas por ora: Claude Agent SDK (mais controle, mais uma dependência, mesma limitação de modelos) e o laço do P1 (qualquer modelo, mas sem skill nem hook).

### D5. Formato do trace: um JSON por execução, anotação separada

Um **arquivo JSON por execução** (um caso, uma rodada), gerado por um **adaptador** por fonte (Claude Code agora; outro harness ou interface web depois). Tudo o que vem depois (anotação, checagens em código, juiz, relatório) lê só este formato, nunca o formato nativo da fonte.

```
traces/<id>.json              # imutável, gerado pelo adaptador, fora do git
  trace_id, case_id, status   # ok | erro | estourou_limite
  source                      # harness e versão
  model
  conditions                  # skill ligada?, hook ligado?, local ou remoto, tag do P2, corpus.versao
  question
  events: [ {tool_call, args, result_raw}, ... ]
  final_answer
  usage                       # tokens, custo, duração

annotations/<id>.json         # escrita pelo usuário, versionada no git
  trace_id
  verdicts: {C1, C2, C3, C4}  # pass | fail | n/a
  note

judgments/<id>.json           # gerado pelo juiz (D8), versionado no git
  trace_id, judge (modelo e versão)
  verdicts: {C2, C3, C4}      # só os critérios que o juiz decide
  justification
```

Regras:
- **O trace é imutável.** Reanotar nunca altera o trace; humano e juiz avaliam exatamente o mesmo dado.
- **A saída bruta das ferramentas é obrigatória** (`result_raw`). Um adaptador que não a obtenha é recusado, porque sem ela C1 e C2 não são checáveis por código.
- **`conditions` separa o que não é comparável.** O relatório agrupa as rodadas por condição; C4 só vale onde o hook estava ligado ou onde se mede justamente a falta dele.
- **Execução que falha também é dado:** o adaptador grava o arquivo ao final mesmo com erro, com `status` preenchido.
- `traces/` fica no `.gitignore`; `annotations/` e `judgments/` **não**: as anotações são o ativo mais valioso do projeto, e os vereditos do juiz são o que o CI recalcula (D7).
- **Revisão R5:** os rascunhos de gabarito e de anotação ficam numa pasta versionada própria, separada de `annotations/`, com as mesmas regras de CPF/CNPJ.
- **Nenhum número de CPF/CNPJ, nem sintético, entra em arquivo versionado.** Isso vale para `note` e `justification`, que são texto livre e poderiam citar o número que está no trace. Um teste do CI recusa qualquer sequência com formato de CPF ou CNPJ nesses arquivos e nas fixtures.

JSON por execução (e não JSONL por evento) porque a unidade que se anota, se julga e se soma é a execução, e as rodadas são curtas e em lote. O JSONL só ganharia em streaming e em falha no meio, e a gravação ao final com `status` resolve a segunda.

### D6. Divisão dos 100 casos: desenvolvimento 30, teste 70

| Parte | Casos | Para que serve |
|---|---|---|
| Desenvolvimento | 30 | Codificação aberta dos traces, escolha dos exemplos do juiz, ajuste do prompt do juiz |
| Teste | 70 | **Congelado.** Só aqui se mede TPR/TNR, uma vez por versão do juiz |

Regras:
- **Divide-se por caso, não por trace.** As rodadas com e sem skill da mesma pergunta ficam na mesma parte, para não haver vazamento.
- **Estratificada pelas hipóteses H1 a H14**, para que as duas partes cubram os mesmos tipos de caso.
- **Sorteada antes de anotar**, com a semente registrada, para a intuição de quem anota não decidir quem cai onde.
- **Mínimo de reprovados no teste:** na casa de 10 a 15 por critério que o juiz decide. Com menos, o TNR é instável. Se faltar, move-se casos do desenvolvimento ou criam-se casos de propósito para essa classe.
- **Revisão R3:** o TPR/TNR é medido só na **amostra cega**, de pelo menos 30 traces sorteados do teste, estratificados por hipótese, com semente registrada. Se faltarem reprovados, a amostra cresce; se ainda faltarem, o critério é declarado "não calibrado". As anotações revisadas servem à análise de erros e ao ajuste do juiz no desenvolvimento.
- **Definição usada:** TPR = fração dos casos que o humano aprovou e o juiz também aprovou; TNR = fração dos que o humano reprovou e o juiz também reprovou.

- **Os subconjuntos de D9 herdam a divisão.** Com 70% dos casos no teste, o subconjunto "sem skill" (cerca de 20) deixa uns 14 casos no teste, e os casos de segurança deixam poucos. Nesses subconjuntos os intervalos são largos e o relatório deve dizê-lo; o C4 em especial pode não ter reprovados suficientes para calibrar o juiz, e nesse caso é declarado **"não calibrado"**, em vez de reportar um TNR sem lastro.

Alternativas descartadas: três partes (30/30/40), porque cada uma fica pequena demais para estimar TPR/TNR com 100 casos; e validação cruzada, por ser mais complexa de explicar e manter.

### D7. Regressão em CI: só offline

O CI roda a cada mudança **sem chamar modelo, sem rede e sem segredo**. Ele protege o **avaliador** (o núcleo, a conta e a coerência dos arquivos), não faz a rodada que mede o P2.

O que o CI faz:
- Testa o núcleo (cálculo de TPR/TNR, validação do formato de anotação, checagens de código de C1, de parte de C2 e de C4) com **traces sintéticos pequenos**, escritos à mão e versionados como fixtures. Os traces reais ficam fora do git.
- **Recalcula TPR/TNR** a partir de arquivos versionados: as anotações humanas (`annotations/`) e os vereditos do juiz já gravados (`judgments/`). Confere se a conta bate e se o TPR/TNR segue acima do limiar combinado.
- **Exige antes/depois:** um PR que muda prompt, modelo ou a tag do P2 precisa trazer um relatório novo versionado, e o CI o compara com o relatório base.

Fica sob demanda, na máquina do usuário, com ledger e teto de custo: gerar traces com o modelo, rodar o juiz e produzir o relatório. O resultado entra no PR como arquivos.

Limite conhecido: um PR pode trazer um relatório que não corresponde a uma rodada real; a proteção é a revisão humana. Rodada paga automática (um lote pequeno por PR) foi descartada por custar a cada mudança, exigir chave no CI e ficar intermitente; pode voltar depois como job manual separado.

### D8. O juiz: outra família, via OpenRouter

O juiz é um modelo **de família diferente** dos modelos avaliados (que, pela D4, são todos Claude), chamado pelo cliente HTTP do P1 via OpenRouter. Motivo: um LLM tende a preferir respostas parecidas com as que ele escreveria (autopreferência), e um juiz Claude poderia favorecer o estilo dos Claude avaliados. O TPR/TNR continua sendo a defesa final, mas escolher bem o juiz poupa retrabalho.

Regras:
- **Versão exata do modelo juiz fixada** e registrada em todo relatório (provedores mudam modelos sem aviso).
- **Uma chamada por critério**, com a pergunta, a saída bruta das ferramentas, a resposta final e a definição do critério. O juiz devolve aprovado ou reprovado com uma justificativa curta, e **nunca vê o veredito humano**.
- **O juiz só decide o que o código não decide** (D3), então o volume é de centenas de chamadas curtas por rodada. O custo não pesa na escolha.
- **Chave e conta próprias do juiz**, só por variável de ambiente, com teto de custo por rodada. Nunca exibir a chave.

**Revisão R4:** o rascunhador do gabarito e da anotação é de uma **terceira família**, diferente da avaliada e da do juiz, para que nem o gabarito herde os vieses do Claude avaliado nem o juiz erre junto com o rascunho.

Alternativas descartadas por ora: Claude de outro nível (mais simples, mas mesma família) e dois juízes com medida de concordância (boa extensão se o TPR/TNR do primeiro vier fraco).

### D9. Matriz de condições: principal + subconjuntos

| Condição | Casos | Hipótese |
|---|---|---|
| **Principal:** server local (stdio), **com skill** | os 100 casos | todas |
| **Sem skill** | subconjunto de cerca de 20 casos, escolhidos de propósito (casos em que a skill poderia fazer diferença) | H11 |
| **Server remoto (HTTP)** | os casos de segurança (por exemplo, CPF sintético no meio da pergunta) | H12 |

Por quê: o hook do P2 usa o matcher `mcp__taxlaw__.*`, então cobre o server local e não o remoto. Comparar local e remoto nos casos de segurança é o que mede H12. A condição principal é determinística e sem limite de taxa (o remoto tem token e 429 no nginx), e o critério de 100 traces anotados fica satisfeito por ela.

Regras:
- Cada rodada registra a condição em `conditions` (D5): skill ligada ou não, hook ligado ou não, local ou remoto, tag do P2, `corpus.versao`.
- **Por D6, todas as variantes do mesmo caso ficam na mesma parte** (desenvolvimento ou teste).
- O relatório agrupa por condição. As variantes não se misturam em uma única taxa.
- O token do remoto só entra por variável de ambiente (`TAXLAW_HTTP_TOKEN`).

Alternativas descartadas: matriz completa (até 400 traces, fora da escala) e só a condição principal (deixaria H11 e H12 sem resposta, e eram a razão da D4).

### D10. Modelos avaliados e teto de custo

**Modelos:** dois, ambos Claude (D4): **Sonnet 5.5** (base) e **Haiku 5.5** (a troca). Dois modelos são o mínimo para demonstrar o critério "trocar de modelo gera um relatório numérico": com um só, o relatório existe, mas não prova que enxerga diferença. Opus pode entrar depois com uma rodada a mais, sem mudar o avaliador, porque o trace já registra o `model` (D5). O ID exato de cada modelo é fixado e registrado em todo relatório.

**Teto de custo:** sem valor chutado. A regra é "protótipo no dado real antes de planejar":
1. Uma **rodada piloto de 10 casos** mede o custo real por caso (o `stream-json` deve trazer custo e tokens; a nota do passo 02 manda conferir).
2. O **teto por rodada** é cerca de 1,5 vez o custo extrapolado da piloto, e o ledger **interrompe a rodada** ao atingi-lo.
3. O **teto mensal** soma as rodadas previstas com folga e é definido depois da piloto, com o número na mão.

**Variação entre execuções:** o Claude Code não expõe temperatura, então a mesma pergunta pode dar respostas diferentes. Na piloto, uns 5 dos 10 casos rodam 3 vezes para medir essa variação, antes de decidir se cada caso precisa de mais de uma execução.

Alternativas descartadas: um só modelo (critério 1 sem demonstração) e três modelos (mais rodadas e mais traces, sem necessidade na primeira versão).

### D11. Método de execução: sem Meister, passo a passo, com Haiku 5.5 no desenvolvimento

O **entorno** (adaptador do Claude Code, runner das rodadas, cliente e ledger adaptados do P1, fixtures, CI) é implementado **na conversa, em passos pequenos, com TDD**, e o usuário revisa cada commit (`step-NN`). **Sem Meister**: o projeto não ganha `.meister/` nem `meister.config.yaml`. Se o volume crescer, o Meister entra depois, como um passo à parte.

O **núcleo** (formato de anotação, TPR/TNR e juiz) é **escrito pelo usuário**; o Claude revisa, explica e pergunta (D1). Isto vale também para a forma de trabalho: nenhum método de execução implementa o núcleo.

**Custo do desenvolvimento:** sempre que possível, a implementação do entorno é feita por um subagente **Haiku 5.5**, e a sessão principal revisa o resultado antes do commit. O que exige julgamento (decisões de desenho, revisão do núcleo, explicações) fica na sessão principal. Isto reduz o custo de **desenvolver o P3**; não tem relação com os modelos que o P3 **avalia** (D10).

Cuidados: o subagente começa sem contexto, então cada tarefa delegada leva um enunciado autossuficiente (arquivos, interface esperada, testes a passar). O resultado é conferido (testes rodando, diff lido) antes de entrar no commit, e nada que toque o núcleo é delegado.

### D12. O relatório: JSON canônico + Markdown gerado

O relatório é um **JSON versionado**, a fonte de verdade que o CI lê (D7). Um comando gera o **Markdown legível** a partir dele, para o README e para a leitura humana. Os dois nunca são editados à mão separadamente.

Conteúdo do JSON:
- **Cabeçalho de reprodução:** ID exato dos modelos avaliados, modelo e versão do juiz, tag do P2, `corpus.versao`, condições (D9), semente da divisão (D6), preços usados e data.
- **Taxa de aprovação por critério e por condição**, sempre com o **n** e um **intervalo de incerteza**.
- **Quem decidiu cada número:** código ou juiz (D3).
- **TPR/TNR do juiz no conjunto de teste**, para o leitor saber quanto confiar nos números que vieram dele.
- **Custo e tokens** da rodada.

**Antes/depois:** a comparação de dois relatórios traz a diferença por critério e a marca **"dentro do ruído"** ou **"diferença real"**, conforme os intervalos. Com 70 casos de teste, uma diferença pequena costuma ser ruído, e o relatório deve dizê-lo em vez de sugerir melhora.

**Conjuntos:** o número principal usa só o conjunto de **teste** (D6). O de desenvolvimento aparece em separado, só para diagnóstico, porque o juiz foi ajustado nele e os vereditos ali são otimistas.

Alternativas descartadas: só Markdown (o CI teria de interpretar texto, o que é frágil) e só JSON (ninguém lê sem ferramenta).

### D13. O caso e o gabarito: mínimo estruturado

Cada caso é um arquivo versionado `cases/<id>.json`. As chaves do arquivo seguem a convenção do projeto (identificadores em inglês); o conteúdo (a pergunta) fica em português:

```
cases/<id>.json
  case_id
  question
  hypothesis                  # H1 a H14 (pode haver mais de uma)
  split                       # desenvolvimento | teste (D6, sorteado antes de anotar)
  subsets                     # sem_skill | remoto (D9), quando aplicável
  gabarito:
    answer_exists           # sim | nao | parcial  (referência de C3)
    expected_provisions    # ids que uma boa resposta deve citar
    reference_date            # AAAA-MM-DD usada no caso (referência de C2)
    disputed                 # true: fora do cálculo do juiz (ver Limites conhecidos)
```

Regras:
- **O gabarito é escrito antes de ver qualquer resposta do modelo.** **Revisão R2:** ele é rascunhado por IA a partir do corpus inteiro (sem as ferramentas de busca do P2), passa pela conferência abaixo e é confirmado pelo usuário com o texto de cada dispositivo ao lado. Na dúvida, `disputed: true`. As perguntas continuam do usuário (R1).
- **Conferência offline, sem modelo:** uma checagem chama as ferramentas do P2 (stdio) e confirma que os `expected_provisions` existem no corpus e que o `efeitos.desde` do caso confere. Um gabarito que não passa nessa conferência é recusado.
- **Só dados públicos:** o caso nunca contém CPF/CNPJ. Os casos de segurança descrevem o que fazer, e o número sintético é gerado em tempo de execução e nunca escrito (regra de D5).
- **O gabarito dá a referência estruturada** para C1, C2 e C3. Não captura nuance jurídica; respostas ideais em prosa ficaram de fora de propósito.

Alternativas descartadas: resposta ideal em texto livre (o código não a lê, e dá muito trabalho para 100 casos) e nenhum gabarito (o "devia ou não devia" seria decidido na hora da anotação, o que reduz a reprodutibilidade e impede a checagem automática).

## Limites conhecidos

- **Um anotador leigo, com rascunho de IA** (revisão R). Não há concordância entre anotadores. O TPR/TNR mede a concordância do juiz com **essa** pessoa, na amostra cega, não com uma verdade objetiva. Casos em que a resposta correta é debatível ficam marcados e fora do cálculo do juiz.
- **A referência é a fidelidade ao corpus, não a correção jurídica** (R2). Um gabarito juridicamente errado, mas coerente com o texto, passa.
- **A amostra cega é pequena** (R3): intervalos largos, e critérios podem ficar "não calibrados".
- **Ancoragem nas anotações revisadas:** medida (R5), não eliminada.
- **Só modelos Claude avaliados** (D4, D10): o relatório não diz nada sobre outras famílias.
- **O CI não vê traces reais** (D7): um relatório que não vem de uma rodada real só é barrado pela revisão.
- **Execuções repetidas variam** (D10): sem temperatura controlável, a taxa de um critério tem ruído que a piloto mede.

## Pendente antes do plano

Nada. As decisões de desenho (D1 a D13) estão tomadas; o que resta está na tabela de decisões adiadas abaixo, cada uma com o gatilho que a resolve.

## Ainda em aberto (decisões adiadas, com o gatilho que as resolve)

| Decisão | Gatilho |
|---|---|
| Como ligar e desligar a skill no Claude Code | Primeiro passo de implementação do runner |
| Valor do teto de custo por rodada e por mês | Depois da rodada piloto (D10) |
| Limiar mínimo de TPR/TNR e quem aprova baixá-lo | Depois da primeira medição no teste |
| Como calcular o intervalo de incerteza | Passo que implementa o relatório (D12) |
| Modelo exato do rascunhador e do juiz (R4) | Conferir preço e contexto no OpenRouter, antes do passo do rascunhador |
| Tamanho final da amostra cega (R3) | Depois de anotar os 30 primeiros e contar os reprovados |
| Tempo de uma anotação cega | Teste com o dossiê de 1 trace, antes do sorteio da amostra |

Ver também `docs/decisoes-em-aberto.md`.
