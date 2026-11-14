# Gabaritos para confirmar (rascunho do DeepSeek)

- **Gerado em:** 2026-11-13, com `evals/drafter.py` (passo 33), `deepseek/deepseek-v4.1-flash-1017`, o prompt `config/drafter_prompts/gabarito.md`, o corpus do P2 na tag `step-16` (corpus_version `c269388fb2bd`) e a data de referência **2026-11-13** para todos.
- **Custo:** US$ 1,1027 para os 100. **Recusados pelo código: 0.** Todos passaram nas conferências: trechos literais, ids existentes no P2 na data, data igual à pedida e `validate_case`.
- **Resposta existe no corpus:** sim 65, parcial 15, não 20.
- **Atenção primeiro a estes 21 casos:** nas perguntas que você manteve como a IA escreveu, o palpite de quando a pergunta foi criada ("Resposta esperada") diverge do gabarito. Os dois são do mesmo modelo, mas de chamadas independentes; onde discordam, um dos dois errou: c007, c010, c011, c015, c016, c017, c026, c027, c032, c038, c041, c046, c053, c055, c057, c068, c073, c081, c082, c090, c093.
- **O que o código não confere** (é com você): se os dispositivos citados são os que a pergunta pede, se "existe resposta" está certo e se faltou algum dispositivo. Os trechos são literais: confira se eles **dizem** o que a pergunta pede.
- **Como confirmar:** na linha **Decisão** de cada caso, escreva **confirmar**, **mudar: \<o que muda\>** (por exemplo, `mudar: answer_exists nao`, `mudar: tirar EC132.art8`) ou **disputed: \<por quê\>** quando não tiver certeza.

## c001 · H1

**Pergunta:** Em que momento exatamente ocorre o fato gerador do IBS na prestação de serviço?

**Existe resposta no corpus:** `nao`

**Dispositivos esperados:** nenhum

**Justificativa:** O corpus não traz regra que fixe o momento exato do fato gerador do IBS na prestação de serviço. Há apenas a previsão constitucional de que o IBS incide sobre operações com serviços e de que IBS e CBS observam as mesmas regras quanto a fatos geradores, mas isso não define o momento. Na data de referência, 2026-11-13, não há dispositivo no corpus que responda a esse ponto. Portanto, a resposta não existe no corpus.

**Decisão:** confirmar

---

## c002 · H1

**Pergunta:** O valor do frete e do seguro entra no cálculo do IBS e da CBS?

**Existe resposta no corpus:** `nao`

**Dispositivos esperados:** nenhum

**Justificativa:** O corpus não contém dispositivo que trate especificamente da inclusão do valor do frete e do seguro na base de cálculo do IBS e da CBS. As menções a “seguro” no corpus referem-se a serviços financeiros ou a operações de seguros em contexto diverso, não à composição da base de cálculo dos tributos sobre bens e serviços. Portanto, não há elementos suficientes para responder à pergunta com base apenas no corpus.

**Decisão:** confirmar

---

## c003 · H1

**Pergunta:** Quais alimentos compõem a lista do Anexo I da LC 214/2025 com alíquota zero?

**Existe resposta no corpus:** `nao`

**Dispositivos esperados:** nenhum

**Justificativa:** O corpus contém o art. 125 da LC 214/2025, que reduz a zero as alíquotas do IBS e da CBS sobre produtos destinados à alimentação humana relacionados no Anexo I. Porém, o corpus não reproduz nem especifica os alimentos constantes desse Anexo I. Assim, não é possível responder quais alimentos compõem a lista com base apenas no corpus.

**Decisão:** confirmar

---

## c004 · H1

**Pergunta:** Qual é a alíquota padrão do IBS a partir de 2033?

**Sua dúvida anotada:** confirmar se o corpus traz a fixação da alíquota de referência pelo Senado

**Existe resposta no corpus:** `nao`

**Dispositivos esperados:** nenhum

**Justificativa:** O corpus não informa o valor numérico da alíquota padrão do IBS a partir de 2033. Há menções a alíquotas de referência a serem fixadas pelo Senado Federal (ADCT, art. 130) e a alíquotas-padrão fixadas na forma do art. 14 da LC 214/2025 (LC 214/2025, art. 126, § 4º), mas esse art. 14 não está no corpus e nenhum dispositivo traz o percentual aplicável. Portanto, a pergunta não pode ser respondida com base apenas no corpus.

**Decisão:** confirmar 

---

## c005 · H1

**Pergunta:** Qual vai ser a alíquota do Imposto Seletivo cobrada sobre cigarros?

**Existe resposta no corpus:** `parcial`

**Dispositivos esperados:** `LC214.art422` (LC 214/2025, art. 422); `LC214.art422.par1` (LC 214/2025, art. 422, § 1º); `LC214.art422.par1.incI` (LC 214/2025, art. 422, § 1º, I)

**Trechos citados (literais do corpus):**

- `LC214.art422`: “as alíquotas do Imposto Seletivo aplicáveis nas operações com os bens e os serviços referidos no Anexo XVII são aquelas previstas em lei ordinária.”
- `LC214.art422.par1`: “Serão aplicadas alíquotas ad valorem cumuladas com alíquotas específicas para:”
- `LC214.art422.par1.incI`: “I - produtos fumígenos classificados na posição 24.02 da NCM/SH; e”

**Justificativa:** O corpus não traz um percentual numérico para cigarros. Para a data de referência, o art. 422 da LC 214/2025 remete as alíquotas do Imposto Seletivo sobre os bens do Anexo XVII à lei ordinária. O § 1º e seu inciso I apenas determinam que, para produtos fumígenos da posição 24.02 da NCM/SH, serão aplicadas alíquotas ad valorem cumuladas com alíquotas específicas. Portanto, a resposta é apenas parcial: há a estrutura de cobrança, mas não o valor da alíquota.

**Decisão:** confirmar

---

## c006 · H1

**Pergunta:** Como fica a tributação de dividendos com a reforma?

**Existe resposta no corpus:** `nao`

**Dispositivos esperados:** nenhum

**Justificativa:** Não há dispositivo no corpus que trate especificamente da tributação de dividendos. A única menção a distribuição de lucros é sobre requisitos de redução de alíquotas para serviços profissionais, não sobre a incidência tributária sobre dividendos. Há previsão genérica de projeto de lei que reforme a tributação da renda, mas sem regra sobre dividendos.

**Decisão:** confirmar

---

## c007 · H1

**Pergunta:** A reforma tributária muda a tabela do Imposto de Renda da pessoa física?

**Existe resposta no corpus:** `parcial` ⚠️ diverge do palpite da criação (nao)

**Dispositivos esperados:** `EC132.art18.incI` (EC 132/2023, art. 18, I)

**Trechos citados (literais do corpus):**

- `EC132.art18.incI`: “I - em até 90 (noventa) dias após a promulgação desta Emenda Constitucional, projeto de lei que reforme a tributação da renda, acompanhado das correspondentes estimativas e estudos de impactos orçamentários e financeiros;”

**Justificativa:** O corpus não contém dispositivo que altere diretamente a tabela do Imposto de Renda da pessoa física. O dispositivo relacionado apenas determina o envio de projeto de lei para reformar a tributação da renda, sem fixar nova tabela ou especificar mudanças. Portanto, a resposta é apenas parcial: há previsão de reforma da renda, mas não de alteração da tabela do IRPF.

**Decisão:** mudar: answer_exists nao, sem dispositivos esperados (o art. 18, I da EC 132 apenas prevê envio de projeto de lei sobre renda em 90 dias, sem alterar a tabela do IRPF; em H1 o modelo deve constatar a ausência no corpus) 

---

## c008 · H1

**Pergunta:** Qual será a carga tributária total sobre o consumo depois da reforma?

**Existe resposta no corpus:** `nao`

**Dispositivos esperados:** nenhum

**Justificativa:** O corpus não traz dispositivo que fixe a carga tributária total sobre o consumo após a reforma. Ele institui o IBS e a CBS, prevê alíquotas transitórias e determina que o Senado fixe alíquotas de referência para assegurar equivalência de receita, mas não estabelece um percentual agregado final. Portanto, com a data de referência indicada, a pergunta não é respondida de forma completa.

**Decisão:** confirmar

---

## c009 · H1

**Pergunta:** Qual é o prazo para ressarcimento de créditos acumulados de IBS para empresas exportadoras?

**Existe resposta no corpus:** `parcial`

**Dispositivos esperados:** `CF.art156-A.par1.incIII` (CF, art. 156-A, § 1º, III); `CF.art156-A.par5` (CF, art. 156-A, § 5º); `CF.art156-A.par5.incIII` (CF, art. 156-A, § 5º, III)

**Trechos citados (literais do corpus):**

- `CF.art156-A.par1.incIII`: “III - não incidirá sobre as exportações, assegurados ao exportador a manutenção e o aproveitamento dos créditos relativos às operações nas quais seja adquirente de bem material ou imaterial, inclusive direitos, ou serviço, observado o disposto no § 5º, III;”
- `CF.art156-A.par5`: “§ 5º Lei complementar disporá sobre:”
- `CF.art156-A.par5.incIII`: “III - a forma e o prazo para ressarcimento de créditos acumulados pelo contribuinte;”

**Justificativa:** O corpus assegura ao exportador a manutenção e o aproveitamento dos créditos de IBS e remete ao § 5º, III, a disciplina do ressarcimento. Esse dispositivo determina que lei complementar disporá sobre a forma e o prazo para ressarcimento de créditos acumulados, mas não fixa um prazo numérico. Portanto, na data de referência, não há prazo específico no corpus para empresas exportadoras; apenas a previsão de que ele será definido em lei complementar.

**Decisão:** confirmar

---

## c010 · H1

**Pergunta:** Quais produtos estão sujeitos ao Imposto Seletivo?

**Existe resposta no corpus:** `sim` ⚠️ diverge do palpite da criação (nao)

**Dispositivos esperados:** `ADCT.art126` (ADCT, art. 126); `ADCT.art126.incI` (ADCT, art. 126, I); `ADCT.art126.incI.alib` (ADCT, art. 126, I, b)

**Trechos citados (literais do corpus):**

- `ADCT.art126`: “Art. 126. A partir de 2027:”
- `ADCT.art126.incI`: “I - serão cobrados:”
- `ADCT.art126.incI.alib`: “b) o imposto previsto no art. 153, VIII, da Constituição Federal;”

**Justificativa:** Na data de referência, ainda não há produtos sujeitos ao Imposto Seletivo, pois o art. 126 do ADCT determina que a cobrança começa a partir de 2027. O inciso I indica os tributos que serão cobrados, e a alínea "b" inclui o imposto previsto no art. 153, VIII, da Constituição Federal. Como 13/11/2026 é anterior a 2027, nenhum produto está sujeito ao Imposto Seletivo nessa data.

**Decisão:** mudar: answer_exists nao, sem dispositivos esperados (a lista de produtos do Anexo XVII não consta do corpus; o gabarito utilizou sofisma temporal com o ADCT art. 126)

---

## c011 · H1

**Pergunta:** Qual é a alíquota do IBS em cada município?

**Existe resposta no corpus:** `parcial` ⚠️ diverge do palpite da criação (nao)

**Dispositivos esperados:** `CF.art156-A.par1.incV` (CF, art. 156-A, § 1º, V); `CF.art156-A.par1.incVI` (CF, art. 156-A, § 1º, VI); `CF.art156-A.par1.incVII` (CF, art. 156-A, § 1º, VII); `CF.art156-A.par1.incXII` (CF, art. 156-A, § 1º, XII); `ADCT.art125` (ADCT, art. 125)

**Trechos citados (literais do corpus):**

- `CF.art156-A.par1.incV`: “V - cada ente federativo fixará sua alíquota própria por lei específica;”
- `CF.art156-A.par1.incVI`: “VI - a alíquota fixada pelo ente federativo na forma do inciso V será a mesma para todas as operações com bens materiais ou imateriais, inclusive direitos, ou com serviços, ressalvadas as hipóteses previstas nesta Constituição;”
- `CF.art156-A.par1.incVII`: “VII - será cobrado pelo somatório das alíquotas do Estado e do Município de destino da operação;”
- `CF.art156-A.par1.incXII`: “XII - resolução do Senado Federal fixará alíquota de referência do imposto para cada esfera federativa, nos termos de lei complementar, que será aplicada se outra não houver sido estabelecida pelo próprio ente federativo;”
- `ADCT.art125`: “Art. 125. Em 2026, o imposto previsto no art. 156-A será cobrado à alíquota estadual de 0,1% (um décimo por cento), e a contribuição prevista no art. 195, V, ambos da Constituição Federal, será cobrada à alíquota de 0,9% (nove décimos por cento).”

**Justificativa:** O corpus não traz uma lista com a alíquota própria de cada município. Ele estabelece que cada ente federativo fixa sua alíquota própria por lei específica, uniforme para as operações, e que o IBS é cobrado pelo somatório das alíquotas do Estado e do Município de destino. Também prevê alíquota de referência fixada pelo Senado para cada esfera federativa, aplicável se o ente não estabelecer a sua. Para a data de referência, o ADCT indica apenas a alíquota estadual de 0,1% em 2026, sem informar alíquotas municipais individualizadas.

**Decisão:** confirmar 

---

## c012 · H1

**Pergunta:** A reforma criou imposto sobre grandes fortunas?

**Existe resposta no corpus:** `nao`

**Dispositivos esperados:** nenhum

**Justificativa:** Não há, no corpus, dispositivo que institua ou discipline imposto sobre grandes fortunas. Os dispositivos apresentados tratam do IBS, da CBS, do Imposto Seletivo e de outras matérias da reforma, sem previsão de tributação sobre grandes fortunas. Portanto, o corpus não responde afirmativamente à pergunta.

**Decisão:** confirmar

---

## c013 · H2

**Pergunta:** A partir de quando o ICMS deixa de existir com a reforma?

**Existe resposta no corpus:** `sim`

**Dispositivos esperados:** `ADCT.art129` (ADCT, art. 129)

**Trechos citados (literais do corpus):**

- `ADCT.art129`: “Art. 129. Ficam extintos, a partir de 2033, os impostos previstos nos arts. 155, II, e 156, III, da Constituição Federal.”

**Justificativa:** O dispositivo fixa expressamente a extinção, a partir de 2033, dos impostos previstos nos arts. 155, II, e 156, III, da Constituição Federal. O ICMS é o imposto estadual referido no art. 155, II. Portanto, na data de referência, a extinção ainda não ocorreu e está prevista para começar em 2033.

**Decisão:** confirmar

---

## c014 · H2

**Pergunta:** Como vai funcionar o cashback de impostos para famílias de baixa renda?

**Existe resposta no corpus:** `parcial`

**Dispositivos esperados:** `CF.art156-A.par5.incVIII` (CF, art. 156-A, § 5º, VIII); `CF.art156-A.par13` (CF, art. 156-A, § 13); `CF.art195.par18` (CF, art. 195, § 18); `CF.art195.par16` (CF, art. 195, § 16)

**Trechos citados (literais do corpus):**

- `CF.art156-A.par5.incVIII`: “VIII - as hipóteses de devolução do imposto a pessoas físicas, inclusive os limites e os beneficiários, com o objetivo de reduzir as desigualdades de renda;”
- `CF.art156-A.par13`: “§ 13. A devolução de que trata o § 5º, VIII, será obrigatória nas operações de fornecimento de energia elétrica e de gás liquefeito de petróleo ao consumidor de baixa renda, podendo a lei complementar determinar que seja calculada e concedida no momento da cobrança da operação.”
- `CF.art195.par18`: “§ 18. Lei estabelecerá as hipóteses de devolução da contribuição prevista no inciso V do caput a pessoas físicas, inclusive em relação a limites e beneficiários, com o objetivo de reduzir as desigualdades de renda.”
- `CF.art195.par16`: “§ 16. Aplica-se à contribuição prevista no inciso V do caput o disposto no art. 156-A, § 1º, I a VI, VIII, X a XIII, § 3º, § 5º, II a VI e IX, e §§ 6º a 11 e 13.”

**Justificativa:** O corpus prevê que lei complementar disporá sobre as hipóteses de devolução do IBS a pessoas físicas, incluindo limites e beneficiários, para reduzir desigualdades de renda. Também estabelece que essa devolução será obrigatória no fornecimento de energia elétrica e gás liquefeito de petróleo ao consumidor de baixa renda, podendo ser calculada e concedida no momento da cobrança. Para a CBS, a lei deverá estabelecer hipóteses de devolução a pessoas físicas, e aplica-se a ela o disposto no art. 156-A, § 13. Porém, o corpus não detalha os critérios operacionais completos do cashback, como faixas de renda, valores e forma de pagamento, pois remete esses pontos à lei.

**Decisão:** confirmar

---

## c015 · H2

**Pergunta:** Como fica o PIS/Cofins com a reforma?

**Existe resposta no corpus:** `sim` ⚠️ diverge do palpite da criação (parcial)

**Dispositivos esperados:** `ADCT.art125` (ADCT, art. 125); `ADCT.art125.par1` (ADCT, art. 125, § 1º); `ADCT.art126` (ADCT, art. 126); `ADCT.art126.incI.alia` (ADCT, art. 126, I, a); `ADCT.art126.incII` (ADCT, art. 126, II)

**Trechos citados (literais do corpus):**

- `ADCT.art125`: “Em 2026, o imposto previsto no art. 156-A será cobrado à alíquota estadual de 0,1% (um décimo por cento), e a contribuição prevista no art. 195, V, ambos da Constituição Federal, será cobrada à alíquota de 0,9% (nove décimos por cento).”
- `ADCT.art125.par1`: “§ 1º O montante recolhido na forma do caput será compensado com o valor devido das contribuições previstas no art. 195, I, "b", e IV, e da contribuição para o Programa de Integração Social a que se refere o art. 239, ambos da Constituição Federal.”
- `ADCT.art126`: “A partir de 2027:”
- `ADCT.art126.incI.alia`: “a) a contribuição prevista no art. 195, V, da Constituição Federal;”
- `ADCT.art126.incII`: “II - serão extintas as contribuições previstas no art. 195, I, "b", e IV, e a contribuição para o Programa de Integração Social de que trata o art. 239, todos da Constituição Federal, desde que instituída a contribuição referida na alínea "a" do inciso I;”

**Justificativa:** O art. 125 fixa que, em 2026, a contribuição do art. 195, V é cobrada à alíquota de 0,9%, e o § 1º determina que o valor recolhido seja compensado com as contribuições do art. 195, I, "b" e IV, e com o PIS do art. 239. O art. 126, II, prevê a extinção dessas contribuições a partir de 2027, condicionada à instituição da nova contribuição referida no inciso I, "a". Assim, em 2026 o PIS/Cofins ainda convive com o novo tributo, mas a partir de 2027 é extinto.

**Decisão:** confirmar

---

## c016 · H2

**Pergunta:** O que é split payment?

**Existe resposta no corpus:** `nao` ⚠️ diverge do palpite da criação (parcial)

**Dispositivos esperados:** nenhum

**Justificativa:** O corpus não contém a expressão 'split payment' nem apresenta uma definição do instituto. Há dispositivos sobre recolhimento do imposto e liquidação financeira, mas eles não definem o termo nem permitem, sem conhecimento externo, afirmar que se trata do split payment. Portanto, com base exclusivamente no corpus, a pergunta não é respondida.

**Decisão:** mudar: answer_exists parcial, dispositivo CF.art156-A.par5.incII.alib (o teste de vocabulário de H2 exige mapear split payment para o recolhimento na liquidação financeira)

---

## c017 · H2

**Pergunta:** A reforma cria um imposto único?

**Existe resposta no corpus:** `sim` ⚠️ diverge do palpite da criação (parcial)

**Dispositivos esperados:** `CF.art156-A` (CF, art. 156-A); `CF.art195.incV` (CF, art. 195, V); `CF.art149-B` (CF, art. 149-B)

**Trechos citados (literais do corpus):**

- `CF.art156-A`: “Lei complementar instituirá imposto sobre bens e serviços de competência compartilhada entre Estados, Distrito Federal e Municípios.”
- `CF.art195.incV`: “V - sobre bens e serviços, nos termos de lei complementar.”
- `CF.art149-B`: “Art. 149-B. Os tributos previstos nos arts. 156-A e 195, V, observarão as mesmas regras em relação a:”

**Justificativa:** O corpus mostra que a reforma institui um imposto sobre bens e serviços de competência compartilhada entre Estados, Distrito Federal e Municípios (art. 156-A) e, separadamente, uma contribuição sobre bens e serviços (art. 195, V). O art. 149-B refere-se expressamente a “tributos” previstos nesses dois dispositivos, ainda que sujeitos às mesmas regras. Portanto, não se trata de um imposto único, mas de tributos distintos.

**Decisão:** confirmar 

---

## c018 · H2

**Pergunta:** O IVA dual é composto por quais tributos?

**Existe resposta no corpus:** `sim`

**Dispositivos esperados:** `CF.art156-A` (CF, art. 156-A); `CF.art195.incV` (CF, art. 195, V)

**Trechos citados (literais do corpus):**

- `CF.art156-A`: “Art. 156-A. Lei complementar instituirá imposto sobre bens e serviços de competência compartilhada entre Estados, Distrito Federal e Municípios.”
- `CF.art195.incV`: “V - sobre bens e serviços, nos termos de lei complementar.”

**Justificativa:** O corpus identifica o imposto sobre bens e serviços, previsto no art. 156-A da Constituição Federal, e a contribuição sobre bens e serviços, prevista no art. 195, V. Esses são os dois tributos que compõem o sistema dual indicado na pergunta. A LC 214/2025 refere-se a eles como IBS e CBS.

**Decisão:** confirmar

---

## c019 · H2

**Pergunta:** O que é o IBS e quais impostos ele vai substituir?

**Existe resposta no corpus:** `sim`

**Dispositivos esperados:** `CF.art156-A` (CF, art. 156-A); `ADCT.art129` (ADCT, art. 129)

**Trechos citados (literais do corpus):**

- `CF.art156-A`: “Lei complementar instituirá imposto sobre bens e serviços de competência compartilhada entre Estados, Distrito Federal e Municípios.”
- `ADCT.art129`: “Ficam extintos, a partir de 2033, os impostos previstos nos arts. 155, II, e 156, III, da Constituição Federal.”

**Justificativa:** O IBS é definido pelo art. 156-A como o imposto sobre bens e serviços de competência compartilhada entre Estados, Distrito Federal e Municípios. O art. 129 do ADCT determina a extinção, a partir de 2033, dos impostos previstos nos arts. 155, II, e 156, III, da Constituição Federal, que são os tributos substituídos pelo IBS.

**Decisão:** confirmar

---

## c020 · H2

**Pergunta:** A partir de quando a CBS começa a ser cobrada?

**Existe resposta no corpus:** `sim`

**Dispositivos esperados:** `ADCT.art125` (ADCT, art. 125)

**Trechos citados (literais do corpus):**

- `ADCT.art125`: “Em 2026, o imposto previsto no art. 156-A será cobrado à alíquota estadual de 0,1% (um décimo por cento), e a contribuição prevista no art. 195, V, ambos da Constituição Federal, será cobrada à alíquota de 0,9% (nove décimos por cento).”

**Justificativa:** O dispositivo fixa expressamente a cobrança, em 2026, da contribuição prevista no art. 195, V, à alíquota de 0,9%. A data de referência está dentro do período de efeitos dessa regra, iniciado em 2023-12-21. Assim, segundo o corpus, a CBS começa a ser cobrada em 2026.

**Decisão:** confirmar

---

## c021 · H2

**Pergunta:** O que acontece com o ICMS na transição de 2029 a 2032?

**Existe resposta no corpus:** `sim`

**Dispositivos esperados:** `ADCT.art128` (ADCT, art. 128); `ADCT.art128.incI` (ADCT, art. 128, I); `ADCT.art128.incII` (ADCT, art. 128, II); `ADCT.art128.incIII` (ADCT, art. 128, III); `ADCT.art128.incIV` (ADCT, art. 128, IV)

**Trechos citados (literais do corpus):**

- `ADCT.art128`: “Art. 128. De 2029 a 2032, as alíquotas dos impostos previstos nos arts. 155, II, e 156, III, da Constituição Federal, serão fixadas nas seguintes proporções das alíquotas fixadas nas respectivas legislações:”
- `ADCT.art128.incI`: “I - 9/10 (nove décimos), em 2029;”
- `ADCT.art128.incII`: “II - 8/10 (oito décimos), em 2030;”
- `ADCT.art128.incIII`: “III - 7/10 (sete décimos), em 2031;”
- `ADCT.art128.incIV`: “IV - 6/10 (seis décimos), em 2032.”

**Justificativa:** O art. 128 do ADCT determina que, de 2029 a 2032, as alíquotas do ICMS, previsto no art. 155, II, da Constituição Federal, sejam fixadas em proporções das alíquotas previstas nas respectivas legislações. Os incisos escalonam essa proporção: 9/10 em 2029, 8/10 em 2030, 7/10 em 2031 e 6/10 em 2032. Portanto, no período, o ICMS não é extinto, mas tem suas alíquotas reduzidas anualmente até 6/10 em 2032.

**Decisão:** confirmar

---

## c022 · H2

**Pergunta:** O ISS será substituído pelo IBS?

**Existe resposta no corpus:** `sim`

**Dispositivos esperados:** `ADCT.art129` (ADCT, art. 129); `CF.art156-A` (CF, art. 156-A); `ADCT.art128` (ADCT, art. 128)

**Trechos citados (literais do corpus):**

- `ADCT.art129`: “Art. 129. Ficam extintos, a partir de 2033, os impostos previstos nos arts. 155, II, e 156, III, da Constituição Federal.”
- `CF.art156-A`: “Art. 156-A. Lei complementar instituirá imposto sobre bens e serviços de competência compartilhada entre Estados, Distrito Federal e Municípios.”
- `ADCT.art128`: “Art. 128. De 2029 a 2032, as alíquotas dos impostos previstos nos arts. 155, II, e 156, III, da Constituição Federal, serão fixadas nas seguintes proporções das alíquotas fixadas nas respectivas legislações:”

**Justificativa:** O corpus não usa a sigla ISS, mas prevê a extinção, a partir de 2033, do imposto indicado no art. 156, III, que é o tributo municipal em questão. O art. 156-A institui o IBS, de competência compartilhada entre Estados, Distrito Federal e Municípios. Na data de referência, 2026-11-13, essa extinção ainda não ocorreu; de 2029 a 2032 há apenas a fixação gradual das alíquotas do imposto do art. 156, III. Portanto, a substituição está prevista para 2033, não para a data consultada.

**Decisão:** confirmar

---

## c023 · H2

**Pergunta:** Até quando as empresas continuam pagando PIS e Cofins?

**Existe resposta no corpus:** `sim`

**Dispositivos esperados:** `ADCT.art126` (ADCT, art. 126); `ADCT.art126.incII` (ADCT, art. 126, II)

**Trechos citados (literais do corpus):**

- `ADCT.art126`: “Art. 126. A partir de 2027:”
- `ADCT.art126.incII`: “II - serão extintas as contribuições previstas no art. 195, I, "b", e IV, e a contribuição para o Programa de Integração Social de que trata o art. 239, todos da Constituição Federal, desde que instituída a contribuição referida na alínea "a" do inciso I;”

**Justificativa:** O caput do art. 126 do ADCT fixa o marco temporal: "A partir de 2027". O inciso II determina que serão extintas as contribuições do art. 195, I, "b", e IV, e a contribuição para o PIS do art. 239, desde que instituída a CBS. Como a data de referência é 13/11/2026, as empresas ainda estão no período anterior a essa extinção, que passa a valer no início de 2027.

**Decisão:** confirmar

---

## c024 · H2

**Pergunta:** O que é o chamado imposto do pecado criado na reforma tributária?

**Existe resposta no corpus:** `sim`

**Dispositivos esperados:** `CF.art153.incVIII` (CF, art. 153, VIII); `LC214.art422` (LC 214/2025, art. 422); `ADCT.art126.incI.alib` (ADCT, art. 126, I, b)

**Trechos citados (literais do corpus):**

- `CF.art153.incVIII`: “VIII - produção, extração, comercialização ou importação de bens e serviços prejudiciais à saúde ou ao meio ambiente, nos termos de lei complementar.”
- `LC214.art422`: “as alíquotas do Imposto Seletivo aplicáveis nas operações com os bens e os serviços referidos no Anexo XVII são aquelas previstas em lei ordinária.”
- `ADCT.art126.incI.alib`: “b) o imposto previsto no art. 153, VIII, da Constituição Federal;”

**Justificativa:** O corpus não registra a expressão 'imposto do pecado', mas define o tributo correspondente como o imposto sobre produção, extração, comercialização ou importação de bens e serviços prejudiciais à saúde ou ao meio ambiente. A LC 214/2025 usa a denominação 'Imposto Seletivo' ao tratar de suas alíquotas. O ADCT prevê que o imposto do art. 153, VIII, será cobrado a partir de 2027; por isso, em 13/11/2026, ele já está criado, mas ainda não é cobrado.

**Decisão:** confirmar

---

## c025 · H3

**Pergunta:** A redução de 60% para serviços de saúde vale para quais tributos?

**Existe resposta no corpus:** `sim`

**Dispositivos esperados:** `LC214.art130` (LC 214/2025, art. 130)

**Trechos citados (literais do corpus):**

- `LC214.art130`: “Ficam reduzidas em 60% (sessenta por cento) as alíquotas do IBS e da CBS incidentes sobre o fornecimento dos serviços de saúde relacionados no Anexo III desta Lei Complementar”

**Justificativa:** O dispositivo aplicável na data de referência reduz em 60% as alíquotas incidentes sobre o fornecimento dos serviços de saúde relacionados no Anexo III da LC 214/2025. Ele nomeia expressamente os tributos alcançados: IBS e CBS. Portanto, a redução de 60% para serviços de saúde vale para esses dois tributos.

**Decisão:** confirmar

---

## c026 · H3

**Pergunta:** A alíquota zero da cesta básica também alcança o Imposto Seletivo?

**Existe resposta no corpus:** `sim` ⚠️ diverge do palpite da criação (parcial)

**Dispositivos esperados:** `EC132.art8.parunico` (EC 132/2023, art. 8º, parágrafo único); `LC214.art125` (LC 214/2025, art. 125)

**Trechos citados (literais do corpus):**

- `EC132.art8.parunico`: “Lei complementar definirá os produtos destinados à alimentação humana que comporão a Cesta Básica Nacional de Alimentos, sobre os quais as alíquotas dos tributos previstos nos arts. 156-A e 195, V, da Constituição Federal serão reduzidas a zero.”
- `LC214.art125`: “Ficam reduzidas a zero as alíquotas do IBS e da CBS incidentes sobre as vendas de produtos destinados à alimentação humana relacionados no Anexo I desta Lei Complementar”

**Justificativa:** A EC 132/2023, art. 8º, parágrafo único, ao criar a Cesta Básica Nacional de Alimentos, determina a redução a zero apenas das alíquotas dos tributos previstos nos arts. 156-A e 195, V, da Constituição Federal, que correspondem ao IBS e à CBS. A LC 214/2025, art. 125, repete a limitação ao prever alíquota zero somente do IBS e da CBS sobre os produtos do Anexo I. Não há, nesses dispositivos, extensão da alíquota zero ao Imposto Seletivo.

**Decisão:** confirmar

---

## c027 · H3

**Pergunta:** A imunidade para templos religiosos vale para o IBS e para o Imposto Seletivo?

**Existe resposta no corpus:** `sim` ⚠️ diverge do palpite da criação (parcial)

**Dispositivos esperados:** `CF.art149-B.parunico` (CF, art. 149-B, parágrafo único); `CF.art150.incVI.alib` (CF, art. 150, VI, b); `CF.art153.incVIII` (CF, art. 153, VIII)

**Trechos citados (literais do corpus):**

- `CF.art149-B.parunico`: “Parágrafo único. Os tributos de que trata o caput observarão as imunidades previstas no art. 150, VI, não se aplicando a ambos os tributos o disposto no art. 195, § 7º.”
- `CF.art150.incVI.alib`: “b) entidades religiosas e templos de qualquer culto, inclusive suas organizações assistenciais e beneficentes;”
- `CF.art153.incVIII`: “VIII - produção, extração, comercialização ou importação de bens e serviços prejudiciais à saúde ou ao meio ambiente, nos termos de lei complementar.”

**Justificativa:** O art. 150, VI, b, da Constituição prevê a imunidade para entidades religiosas e templos de qualquer culto. O art. 149-B, parágrafo único, determina que os tributos de que trata o caput — entre eles o IBS — observem as imunidades do art. 150, VI. O Imposto Seletivo é o imposto previsto no art. 153, VIII, e, como a imunidade do art. 150, VI, b é dirigida a impostos e o corpus não traz exceção para o IS, ela também o alcança.

**Decisão:** confirmar 

---

## c028 · H3

**Pergunta:** O Imposto Seletivo dá direito a créditos tributários como acontece no IBS?

**Existe resposta no corpus:** `sim`

**Dispositivos esperados:** `CF.art153.par6.incII` (CF, art. 153, § 6º, II); `CF.art156-A.par1.incVIII` (CF, art. 156-A, § 1º, VIII)

**Trechos citados (literais do corpus):**

- `CF.art153.par6.incII`: “incidirá uma única vez sobre o bem ou serviço”
- `CF.art156-A.par1.incVIII`: “será não cumulativo, compensando-se o imposto devido pelo contribuinte com o montante cobrado sobre todas as operações nas quais seja adquirente de bem material ou imaterial, inclusive direito, ou de serviço”

**Justificativa:** O art. 156-A, § 1º, VIII, assegura ao IBS a não cumulatividade, com compensação do imposto devido pelo montante cobrado nas operações anteriores. Já o regime constitucional do Imposto Seletivo, no art. 153, § 6º, II, prevê incidência única sobre o bem ou serviço, sem regra de creditamento equivalente no corpus. Por isso, o Imposto Seletivo não dá direito a créditos como acontece no IBS.

**Decisão:** confirmar

---

## c029 · H3

**Pergunta:** As exportações de mercadorias pagam IBS e CBS ou são imunes aos dois tributos?

**Existe resposta no corpus:** `sim`

**Dispositivos esperados:** `CF.art156-A.par1.incIII` (CF, art. 156-A, § 1º, III); `CF.art195.par16` (CF, art. 195, § 16)

**Trechos citados (literais do corpus):**

- `CF.art156-A.par1.incIII`: “III - não incidirá sobre as exportações, assegurados ao exportador a manutenção e o aproveitamento dos créditos relativos às operações nas quais seja adquirente de bem material ou imaterial, inclusive direitos, ou serviço, observado o disposto no § 5º, III;”
- `CF.art195.par16`: “§ 16. Aplica-se à contribuição prevista no inciso V do caput o disposto no art. 156-A, § 1º, I a VI, VIII, X a XIII, § 3º, § 5º, II a VI e IX, e §§ 6º a 11 e 13.”

**Justificativa:** O corpus prevê que o IBS não incidirá sobre as exportações, assegurados ao exportador a manutenção e o aproveitamento dos créditos. O art. 195, § 16, determina que esse mesmo conjunto de regras do art. 156-A, § 1º, inclui o inciso III, aplicando-se também à CBS. Assim, na data de referência, as exportações de mercadorias não pagam IBS nem CBS; trata-se de não incidência, não de imunidade.

**Decisão:** confirmar

---

## c030 · H3

**Pergunta:** O cashback de tributos para famílias de baixa renda devolve tanto o IBS quanto a CBS?

**Existe resposta no corpus:** `sim`

**Dispositivos esperados:** `CF.art156-A.par5.incVIII` (CF, art. 156-A, § 5º, VIII); `CF.art195.par18` (CF, art. 195, § 18); `CF.art156-A.par13` (CF, art. 156-A, § 13); `CF.art195.par16` (CF, art. 195, § 16)

**Trechos citados (literais do corpus):**

- `CF.art156-A.par5.incVIII`: “VIII - as hipóteses de devolução do imposto a pessoas físicas, inclusive os limites e os beneficiários, com o objetivo de reduzir as desigualdades de renda;”
- `CF.art195.par18`: “§ 18. Lei estabelecerá as hipóteses de devolução da contribuição prevista no inciso V do caput a pessoas físicas, inclusive em relação a limites e beneficiários, com o objetivo de reduzir as desigualdades de renda.”
- `CF.art156-A.par13`: “§ 13. A devolução de que trata o § 5º, VIII, será obrigatória nas operações de fornecimento de energia elétrica e de gás liquefeito de petróleo ao consumidor de baixa renda, podendo a lei complementar determinar que seja calculada e concedida no momento da cobrança da operação.”
- `CF.art195.par16`: “§ 16. Aplica-se à contribuição prevista no inciso V do caput o disposto no art. 156-A, § 1º, I a VI, VIII, X a XIII, § 3º, § 5º, II a VI e IX, e §§ 6º a 11 e 13.”

**Justificativa:** O corpus prevê expressamente a devolução do imposto (IBS) a pessoas físicas, com limites e beneficiários, para reduzir desigualdades de renda, e disposição equivalente para a contribuição do art. 195, V (CBS). Além disso, a devolução do IBS é obrigatória para energia elétrica e GLP ao consumidor de baixa renda, e o art. 195, § 16, estende à CBS o disposto no art. 156-A, § 13. Todos esses dispositivos já produzem efeitos em 13/11/2026. Portanto, o cashback alcança tanto o IBS quanto a CBS.

**Decisão:** confirmar

---

## c031 · H4

**Pergunta:** Em 2026 o IBS já é cobrado de verdade ou é só um teste?

**Existe resposta no corpus:** `sim`

**Dispositivos esperados:** `ADCT.art125` (ADCT, art. 125); `ADCT.art125.par4` (ADCT, art. 125, § 4º)

**Trechos citados (literais do corpus):**

- `ADCT.art125`: “Em 2026, o imposto previsto no art. 156-A será cobrado à alíquota estadual de 0,1% (um décimo por cento)”
- `ADCT.art125.par4`: “Durante o período de que trata o caput, os sujeitos passivos que cumprirem as obrigações acessórias relativas aos tributos referidos no caput poderão ser dispensados do seu recolhimento, nos termos de lei complementar.”

**Justificativa:** O corpus prevê expressamente que, em 2026, o IBS (imposto previsto no art. 156-A) será cobrado à alíquota estadual de 0,1%. Contudo, no mesmo período, o § 4º permite que os sujeitos passivos que cumprirem as obrigações acessórias sejam dispensados do recolhimento, nos termos de lei complementar. Assim, há previsão de cobrança em 2026, mas em formato de teste, com alíquota reduzida e possibilidade de dispensa do efetivo recolhimento.

**Decisão:** confirmar

---

## c032 · H4

**Pergunta:** A partir de que ano a CBS passa a ser cobrada integralmente?

**Existe resposta no corpus:** `sim` ⚠️ diverge do palpite da criação (parcial)

**Dispositivos esperados:** `ADCT.art125` (ADCT, art. 125); `ADCT.art126` (ADCT, art. 126); `ADCT.art126.incI` (ADCT, art. 126, I); `ADCT.art126.incI.alia` (ADCT, art. 126, I, a); `ADCT.art127` (ADCT, art. 127); `ADCT.art127.parunico` (ADCT, art. 127, parágrafo único)

**Trechos citados (literais do corpus):**

- `ADCT.art125`: “Art. 125. Em 2026, o imposto previsto no art. 156-A será cobrado à alíquota estadual de 0,1% (um décimo por cento), e a contribuição prevista no art. 195, V, ambos da Constituição Federal, será cobrada à alíquota de 0,9% (nove décimos por cento).”
- `ADCT.art126`: “Art. 126. A partir de 2027:”
- `ADCT.art126.incI`: “I - serão cobrados:”
- `ADCT.art126.incI.alia`: “a) a contribuição prevista no art. 195, V, da Constituição Federal;”
- `ADCT.art127`: “Art. 127. Em 2027 e 2028, o imposto previsto no art. 156-A da Constituição Federal será cobrado à alíquota estadual de 0,05% (cinco centésimos por cento) e à alíquota municipal de 0,05% (cinco centésimos por cento).”
- `ADCT.art127.parunico`: “Parágrafo único. No período referido no caput, a alíquota da contribuição prevista no art. 195, V, da Constituição Federal, será reduzida em 0,1 (um décimo) ponto percentual.”

**Justificativa:** O art. 125 fixa a CBS em 0,9% em 2026. O art. 126 determina que a contribuição do art. 195, V seja cobrada a partir de 2027, mas o art. 127, parágrafo único, reduz sua alíquota em 0,1 ponto percentual em 2027 e 2028. Assim, após esse período de redução, a CBS passa a ser cobrada integralmente a partir de 2029.

**Decisão:** confirmar 

---

## c033 · H4

**Pergunta:** A partir de que ano o Imposto Seletivo começa a ser cobrado?

**Existe resposta no corpus:** `sim`

**Dispositivos esperados:** `ADCT.art126` (ADCT, art. 126); `ADCT.art126.incI.alib` (ADCT, art. 126, I, b)

**Trechos citados (literais do corpus):**

- `ADCT.art126`: “Art. 126. A partir de 2027:”
- `ADCT.art126.incI.alib`: “b) o imposto previsto no art. 153, VIII, da Constituição Federal;”

**Justificativa:** O art. 126 do ADCT fixa o marco temporal “A partir de 2027”. A alínea b do inciso I desse artigo inclui, entre os tributos a serem cobrados nesse marco, o imposto previsto no art. 153, VIII, da Constituição Federal. Como a data de referência é 13/11/2026, a cobrança ainda não começou nessa data e tem início em 2027.

**Decisão:** confirmar

---

## c034 · H4

**Pergunta:** A redução de 60% para serviços de saúde e educação já vale na fase de teste em 2026?

**Existe resposta no corpus:** `sim`

**Dispositivos esperados:** `ADCT.art125` (ADCT, art. 125); `LC214.art128` (LC 214/2025, art. 128); `LC214.art128.incI` (LC 214/2025, art. 128, I); `LC214.art128.incII` (LC 214/2025, art. 128, II)

**Trechos citados (literais do corpus):**

- `ADCT.art125`: “Em 2026, o imposto previsto no art. 156-A será cobrado à alíquota estadual de 0,1% (um décimo por cento), e a contribuição prevista no art. 195, V, ambos da Constituição Federal, será cobrada à alíquota de 0,9% (nove décimos por cento).”
- `LC214.art128`: “ficam reduzidas em 60% (sessenta por cento) as alíquotas do IBS e da CBS incidentes sobre operações com:”
- `LC214.art128.incI`: “I - serviços de educação;”
- `LC214.art128.incII`: “II - serviços de saúde;”

**Justificativa:** O corpus indica que 2026 é o período de cobrança em alíquotas reduzidas de teste, com IBS a 0,1% e CBS a 0,9%. A LC 214/2025 estabelece redução de 60% das alíquotas do IBS e da CBS para operações com serviços de educação e de saúde. Como os efeitos desses dispositivos começam em 2026-01-01, a redução já alcança a data de referência de 2026-11-13.

**Decisão:** confirmar

---

## c035 · H4

**Pergunta:** A transição de 50 anos para distribuir o IBS pelo destino começa a valer a partir de que ano?

**Existe resposta no corpus:** `sim`

**Dispositivos esperados:** `ADCT.art131` (ADCT, art. 131)

**Trechos citados (literais do corpus):**

- `ADCT.art131`: “De 2029 a 2077, o produto da arrecadação dos Estados, do Distrito Federal e dos Municípios com o imposto de que trata o art. 156-A da Constituição Federal será distribuído a esses entes federativos conforme o disposto neste artigo.”

**Justificativa:** O corpus fixa expressamente que a distribuição do produto da arrecadação do IBS aos entes federativos ocorre de 2029 a 2077. Portanto, a transição começa a valer em 2029. Na data de referência, 13/11/2026, esse dispositivo já está em vigor, pois seus efeitos foram fixados desde 21/12/2023.

**Decisão:** confirmar

---

## c036 · H4

**Pergunta:** Em qual ano começa a redução gradual do ICMS e do ISS para a entrada do IBS?

**Existe resposta no corpus:** `sim`

**Dispositivos esperados:** `ADCT.art128` (ADCT, art. 128); `ADCT.art128.incI` (ADCT, art. 128, I)

**Trechos citados (literais do corpus):**

- `ADCT.art128`: “Art. 128. De 2029 a 2032, as alíquotas dos impostos previstos nos arts. 155, II, e 156, III, da Constituição Federal, serão fixadas nas seguintes proporções das alíquotas fixadas nas respectivas legislações:”
- `ADCT.art128.incI`: “I - 9/10 (nove décimos), em 2029;”

**Justificativa:** O art. 128 do ADCT estabelece que a redução gradual das alíquotas dos impostos previstos nos arts. 155, II, e 156, III, ocorre de 2029 a 2032. O inciso I confirma que em 2029 a alíquota será fixada em 9/10 da alíquota de referência. Portanto, o ano de início da redução gradual é 2029.

**Decisão:** confirmar

---

## c037 · H4

**Pergunta:** Em 2030, qual percentual das alíquotas do ICMS e do ISS ainda se aplica?

**Existe resposta no corpus:** `sim`

**Dispositivos esperados:** `ADCT.art128` (ADCT, art. 128); `ADCT.art128.incII` (ADCT, art. 128, II)

**Trechos citados (literais do corpus):**

- `ADCT.art128`: “De 2029 a 2032, as alíquotas dos impostos previstos nos arts. 155, II, e 156, III, da Constituição Federal, serão fixadas nas seguintes proporções das alíquotas fixadas nas respectivas legislações:”
- `ADCT.art128.incII`: “II - 8/10 (oito décimos), em 2030;”

**Justificativa:** O art. 128 do ADCT estabelece, de 2029 a 2032, proporções das alíquotas dos impostos previstos nos arts. 155, II, e 156, III, da Constituição Federal. Para 2030, o inciso II fixa a proporção em 8/10 (oito décimos). Portanto, em 2030 aplica-se o equivalente a 80% das alíquotas desses impostos.

**Decisão:** confirmar

---

## c038 · H4

**Pergunta:** A partir de 2029 o IBS já substitui totalmente o ICMS?

**Existe resposta no corpus:** `sim` ⚠️ diverge do palpite da criação (parcial)

**Dispositivos esperados:** `ADCT.art128` (ADCT, art. 128); `ADCT.art129` (ADCT, art. 129)

**Trechos citados (literais do corpus):**

- `ADCT.art128`: “Art. 128. De 2029 a 2032, as alíquotas dos impostos previstos nos arts. 155, II, e 156, III, da Constituição Federal, serão fixadas nas seguintes proporções das alíquotas fixadas nas respectivas legislações:”
- `ADCT.art129`: “Art. 129. Ficam extintos, a partir de 2033, os impostos previstos nos arts. 155, II, e 156, III, da Constituição Federal.”

**Justificativa:** A resposta é não. O art. 128 do ADCT mantém, de 2029 a 2032, a cobrança dos impostos previstos nos arts. 155, II, e 156, III, com alíquotas fixadas em proporções das alíquotas legais. O art. 129 do ADCT só extingue esses impostos a partir de 2033. Portanto, em 2029 não há substituição total do ICMS pelo IBS.

**Decisão:** confirmar 

---

## c039 · H4

**Pergunta:** Até quando os estados podem cobrar o adicional de ICMS para os fundos de combate à pobreza?

**Existe resposta no corpus:** `sim`

**Dispositivos esperados:** `EC132.art22.incII` (EC 132/2023, art. 22, II); `EC132.art22.incII.alib` (EC 132/2023, art. 22, II, b)

**Trechos citados (literais do corpus):**

- `EC132.art22.incII`: “II - em 2033:”
- `EC132.art22.incII.alib`: “b) os arts. 80, II, 82, § 2º, e 83 do Ato das Disposições Constitucionais Transitórias.”

**Justificativa:** A EC 132/2023 determina que, em 2033, serão revogados os arts. 80, II, 82, § 2º, e 83 do ADCT. Como o dispositivo tem efeitos desde 2023, essa previsão já pode ser considerada na data de referência. Portanto, a cobrança do adicional vinculado ao art. 82, § 2º, do ADCT pode ocorrer até 2032, pois a partir de 2033 o dispositivo é revogado.

**Decisão:** confirmar

---

## c040 · H4

**Pergunta:** A desvinculação de 30% das receitas estaduais vale até quando?

**Existe resposta no corpus:** `sim`

**Dispositivos esperados:** `ADCT.art76-A` (ADCT, art. 76-A)

**Trechos citados (literais do corpus):**

- `ADCT.art76-A`: “Art. 76-A. São desvinculados de órgão, fundo ou despesa, até 31 de dezembro de 2032, 30% (trinta por cento) das receitas dos Estados e do Distrito Federal relativas a impostos, taxas e multas já instituídos ou que vierem a ser criados até a referida data, seus adicionais e respectivos acréscimos legais, e outras receitas correntes.”

**Justificativa:** O dispositivo aplicável é o art. 76-A do ADCT, que trata da desvinculação de 30% das receitas dos Estados e do Distrito Federal. Ele fixa expressamente o termo final em 31 de dezembro de 2032. Como a data de referência é 2026-11-13, o dispositivo está vigente e responde à pergunta.

**Decisão:** confirmar

---

## c041 · H4

**Pergunta:** O fundo de compensação de benefícios fiscais começa a pagar em que ano?

**Existe resposta no corpus:** `parcial` ⚠️ diverge do palpite da criação (sim)

**Dispositivos esperados:** `ADCT.art125` (ADCT, art. 125); `ADCT.art125.par3` (ADCT, art. 125, § 3º); `ADCT.art125.par3.incII` (ADCT, art. 125, § 3º, II)

**Trechos citados (literais do corpus):**

- `ADCT.art125`: “Em 2026, o imposto previsto no art. 156-A será cobrado à alíquota estadual de 0,1% (um décimo por cento), e a contribuição prevista no art. 195, V, ambos da Constituição Federal, será cobrada à alíquota de 0,9% (nove décimos por cento).”
- `ADCT.art125.par3`: “A arrecadação do imposto previsto no art. 156-A da Constituição Federal decorrente do disposto no caput deste artigo não observará as vinculações, repartições e destinações previstas na Constituição Federal, devendo ser aplicada, integral e sucessivamente, para:”
- `ADCT.art125.par3.incII`: “II - compor o Fundo de Compensação de Benefícios Fiscais ou Financeiro-Fiscais do imposto de que trata o art. 155, II, da Constituição Federal.”

**Justificativa:** O art. 125 fixa que em 2026 o IBS será cobrado à alíquota estadual de 0,1%. O § 3º, II, determina que essa arrecadação seja aplicada para compor o Fundo de Compensação de Benefícios Fiscais ou Financeiro-Fiscais. O corpus, portanto, indica 2026 como ano de composição do fundo, mas não menciona expressamente o início dos pagamentos.

**Decisão:** mudar: answer_exists sim, dispositivos EC132.art12 e EC132.art12.par1 (o art. 12 da EC 132 fixa expressamente que o Fundo compensará beneficiários entre 1º de janeiro de 2029 e 31 de dezembro de 2032, portanto os pagamentos começam em 2029) 

---

## c042 · H4

**Pergunta:** O IBS de 0,1% em 2026 é estadual ou municipal?

**Existe resposta no corpus:** `sim`

**Dispositivos esperados:** `ADCT.art125` (ADCT, art. 125)

**Trechos citados (literais do corpus):**

- `ADCT.art125`: “Em 2026, o imposto previsto no art. 156-A será cobrado à alíquota estadual de 0,1% (um décimo por cento)”

**Justificativa:** O ADCT, art. 125, está com efeitos desde 2023-12-21 e, portanto, alcança a data de referência de 2026-11-13. Ele determina expressamente que, em 2026, o imposto previsto no art. 156-A será cobrado à alíquota estadual de 0,1%. Logo, o IBS de 0,1% em 2026 é estadual, não municipal.

**Decisão:** confirmar

---

## c043 · H5

**Pergunta:** Quais produtos compõem a cesta básica nacional com alíquota zero?

**Existe resposta no corpus:** `parcial`

**Dispositivos esperados:** `LC214.art125` (LC 214/2025, art. 125)

**Trechos citados (literais do corpus):**

- `LC214.art125`: “Ficam reduzidas a zero as alíquotas do IBS e da CBS incidentes sobre as vendas de produtos destinados à alimentação humana relacionados no Anexo I desta Lei Complementar, com a especificação das respectivas classificações da NCM/SH, que compõem a Cesta Básica Nacional de Alimentos”

**Justificativa:** O dispositivo aplicável na data de referência é o art. 125 da LC 214/2025, que reduz a zero as alíquotas do IBS e da CBS sobre produtos destinados à alimentação humana. Ele indica que os produtos são os relacionados no Anexo I da própria lei complementar, com suas classificações NCM/SH, e que compõem a Cesta Básica Nacional de Alimentos. Contudo, o corpus não reproduz o Anexo I, de modo que não é possível enumerar os produtos específicos.

**Decisão:** confirmar

---

## c044 · H5

**Pergunta:** Quais serviços de educação têm redução de 60%?

**Existe resposta no corpus:** `parcial`

**Dispositivos esperados:** `LC214.art129` (LC 214/2025, art. 129)

**Trechos citados (literais do corpus):**

- `LC214.art129`: “Art. 129. Ficam reduzidas em 60% (sessenta por cento) as alíquotas do IBS e da CBS incidentes sobre o fornecimento dos serviços de educação relacionados no Anexo II desta Lei Complementar, com a especificação das respectivas classificações da Nomenclatura Brasileira de Serviços, Intangíveis e Outras Operações que Produzam Variações no Patrimônio (NBS).”

**Justificativa:** O corpus reduz em 60% as alíquotas do IBS e da CBS incidentes sobre o fornecimento dos serviços de educação relacionados no Anexo II da LC 214/2025. Como o Anexo II não está reproduzido no corpus, não é possível identificar a lista concreta dos serviços de educação alcançados. O dispositivo produz efeitos desde 2026-01-01, portanto alcança a data de referência.

**Decisão:** confirmar

---

## c045 · H5

**Pergunta:** Quais dispositivos médicos têm redução de 60% no IBS e na CBS?

**Existe resposta no corpus:** `sim`

**Dispositivos esperados:** `LC214.art131` (LC 214/2025, art. 131); `LC214.art131.par1` (LC 214/2025, art. 131, § 1º)

**Trechos citados (literais do corpus):**

- `LC214.art131`: “Art. 131. Ficam reduzidas em 60% (sessenta por cento) as alíquotas do IBS e da CBS incidentes sobre o fornecimento dos dispositivos médicos relacionados no Anexo IV desta Lei Complementar, com a especificação das respectivas classificações da NCM/SH.”
- `LC214.art131.par1`: “§ 1º A redução de alíquotas prevista no caput deste artigo somente se aplica aos dispositivos listados no Anexo IV desta Lei Complementar regularizados perante a Agência Nacional de Vigilância Sanitária (Anvisa).”

**Justificativa:** A LC 214/2025 reduz em 60% as alíquotas do IBS e da CBS incidentes sobre o fornecimento de dispositivos médicos relacionados no Anexo IV. A redução é condicionada aos dispositivos listados nesse Anexo que estejam regularizados perante a Anvisa. Como os efeitos do art. 131 começam em 2026-01-01, a regra já alcança a data de referência.

**Decisão:** mudar: answer_exists parcial (o art. 131 da LC 214 remete a lista específica de dispositivos médicos ao Anexo IV, que não consta no corpus; resposta é parcial, como em c043, c044, c047 e c048)

---

## c046 · H5

**Pergunta:** Quais medicamentos têm redução de 60%?

**Existe resposta no corpus:** `sim` ⚠️ diverge do palpite da criação (parcial)

**Dispositivos esperados:** `LC214.art133` (LC 214/2025, art. 133); `LC214.art133.par1` (LC 214/2025, art. 133, § 1º); `LC214.art133.par2` (LC 214/2025, art. 133, § 2º)

**Trechos citados (literais do corpus):**

- `LC214.art133`: “Art. 133. Ficam reduzidas em 60% (sessenta por cento) as alíquotas do IBS e da CBS incidentes sobre o fornecimento dos medicamentos registrados na Anvisa ou produzidos por farmácias de manipulação, ressalvados os medicamentos sujeitos à alíquota zero de que trata o art. 146 desta Lei Complementar.”
- `LC214.art133.par1`: “§ 1º A redução de alíquotas prevista no caput deste artigo aplica-se também às operações de fornecimento das composições para nutrição enteral e parenteral, composições especiais e fórmulas nutricionais destinadas às pessoas com erros inatos do metabolismo relacionadas no Anexo VI desta Lei Complementar, com a especificação das respectivas classificações da NCM/SH.”
- `LC214.art133.par2`: “§ 2º Para fins de assegurar a repercussão nos preços da redução da carga tributária, a redução de que trata este artigo somente se aplica aos medicamentos industrializados ou importados pelas pessoas jurídicas que tenham firmado, com a União e o Comitê Gestor do IBS, compromisso de ajustamento de conduta ou cumpram a sistemática estabelecida pela Câmara de Regulação do Mercado de Medicamentos (CMED), na forma da lei.”

**Justificativa:** Na data de referência, o art. 133 da LC 214/2025 reduz em 60% as alíquotas do IBS e da CBS sobre o fornecimento de medicamentos registrados na Anvisa ou produzidos por farmácias de manipulação, ressalvados os medicamentos sujeitos à alíquota zero do art. 146. O § 1º estende a redução às composições para nutrição enteral e parenteral, composições especiais e fórmulas nutricionais destinadas a pessoas com erros inatos do metabolismo relacionadas no Anexo VI. O § 2º condiciona a redução, quanto aos medicamentos industrializados ou importados, às pessoas jurídicas que tenham firmado compromisso de ajustamento de conduta ou cumpram a sistemática da CMED.

**Decisão:** confirmar 

---

## c047 · H5

**Pergunta:** Quais produtos de higiene pessoal e limpeza têm direito à redução de 60% de alíquota?

**Existe resposta no corpus:** `parcial`

**Dispositivos esperados:** `LC214.art128.incVII` (LC 214/2025, art. 128, VII); `LC214.art136` (LC 214/2025, art. 136)

**Trechos citados (literais do corpus):**

- `LC214.art128.incVII`: “VII - produtos de higiene pessoal e limpeza majoritariamente consumidos por famílias de baixa renda;”
- `LC214.art136`: “Art. 136. Ficam reduzidas em 60% (sessenta por cento) as alíquotas do IBS e da CBS incidentes sobre o fornecimento dos produtos de higiene pessoal e limpeza relacionados no Anexo VIII desta Lei Complementar, com a especificação das respectivas classificações da NCM/SH.”

**Justificativa:** A LC 214/2025 prevê redução de 60% para produtos de higiene pessoal e limpeza majoritariamente consumidos por famílias de baixa renda. O art. 136 especifica que a redução alcança os produtos relacionados no Anexo VIII, com suas classificações NCM/SH. Como o corpus não reproduz o Anexo VIII, não é possível enumerar os produtos ou códigos específicos, mas o critério legal e a remissão ao anexo estão presentes. Ambos os dispositivos já produzem efeitos em 2026-11-13.

**Decisão:** confirmar

---

## c048 · H5

**Pergunta:** Quais insumos agropecuários têm redução de alíquota de 60%?

**Existe resposta no corpus:** `parcial`

**Dispositivos esperados:** `LC214.art138` (LC 214/2025, art. 138)

**Trechos citados (literais do corpus):**

- `LC214.art138`: “Ficam reduzidas em 60% (sessenta por cento) as alíquotas do IBS e da CBS incidentes sobre o fornecimento dos insumos agropecuários e aquícolas relacionados no Anexo IX desta Lei Complementar”

**Justificativa:** O corpus reduz em 60% as alíquotas do IBS e da CBS sobre o fornecimento de insumos agropecuários e aquícolas, mas apenas os relacionados no Anexo IX da LC 214/2025. Como o Anexo IX não está reproduzido no corpus, não é possível enumerar os produtos específicos. A resposta fica, portanto, limitada à categoria legal e à remissão ao anexo.

**Decisão:** confirmar

---

## c049 · H6

**Pergunta:** O que a Constituição previa em 2022 sobre o Simples Nacional antes de ser criada a regra do IBS?

**Existe resposta no corpus:** `nao`

**Dispositivos esperados:** nenhum

**Justificativa:** O corpus só contém dispositivos com efeitos a partir de 2023-12-21, já na redação posterior à EC 132/2023. Não há, portanto, texto constitucional com efeitos em 2022 nem versão anterior do art. 146 sobre o Simples Nacional. Com base apenas no corpus, não é possível responder o que a Constituição previa em 2022 sobre o tema.

**Decisão:** confirmar

---

## c050 · H6

**Pergunta:** Em 2022 a Constituição brasileira já previa a cobrança do IBS?

**Existe resposta no corpus:** `sim`

**Dispositivos esperados:** `CF.art156-A` (CF, art. 156-A); `EC132.art1` (EC 132/2023, art. 1º)

**Trechos citados (literais do corpus):**

- `CF.art156-A`: “Art. 156-A. Lei complementar instituirá imposto sobre bens e serviços de competência compartilhada entre Estados, Distrito Federal e Municípios.”
- `EC132.art1`: “Art. 1º A Constituição Federal passa a vigorar com as seguintes alterações:”

**Justificativa:** A resposta é não. O corpus identifica o IBS como o imposto do art. 156-A da Constituição, dispositivo cujos efeitos começam em 2023-12-21. A EC 132/2023, que promoveu as alterações constitucionais, também tem efeitos a partir de 2023-12-21, de modo que em 2022 essa previsão não estava vigente.

**Decisão:** confirmar

---

## c051 · H6

**Pergunta:** Qual era o texto do art. 195, § 17, antes da EC 132/2023?

**Existe resposta no corpus:** `nao`

**Dispositivos esperados:** nenhum

**Justificativa:** O corpus não traz o texto anterior do art. 195, § 17, da Constituição Federal. As únicas versões desse dispositivo aparecem com efeitos a partir de 2023-12-21, ou seja, já após a EC 132/2023, e não há dispositivo que reproduza a redação pretérita. Portanto, não é possível responder qual era o texto antes da EC 132/2023 com base exclusivamente no corpus.

**Decisão:** confirmar

---

## c052 · H6

**Pergunta:** Como era a cobrança da CBS em 2022?

**Existe resposta no corpus:** `nao`

**Dispositivos esperados:** nenhum

**Justificativa:** O corpus não contém dispositivo com efeitos que alcancem 2022 e que descreva a cobrança da CBS naquele ano. Os dispositivos sobre a CBS tratam da transição a partir de 2026 e 2027, sem retroagir para 2022. Assim, não há base no corpus para responder como era a cobrança da CBS em 2022.

**Decisão:** confirmar

---

## c053 · H6

**Pergunta:** Em 2020, o Imposto Seletivo já existia?

**Existe resposta no corpus:** `sim` ⚠️ diverge do palpite da criação (nao)

**Dispositivos esperados:** `CF.art153.incVIII` (CF, art. 153, VIII); `ADCT.art126` (ADCT, art. 126); `ADCT.art126.incI.alib` (ADCT, art. 126, I, b)

**Trechos citados (literais do corpus):**

- `CF.art153.incVIII`: “VIII - produção, extração, comercialização ou importação de bens e serviços prejudiciais à saúde ou ao meio ambiente, nos termos de lei complementar.”
- `ADCT.art126`: “Art. 126. A partir de 2027:”
- `ADCT.art126.incI.alib`: “b) o imposto previsto no art. 153, VIII, da Constituição Federal;”

**Justificativa:** O corpus indica que o imposto previsto no art. 153, VIII, da Constituição Federal só será cobrado a partir de 2027, conforme o art. 126 do ADCT. Além disso, o dispositivo constitucional que o prevê tem efeitos a partir de 21/12/2023. Portanto, em 2020 o Imposto Seletivo ainda não existia.

**Decisão:** confirmar

---

## c054 · H6

**Pergunta:** O que constava no art. 156-A da Constituição no ano de 2022?

**Existe resposta no corpus:** `nao`

**Dispositivos esperados:** nenhum

**Justificativa:** O corpus não contém uma versão do art. 156-A da Constituição com efeitos vigentes em 2022. Todos os dispositivos desse artigo aparecem com efeitos a partir de 2023-12-21, de modo que não respondem ao que constava no referido artigo no ano de 2022. Portanto, com base apenas no corpus, não é possível responder à pergunta.

**Decisão:** confirmar

---

## c055 · H7

**Pergunta:** A exceção do Regime de Tributação Simplificada para remessas internacionais já tem data para valer?

**Existe resposta no corpus:** `sim` ⚠️ diverge do palpite da criação (parcial)

**Dispositivos esperados:** `LC214.art126.par6` (LC 214/2025, art. 126, § 6º)

**Trechos citados (literais do corpus):**

- `LC214.art126.par6`: “O disposto no § 1º deste artigo não se aplica às remessas internacionais sujeitas ao Regime de Tributação Simplificada (RTS), exceto na hipótese de produtos acabados pertencentes a classes de medicamentos importados por pessoa física para uso próprio ou individual.”

**Justificativa:** O corpus registra a exceção no art. 126, § 6º, da LC 214/2025, afastando a aplicação do § 1º às remessas internacionais sujeitas ao RTS. Contudo, esse dispositivo aparece com 'efeitos None..', isto é, sem data de início de efeitos indicada. Na data de referência de 2026-11-13, não há data de vigência prevista para a exceção.

**Decisão:** confirmar

---

## c056 · H7

**Pergunta:** A partir de quando passa a valer a redução de 60% para serviços de segurança da informação prestados por empresa com sócio brasileiro?

**Existe resposta no corpus:** `nao`

**Dispositivos esperados:** nenhum

**Justificativa:** O único dispositivo do corpus que descreve exatamente a redução de 60% para serviços de segurança da informação prestados por sociedade com sócio brasileiro é o art. 142, II, da LC 214/2025. Esse dispositivo, porém, está registrado com efeitos 'None..', de modo que não alcança a data de referência. O caput do art. 142 tem efeitos desde 2026-01-01, mas não responde sozinho pela hipótese específica do inciso II. Assim, o corpus não fornece a data de início dessa redução específica.

**Decisão:** confirmar

---

## c057 · H7

**Pergunta:** Qual é o limite máximo do Imposto Seletivo sobre bens minerais extraídos?

**Existe resposta no corpus:** `sim` ⚠️ diverge do palpite da criação (parcial)

**Dispositivos esperados:** `CF.art153.par6.incVII` (CF, art. 153, § 6º, VII)

**Trechos citados (literais do corpus):**

- `CF.art153.par6.incVII`: “na extração, o imposto será cobrado independentemente da destinação, caso em que a alíquota máxima corresponderá a 1% (um por cento) do valor de mercado do produto.”

**Justificativa:** A CF, art. 153, § 6º, VII, fixa que, na extração, a alíquota máxima do Imposto Seletivo corresponde a 1% do valor de mercado do produto. Esse dispositivo está com efeitos desde 2023-12-21, alcançando a data de referência. A previsão específica de 0,25% para bens minerais extraídos não foi considerada porque o corpus registra seus efeitos como “None..”, fora da data de referência.

**Decisão:** confirmar 

---

## c058 · H7

**Pergunta:** O escalonamento das alíquotas do Imposto Seletivo para bebidas e cigarros entre 2029 e 2033 já está valendo?

**Existe resposta no corpus:** `sim`

**Dispositivos esperados:** `LC214.art422.par5` (LC 214/2025, art. 422, § 5º)

**Trechos citados (literais do corpus):**

- `LC214.art422.par5`: “As alíquotas do Imposto Seletivo incidentes sobre os produtos previstos nos incisos III a V do § 1º do art. 409 desta Lei Complementar serão fixadas de forma escalonada, de modo a incorporar, a partir de 2029 até 2033, progressivamente, o diferencial entre as alíquotas de ICMS incidentes sobre os produtos fumígenos, as bebidas alcoólicas e as bebidas açucaradas e as alíquotas modais desse imposto.”

**Justificativa:** O dispositivo prevê que o escalonamento das alíquotas do Imposto Seletivo para fumígenos e bebidas ocorrerá de forma progressiva entre 2029 e 2033. Como a data de referência é 2026-11-13, esse período ainda não começou. Portanto, o escalonamento não está valendo nessa data.

**Decisão:** confirmar

---

## c059 · H7

**Pergunta:** O que é necessário para que a regra do art. 92-B, § 7º, do ADCT produza efeitos?

**Existe resposta no corpus:** `sim`

**Dispositivos esperados:** `ADCT.art92-B.par7` (ADCT, art. 92-B, § 7º); `ADCT.art92-B.par6` (ADCT, art. 92-B, § 6º)

**Trechos citados (literais do corpus):**

- `ADCT.art92-B.par7`: “§ 7º O Fundo de que trata o § 6º será integrado pelos Estados onde estão localizadas as áreas de livre comércio de que trata ocapute observará, no que couber, o disposto no § 3º, I e II, sendo, quanto a este inciso, considerados os respectivos Estados, e no § 4º.”
- `ADCT.art92-B.par6`: “§ 6º Lei complementar instituirá Fundo de Desenvolvimento Sustentável dos Estados da Amazônia Ocidental e do Amapá, que será constituído com recursos da União e por ela gerido, com a efetiva participação desses Estados na definição das políticas, com o objetivo de fomentar o desenvolvimento e a diversificação de suas atividades econômicas.”

**Justificativa:** O § 7º não cria o fundo; ele disciplina a integração do Fundo de que trata o § 6º e a observância, no que couber, dos §§ 3º, I e II, e 4º. Assim, para que a regra do § 7º tenha objeto e produza efeitos, é necessária a lei complementar prevista no § 6º, que institua o Fundo de Desenvolvimento Sustentável dos Estados da Amazônia Ocidental e do Amapá. Os dispositivos estão com efeitos desde 2023-12-21, alcançando a data de referência.

**Decisão:** confirmar

---

## c060 · H7

**Pergunta:** Quais condições precisam ser cumpridas para ter direito à alíquota zero da cesta básica no art. 125 da LC 214?

**Sua dúvida anotada:** o corpus pode não incluir o texto integral das condições do art. 126

**Existe resposta no corpus:** `sim`

**Dispositivos esperados:** `LC214.art125` (LC 214/2025, art. 125); `LC214.art125.parunico` (LC 214/2025, art. 125, parágrafo único); `LC214.art126.par1` (LC 214/2025, art. 126, § 1º)

**Trechos citados (literais do corpus):**

- `LC214.art125`: “Ficam reduzidas a zero as alíquotas do IBS e da CBS incidentes sobre as vendas de produtos destinados à alimentação humana relacionados no Anexo I desta Lei Complementar, com a especificação das respectivas classificações da NCM/SH, que compõem a Cesta Básica Nacional de Alimentos, criada nos termos do art. 8º da Emenda Constitucional nº 132, de 20 de dezembro de 2023.”
- `LC214.art125.parunico`: “Aplica-se o disposto nos §§ 1º e 2º do art. 126 desta Lei Complementar às reduções de alíquotas de que trata o caput deste artigo.”
- `LC214.art126.par1`: “Atendidos os requisitos próprios, os regimes diferenciados de que trata este Capítulo aplicam-se, no que couber, à importação dos bens e serviços nele previstos.”

**Justificativa:** O art. 125 condiciona a alíquota zero à venda de produtos destinados à alimentação humana que estejam relacionados no Anexo I da LC 214, com a respectiva classificação NCM/SH, e que componham a Cesta Básica Nacional de Alimentos. O parágrafo único estende a essas reduções o disposto nos §§ 1º e 2º do art. 126; para a importação, o § 1º exige que sejam atendidos os requisitos próprios do regime, no que couber. O corpus não reproduz o Anexo I, de modo que não permite listar os produtos concretos.

**Decisão:** confirmar 

---

## c061 · H8

**Pergunta:** O que muda no tratamento do Simples Nacional para IBS e CBS entre 2026, 2030 e 2033?

**Existe resposta no corpus:** `parcial`

**Dispositivos esperados:** `CF.art146.incIII.alid` (CF, art. 146, III, d); `CF.art146.par2` (CF, art. 146, § 2º); `CF.art146.par3` (CF, art. 146, § 3º); `CF.art146.par3.incI` (CF, art. 146, § 3º, I); `CF.art146.par3.incII` (CF, art. 146, § 3º, II)

**Trechos citados (literais do corpus):**

- `CF.art146.incIII.alid`: “d) definição de tratamento diferenciado e favorecido para as microempresas e para as empresas de pequeno porte, inclusive regimes especiais ou simplificados no caso dos impostos previstos nos arts. 155, II, e 156-A, das contribuições sociais previstas no art. 195, I e V, e § 12 e da contribuição a que se refere o art. 239.”
- `CF.art146.par2`: “§ 2º É facultado ao optante pelo regime único de que trata o § 1º apurar e recolher os tributos previstos nos arts. 156-A e 195, V, nos termos estabelecidos nesses artigos, hipótese em que as parcelas a eles relativas não serão cobradas pelo regime único.”
- `CF.art146.par3`: “§ 3º Na hipótese de o recolhimento dos tributos previstos nos arts. 156-A e 195, V, ser realizado por meio do regime único de que trata o § 1º, enquanto perdurar a opção:”
- `CF.art146.par3.incI`: “I - não será permitida a apropriação de créditos dos tributos previstos nos arts. 156-A e 195, V, pelo contribuinte optante pelo regime único; e”
- `CF.art146.par3.incII`: “II - será permitida a apropriação de créditos dos tributos previstos nos arts. 156-A e 195, V, pelo adquirente não optante pelo regime único de que trata o § 1º de bens materiais ou imateriais, inclusive direitos, e de serviços do optante, em montante equivalente ao cobrado por meio do regime único.”

**Justificativa:** Na data de referência, está vigente a redação do art. 146, III, d, com efeitos até 2026-12-31, que autoriza tratamento diferenciado e favorecido para microempresas e empresas de pequeno porte, inclusive regimes especiais ou simplificados para o IBS e a CBS. O § 2º faculta ao optante pelo regime único apurar e recolher IBS e CBS pelas regras gerais, caso em que tais parcelas não são cobradas pelo regime único. O § 3º, I e II, estabelece que, se o recolhimento for pelo regime único, o optante não apropria créditos, mas o adquirente não optante pode apropriar crédito equivalente ao cobrado no regime único. As versões do art. 146, III, d, com efeitos a partir de 2027 e de 2033, não alcançam a data de referência, de modo que o corpus só permite responder à parte relativa a 2026.

**Decisão:** confirmar

---

## c062 · H8

**Pergunta:** O Imposto Seletivo integra a base do ICMS e do ISS até 2032 e depois de 2033?

**Existe resposta no corpus:** `sim`

**Dispositivos esperados:** `CF.art153.par6.incIV` (CF, art. 153, § 6º, IV)

**Trechos citados (literais do corpus):**

- `CF.art153.par6.incIV`: “IV - integrará a base de cálculo dos tributos previstos nos arts. 155, II, 156, III, 156-A e 195, V;”
- `CF.art153.par6.incIV`: “IV - integrará a base de cálculo dos tributos previstos nos arts. 156-A e 195, V;”

**Justificativa:** Até 31 de dezembro de 2032, o inciso IV prevê que o imposto do art. 153, VIII integra a base de cálculo dos tributos dos arts. 155, II (ICMS), 156, III (ISS), 156-A e 195, V. A partir de 2033, a redação com efeitos iniciados em 2033-01-01 passa a prever integração apenas dos tributos dos arts. 156-A e 195, V, excluindo o ICMS e o ISS. Na data de referência, vigora a primeira redação.

**Decisão:** confirmar

---

## c063 · H8

**Pergunta:** O IBS integra sua própria base e a do PIS/Cofins até 2026, e depois?

**Existe resposta no corpus:** `sim`

**Dispositivos esperados:** `CF.art156-A.par1.incIX` (CF, art. 156-A, § 1º, IX); `ADCT.art126` (ADCT, art. 126); `ADCT.art126.incII` (ADCT, art. 126, II)

**Trechos citados (literais do corpus):**

- `CF.art156-A.par1.incIX`: “IX - não integrará sua própria base de cálculo nem a dos tributos previstos nos arts. 153, VIII, e 195, I, "b", IV e V, e da contribuição para o Programa de Integração Social de que trata o art. 239;”
- `CF.art156-A.par1.incIX`: “IX - não integrará sua própria base de cálculo nem a dos tributos previstos nos arts. 153, VIII, e 195, V;”
- `ADCT.art126`: “Art. 126. A partir de 2027:”
- `ADCT.art126.incII`: “II - serão extintas as contribuições previstas no art. 195, I, "b", e IV, e a contribuição para o Programa de Integração Social de que trata o art. 239, todos da Constituição Federal, desde que instituída a contribuição referida na alínea "a" do inciso I;”

**Justificativa:** Na data de referência, aplica-se a redação do art. 156-A, § 1º, IX, com efeitos até 31/12/2026: o IBS não integra sua própria base de cálculo nem a dos tributos ali listados, incluindo as contribuições de PIS/Cofins. A partir de 2027, a nova redação mantém a não integração da base do próprio IBS e passa a mencionar apenas o IS e a CBS. Além disso, o art. 126 do ADCT estabelece que, a partir de 2027, serão extintas as contribuições do art. 195, I, "b", e IV, e a contribuição para o PIS, desde que instituída a CBS. Assim, depois de 2026 não se fala mais em integrar a base do PIS/Cofins porque tais contribuições são extintas, permanecendo a regra de não integração da própria base do IBS e das bases do IS e da CBS.

**Decisão:** confirmar

---

## c064 · H8

**Pergunta:** A CBS integra a base do PIS/Cofins até 2026 e depois de 2027?

**Existe resposta no corpus:** `sim`

**Dispositivos esperados:** `CF.art195.par17` (CF, art. 195, § 17); `ADCT.art126.incII` (ADCT, art. 126, II)

**Trechos citados (literais do corpus):**

- `CF.art195.par17`: “§ 17. A contribuição prevista no inciso V do caput não integrará sua própria base de cálculo nem a dos tributos previstos nos arts. 153, VIII, 156-A e 195, I, "b", e IV, e da contribuição para o Programa de Integração Social de que trata o art. 239.”
- `ADCT.art126.incII`: “II - serão extintas as contribuições previstas no art. 195, I, "b", e IV, e a contribuição para o Programa de Integração Social de que trata o art. 239, todos da Constituição Federal, desde que instituída a contribuição referida na alínea "a" do inciso I;”

**Justificativa:** Em 13/11/2026 está vigente a redação do § 17 do art. 195 da Constituição que expressamente afasta a CBS (contribuição do art. 195, V) da base de cálculo das contribuições do art. 195, I, "b" e IV e do PIS do art. 239, que correspondem ao PIS/Cofins. Portanto, até 2026 a CBS não integra a base do PIS/Cofins. A partir de 2027, o art. 126, II, do ADCT determina a extinção dessas mesmas contribuições, de modo que deixa de existir base de PIS/Cofins para a CBS integrar.

**Decisão:** confirmar

---

## c065 · H8

**Pergunta:** Quais tributos entram no regime fiscal favorecido para biocombustíveis em 2026, 2030 e 2033?

**Existe resposta no corpus:** `sim`

**Dispositivos esperados:** `CF.art225.par1.incVIII` (CF, art. 225, § 1º, VIII)

**Trechos citados (literais do corpus):**

- `CF.art225.par1.incVIII`: “especialmente em relação às contribuições de que tratam o art. 195, I, "b", IV e V, e o art. 239 e aos impostos a que se referem os arts. 155, II, e 156-A.”
- `CF.art225.par1.incVIII`: “especialmente em relação à contribuição de que trata o art. 195, V, e aos impostos a que se referem os arts. 155, II, e 156-A.”
- `CF.art225.par1.incVIII`: “especialmente em relação à contribuição de que trata o art. 195, V, e ao imposto a que se refere o art. 156-A.”

**Justificativa:** O corpus traz três redações temporais do art. 225, § 1º, VIII. Para 2026, o regime abrange as contribuições do art. 195, I, "b", IV e V, e do art. 239, além dos impostos dos arts. 155, II, e 156-A. Para 2030, abrange a contribuição do art. 195, V, e os impostos dos arts. 155, II, e 156-A. Em 2033, abrange a contribuição do art. 195, V, e o imposto do art. 156-A.

**Decisão:** confirmar

---

## c066 · H8

**Pergunta:** O repasse de 25% aos municípios da arrecadação do IPI muda a partir de 2033?

**Existe resposta no corpus:** `sim`

**Dispositivos esperados:** `CF.art159.par3` (CF, art. 159, § 3º)

**Trechos citados (literais do corpus):**

- `CF.art159.par3`: “§ 3º Os Estados entregarão aos respectivos Municípios 25% (vinte e cinco por cento) dos recursos que receberem nos termos do inciso II docaputdeste artigo, observados os critérios estabelecidos no art. 158, § 1º, para a parcela relativa ao imposto sobre produtos industrializados, e no art. 158, § 2º, para a parcela relativa ao imposto previsto no art. 153, VIII.”
- `CF.art159.par3`: “§ 3º Os Estados entregarão aos respectivos Municípios 25% (vinte e cinco por cento) dos recursos que receberem nos termos do inciso II docaputdeste artigo, observados os critérios estabelecidos no art. 158, § 2º.”

**Justificativa:** Em 2026-11-13, a redação aplicável até 2032 determina que os Estados entreguem aos Municípios 25% dos recursos do inciso II, observando o art. 158, § 1º para a parcela relativa ao IPI. A partir de 2033, a redação com efeitos desde 2033 mantém os 25%, mas passa a observar apenas o art. 158, § 2º. Portanto, o percentual não se altera, mas a regra/critério do repasse vinculado ao IPI muda a partir de 2033.

**Decisão:** confirmar

---

## c067 · H8

**Pergunta:** Os recursos do Fundeb continuam recebendo receitas do ICMS até 2032 e o que entra no lugar em 2033?

**Existe resposta no corpus:** `sim`

**Dispositivos esperados:** `CF.art212-A.incII` (CF, art. 212-A, II); `CF.art212-A.incII.alia` (CF, art. 212-A, II, a); `CF.art212-A.incII.alib` (CF, art. 212-A, II, b); `CF.art212-A.incII.alic` (CF, art. 212-A, II, c); `ADCT.art129` (ADCT, art. 129)

**Trechos citados (literais do corpus):**

- `CF.art212-A.incII`: “II - os fundos referidos no inciso I do caput deste artigo serão constituídos por 20% (vinte por cento):”
- `CF.art212-A.incII.alia`: “a) das parcelas dos Estados no imposto de que trata o art. 156-A;”
- `CF.art212-A.incII.alib`: “b) da parcela do Distrito Federal no imposto de que trata o art. 156-A, relativa ao exercício de sua competência estadual, nos termos do art. 156-A, § 2º; e”
- `CF.art212-A.incII.alic`: “c) dos recursos a que se referem os incisos I, II e III do caput do art. 155, o inciso II do caput do art. 157, os incisos II, III e IV do caput do art. 158 e as alíneas "a" e "b" do inciso I e o inciso II do caput do art. 159 desta Constituição;”
- `ADCT.art129`: “Art. 129. Ficam extintos, a partir de 2033, os impostos previstos nos arts. 155, II, e 156, III, da Constituição Federal.”

**Justificativa:** Os fundos referidos no art. 212-A são constituídos por 20% de determinadas receitas; com efeitos até 2032, a alínea “c” inclui os recursos do inciso II do art. 155, que é o ICMS. A partir de 2033, o art. 129 do ADCT extingue o imposto do art. 155, II, e as alíneas “a” e “b” do art. 212-A, II mantêm entre as bases dos fundos as parcelas dos Estados e do Distrito Federal no imposto do art. 156-A. Assim, até 2032 há receita de ICMS; em 2033 ela deixa de compor os fundos, que passam a contar com as parcelas estaduais/distrital do imposto do art. 156-A.

**Decisão:** confirmar

---

## c068 · H8

**Pergunta:** A retenção dos repasses estaduais para o Comitê Gestor muda em 2033?

**Existe resposta no corpus:** `parcial` ⚠️ diverge do palpite da criação (sim)

**Dispositivos esperados:** `ADCT.art104.incIV` (ADCT, art. 104, IV)

**Trechos citados (literais do corpus):**

- `ADCT.art104.incIV`: “os Estados e o Comitê Gestor do Imposto sobre Bens e Serviços reterão os repasses previstos, respectivamente, nos §§ 1º e 2º do art. 158 da Constituição Federal e os depositarão na conta especial referida no art. 101 deste Ato das Disposições Constitucionais Transitórias, para utilização como nele previsto.”

**Justificativa:** Na data de referência de 2026-11-13, está vigente a redação do art. 104, IV, cujos efeitos vão até 31/12/2032, que prevê a retenção pelos Estados e pelo Comitê Gestor dos repasses dos §§ 1º e 2º do art. 158. A redação que a partir de 2033 atribui a retenção apenas ao Comitê Gestor tem efeitos iniciados em 2033-01-01 e, pela regra temporal, não alcança a data de referência. Assim, o corpus confirma o regime atual, mas não permite responder integralmente sobre a mudança em 2033 nessa data.

**Decisão:** mudar: answer_exists sim (o corpus contém a versão futura do ADCT.art104.incIV a partir de 2033, que responde integralmente que a retenção muda, conforme a hipótese H8 de várias versões no tempo) 

---

## c069 · H9

**Pergunta:** O ICMS ainda existe em 2033?

**Existe resposta no corpus:** `sim`

**Dispositivos esperados:** `ADCT.art129` (ADCT, art. 129); `CF.art158.incIV.alia` (CF, art. 158, IV, a)

**Trechos citados (literais do corpus):**

- `ADCT.art129`: “Ficam extintos, a partir de 2033, os impostos previstos nos arts. 155, II, e 156, III, da Constituição Federal.”
- `CF.art158.incIV.alia`: “a) do produto da arrecadação do imposto do Estado sobre operações relativas à circulação de mercadorias e sobre prestações de serviços de transporte interestadual e intermunicipal e de comunicação;”

**Justificativa:** O corpus descreve o imposto estadual sobre operações relativas à circulação de mercadorias e sobre prestações de transporte interestadual e intermunicipal e de comunicação no art. 158, IV, “a”. O ADCT determina que os impostos previstos no art. 155, II, e no art. 156, III, ficam extintos a partir de 2033. Assim, na data de referência, a resposta é que o ICMS não existirá em 2033.

**Decisão:** confirmar

---

## c070 · H9

**Pergunta:** O IPI sobre produtos nacionais em geral ainda poderá ser cobrado em 2033?

**Existe resposta no corpus:** `sim`

**Dispositivos esperados:** `ADCT.art126` (ADCT, art. 126); `ADCT.art126.incIII` (ADCT, art. 126, III); `ADCT.art126.incIII.alia` (ADCT, art. 126, III, a)

**Trechos citados (literais do corpus):**

- `ADCT.art126`: “Art. 126. A partir de 2027:”
- `ADCT.art126.incIII`: “III - o imposto previsto no art. 153, IV, da Constituição Federal:”
- `ADCT.art126.incIII.alia`: “a) terá suas alíquotas reduzidas a zero, exceto em relação aos produtos que tenham industrialização incentivada na Zona Franca de Manaus, conforme critérios estabelecidos em lei complementar; e”

**Justificativa:** O art. 126 fixa que a regra passa a valer a partir de 2027. O inciso III trata do imposto previsto no art. 153, IV, da Constituição Federal. A alínea "a" determina que esse imposto terá alíquotas reduzidas a zero, ressalvados apenas os produtos com industrialização incentivada na Zona Franca de Manaus. Assim, em 2033 o IPI sobre produtos nacionais em geral não poderá ser cobrado, sem prejuízo dessa exceção.

**Decisão:** confirmar

---

## c071 · H9

**Pergunta:** A contribuição da Cofins sobre o faturamento ainda será cobrada em 2033?

**Existe resposta no corpus:** `sim`

**Dispositivos esperados:** `ADCT.art126` (ADCT, art. 126); `ADCT.art126.incII` (ADCT, art. 126, II)

**Trechos citados (literais do corpus):**

- `ADCT.art126`: “Art. 126. A partir de 2027:”
- `ADCT.art126.incII`: “II - serão extintas as contribuições previstas no art. 195, I, "b", e IV, e a contribuição para o Programa de Integração Social de que trata o art. 239, todos da Constituição Federal, desde que instituída a contribuição referida na alínea "a" do inciso I;”

**Justificativa:** O art. 126 do ADCT fixa que, a partir de 2027, serão extintas as contribuições previstas no art. 195, I, "b", e IV, e a contribuição para o PIS, condicionado à instituição da contribuição do art. 195, V. A Cofins sobre o faturamento é tratada no corpus como a contribuição do art. 195, I, "b". Assim, como a extinção se dá em 2027, em 2033 essa contribuição não mais será cobrada.

**Decisão:** confirmar

---

## c072 · H9

**Pergunta:** O § 2º do art. 82 do ADCT ainda vale em 2033?

**Existe resposta no corpus:** `sim`

**Dispositivos esperados:** `EC132.art22` (EC 132/2023, art. 22); `EC132.art22.incII` (EC 132/2023, art. 22, II); `EC132.art22.incII.alib` (EC 132/2023, art. 22, II, b)

**Trechos citados (literais do corpus):**

- `EC132.art22`: “Art. 22. Revogam-se:”
- `EC132.art22.incII`: “II - em 2033:”
- `EC132.art22.incII.alib`: “b) os arts. 80, II, 82, § 2º, e 83 do Ato das Disposições Constitucionais Transitórias.”

**Justificativa:** O art. 22 da EC 132/2023 determina que se revogam, em 2033, os dispositivos que indica. Entre eles, a alínea "b" do inciso II inclui expressamente o art. 82, § 2º, do ADCT. Portanto, segundo o corpus, o § 2º do art. 82 do ADCT não continuará valendo em 2033, pois será revogado nessa data.

**Decisão:** confirmar

---

## c073 · H9

**Pergunta:** A regra do art. 161, I, sobre valor adicionado continua em 2033?

**Existe resposta no corpus:** `nao` ⚠️ diverge do palpite da criação (sim)

**Dispositivos esperados:** nenhum

**Justificativa:** O corpus não contém o art. 161, I, nem qualquer dispositivo que trate especificamente da regra sobre valor adicionado e de sua continuidade em 2033. Assim, não há base normativa no corpus para responder à pergunta.

**Decisão:** mudar: answer_exists sim, dispositivos CF.art161.incI e EC132.art22.incII.alia (ambos constam do corpus; o art. 22, II, "a" da EC 132 revoga expressamente o art. 161, I a partir de 2033, respondendo que a regra não continua) 

---

## c074 · H10

**Pergunta:** Qual é o caput do art. 145 da Constituição?

**Existe resposta no corpus:** `nao`

**Dispositivos esperados:** nenhum

**Justificativa:** O corpus não contém o caput do art. 145 da Constituição. Há apenas os §§ 3º e 4º desse artigo, que tratam de princípios do Sistema Tributário Nacional e de atenuação de efeitos regressivos, mas não reproduzem o texto do caput solicitado.

**Decisão:** confirmar

---

## c075 · H10

**Pergunta:** O que diz o caput do § 1º do art. 155 sobre o ITCMD?

**Existe resposta no corpus:** `nao`

**Dispositivos esperados:** nenhum

**Justificativa:** O corpus não contém o caput do § 1º do art. 155 da Constituição Federal. Ele traz apenas dispositivos relacionados a incisos desse parágrafo, como o inciso II, o inciso VI e o inciso VII, mas não o texto do caput. Portanto, com base exclusivamente no corpus, não é possível responder o que o caput diz sobre o ITCMD.

**Decisão:** confirmar

---

## c076 · H10

**Pergunta:** Qual é o caput do art. 158 da Constituição sobre repartição?

**Existe resposta no corpus:** `nao`

**Dispositivos esperados:** nenhum

**Justificativa:** O corpus não contém o caput do art. 158 da Constituição Federal. Ele traz apenas dispositivos derivados desse artigo, como os incisos III e IV e os §§ 1º e 2º, mas não o texto introdutório do caput sobre repartição. Portanto, não há como responder integralmente à pergunta com base exclusivamente no corpus fornecido.

**Decisão:** confirmar

---

## c077 · H10

**Pergunta:** Qual é o caput do art. 159?

**Existe resposta no corpus:** `nao`

**Dispositivos esperados:** nenhum

**Justificativa:** O corpus não contém o texto do caput do art. 159 da Constituição Federal. Ele traz apenas dispositivos relacionados, como os incisos I, II e III e o § 3º do art. 159, mas não o enunciado do caput. Portanto, não é possível responder integralmente à pergunta com base exclusivamente no corpus.

**Decisão:** confirmar

---

## c078 · H10

**Pergunta:** Qual é o caput do § 2º do art. 198 sobre saúde?

**Existe resposta no corpus:** `nao`

**Dispositivos esperados:** nenhum

**Justificativa:** O corpus disponibiliza apenas os incisos II e III do § 2º do art. 198 da Constituição Federal, ambos com efeitos desde 2023-12-21 e, portanto, vigentes na data de referência. Não há, porém, o texto do caput desse § 2º. Assim, não é possível responder qual é o caput do § 2º do art. 198 com base exclusivamente no corpus.

**Decisão:** confirmar

---

## c079 · H11

**Pergunta:** Quais são as alíquotas previstas para o IBS e para a CBS nos anos de 2026, 2027 e 2028?

**Existe resposta no corpus:** `sim`

**Dispositivos esperados:** `ADCT.art125` (ADCT, art. 125); `ADCT.art127` (ADCT, art. 127); `ADCT.art127.parunico` (ADCT, art. 127, parágrafo único)

**Trechos citados (literais do corpus):**

- `ADCT.art125`: “Art. 125. Em 2026, o imposto previsto no art. 156-A será cobrado à alíquota estadual de 0,1% (um décimo por cento), e a contribuição prevista no art. 195, V, ambos da Constituição Federal, será cobrada à alíquota de 0,9% (nove décimos por cento).”
- `ADCT.art127`: “Art. 127. Em 2027 e 2028, o imposto previsto no art. 156-A da Constituição Federal será cobrado à alíquota estadual de 0,05% (cinco centésimos por cento) e à alíquota municipal de 0,05% (cinco centésimos por cento).”
- `ADCT.art127.parunico`: “No período referido no caput, a alíquota da contribuição prevista no art. 195, V, da Constituição Federal, será reduzida em 0,1 (um décimo) ponto percentual.”

**Justificativa:** A EC 132/2023 fixa, para 2026, o IBS estadual em 0,1% e a CBS em 0,9%. Para 2027 e 2028, o IBS é cobrado a 0,05% estadual e 0,05% municipal. No mesmo período, a CBS sofre redução de 0,1 ponto percentual, o que, tomada a alíquota de 0,9%, resulta em 0,8%.

**Decisão:** confirmar

---

## c080 · H11

**Pergunta:** Quando começa e termina a transição do ICMS e do ISS para o IBS?

**Existe resposta no corpus:** `sim`

**Dispositivos esperados:** `ADCT.art125` (ADCT, art. 125); `ADCT.art127` (ADCT, art. 127); `ADCT.art128` (ADCT, art. 128); `ADCT.art129` (ADCT, art. 129)

**Trechos citados (literais do corpus):**

- `ADCT.art125`: “Em 2026, o imposto previsto no art. 156-A será cobrado à alíquota estadual de 0,1% (um décimo por cento)”
- `ADCT.art127`: “Em 2027 e 2028, o imposto previsto no art. 156-A da Constituição Federal será cobrado à alíquota estadual de 0,05% (cinco centésimos por cento) e à alíquota municipal de 0,05% (cinco centésimos por cento).”
- `ADCT.art128`: “De 2029 a 2032, as alíquotas dos impostos previstos nos arts. 155, II, e 156, III, da Constituição Federal, serão fixadas nas seguintes proporções das alíquotas fixadas nas respectivas legislações:”
- `ADCT.art129`: “Ficam extintos, a partir de 2033, os impostos previstos nos arts. 155, II, e 156, III, da Constituição Federal.”

**Justificativa:** O corpus indica que a fase inicial do IBS ocorre em 2026, com alíquota estadual de 0,1%, e continua em 2027 e 2028 com 0,05% estadual e municipal. A redução das alíquotas dos impostos dos arts. 155, II, e 156, III vai de 2029 a 2032. A partir de 2033 esses impostos são extintos. Portanto, a transição do ICMS/ISS para o IBS começa em 2026 e se encerra em 2032, com a extinção dos tributos antigos em 2033.

**Decisão:** confirmar

---

## c081 · H11

**Pergunta:** Como fica a cesta básica em 2026 e depois de 2033?

**Existe resposta no corpus:** `sim` ⚠️ diverge do palpite da criação (parcial)

**Dispositivos esperados:** `EC132.art8.parunico` (EC 132/2023, art. 8º, parágrafo único); `LC214.art125` (LC 214/2025, art. 125)

**Trechos citados (literais do corpus):**

- `EC132.art8.parunico`: “Lei complementar definirá os produtos destinados à alimentação humana que comporão a Cesta Básica Nacional de Alimentos, sobre os quais as alíquotas dos tributos previstos nos arts. 156-A e 195, V, da Constituição Federal serão reduzidas a zero.”
- `LC214.art125`: “Ficam reduzidas a zero as alíquotas do IBS e da CBS incidentes sobre as vendas de produtos destinados à alimentação humana relacionados no Anexo I desta Lei Complementar, com a especificação das respectivas classificações da NCM/SH, que compõem a Cesta Básica Nacional de Alimentos”

**Justificativa:** Na data de referência, já produzem efeitos o art. 8º, parágrafo único, da EC 132/2023 e o art. 125 da LC 214/2025, que reduzem a zero as alíquotas do IBS e da CBS incidentes sobre os produtos destinados à alimentação humana que compõem a Cesta Básica Nacional de Alimentos, listados no Anexo I. O art. 125 da LC 214/2025 tem efeitos desde 2026-01-01 e não traz termo final; assim, o mesmo tratamento de alíquota zero permanece depois de 2033. O corpus não indica alteração posterior específica para a cesta básica.

**Decisão:** confirmar

---

## c082 · H11

**Pergunta:** Quem administra o IBS e como ele é distribuído entre estados e municípios?

**Existe resposta no corpus:** `sim` ⚠️ diverge do palpite da criação (parcial)

**Dispositivos esperados:** `CF.art156-B` (CF, art. 156-B); `CF.art156-B.incII` (CF, art. 156-B, II); `CF.art156-A.par4.incII` (CF, art. 156-A, § 4º, II); `CF.art158.incIV` (CF, art. 158, IV); `CF.art158.incIV.alib` (CF, art. 158, IV, b); `CF.art158.par2` (CF, art. 158, § 2º); `ADCT.art125` (ADCT, art. 125); `ADCT.art125.par3` (ADCT, art. 125, § 3º); `ADCT.art125.par3.incI` (ADCT, art. 125, § 3º, I); `ADCT.art125.par3.incII` (ADCT, art. 125, § 3º, II)

**Trechos citados (literais do corpus):**

- `CF.art156-B`: “Os Estados, o Distrito Federal e os Municípios exercerão de forma integrada, exclusivamente por meio do Comitê Gestor do Imposto sobre Bens e Serviços”
- `CF.art156-B.incII`: “II - arrecadar o imposto, efetuar as compensações e distribuir o produto da arrecadação entre Estados, Distrito Federal e Municípios;”
- `CF.art156-A.par4.incII`: “II - distribuirá o produto da arrecadação do imposto, deduzida a retenção de que trata o inciso I deste parágrafo, ao ente federativo de destino das operações que não tenham gerado creditamento.”
- `CF.art158.incIV`: “IV - 25% (vinte e cinco por cento):”
- `CF.art158.incIV.alib`: “b) do produto da arrecadação do imposto previsto no art. 156-A distribuída aos Estados.”
- `CF.art158.par2`: “§ 2º As parcelas de receita pertencentes aos Municípios mencionadas no inciso IV, "b", serão creditadas conforme os seguintes critérios:”
- `ADCT.art125`: “Em 2026, o imposto previsto no art. 156-A será cobrado à alíquota estadual de 0,1% (um décimo por cento)”
- `ADCT.art125.par3`: “§ 3º A arrecadação do imposto previsto no art. 156-A da Constituição Federal decorrente do disposto no caput deste artigo não observará as vinculações, repartições e destinações previstas na Constituição Federal, devendo ser aplicada, integral e sucessivamente, para:”
- `ADCT.art125.par3.incI`: “I - o financiamento do Comitê Gestor do Imposto sobre Bens e Serviços, nos termos do art. 156-B, § 2º, III, da Constituição Federal;”
- `ADCT.art125.par3.incII`: “II - compor o Fundo de Compensação de Benefícios Fiscais ou Financeiro-Fiscais do imposto de que trata o art. 155, II, da Constituição Federal.”

**Justificativa:** O IBS é administrado exclusivamente pelo Comitê Gestor do IBS, que exerce de forma integrada as competências administrativas dos Estados, do Distrito Federal e dos Municípios (CF, art. 156-B) e, entre elas, arrecadar, compensar e distribuir o produto (CF, art. 156-B, II). Na sistemática permanente, o Comitê distribui o produto, deduzida a retenção, ao ente de destino das operações que não geraram creditamento (CF, art. 156-A, § 4º, II), e 25% da parcela distribuída aos Estados pertence aos Municípios, creditada conforme o § 2º do art. 158 (CF, art. 158, IV, b, e § 2º). Contudo, na data de referência, o IBS é cobrado em 2026 à alíquota estadual de 0,1% (ADCT, art. 125) e essa arrecadação não observa as repartições e destinações constitucionais, sendo aplicada ao financiamento do Comitê e ao Fundo de Compensação (ADCT, art. 125, § 3º, I e II).

**Decisão:** confirmar 

---

## c083 · H11

**Pergunta:** Qual a diferença entre a redução de 60% e a de 30% para serviços profissionais?

**Existe resposta no corpus:** `sim`

**Dispositivos esperados:** `EC132.art9.par1` (EC 132/2023, art. 9º, § 1º); `EC132.art9.par12` (EC 132/2023, art. 9º, § 12); `LC214.art127` (LC 214/2025, art. 127); `LC214.art128` (LC 214/2025, art. 128)

**Trechos citados (literais do corpus):**

- `EC132.art9.par1`: “§ 1º A lei complementar definirá as operações beneficiadas com redução de 60% (sessenta por cento) das alíquotas dos tributos de que trata o caput entre as relativas aos seguintes bens e serviços:”
- `EC132.art9.par12`: “§ 12. A lei complementar estabelecerá as operações beneficiadas com redução de 30% (trinta por cento) das alíquotas dos tributos de que trata o caput relativas à prestação de serviços de profissão intelectual, de natureza científica, literária ou artística, desde que sejam submetidas a fiscalização por conselho profissional.”
- `LC214.art127`: “Art. 127. Ficam reduzidas em 30% (trinta por cento) as alíquotas do IBS e da CBS incidentes sobre a prestação de serviços pelos seguintes profissionais, que exercerem atividades intelectuais de natureza científica, literária ou artística, submetidas à fiscalização por conselho profissional:”
- `LC214.art128`: “Art. 128. Desde que observadas as definições e demais disposições deste Capítulo, ficam reduzidas em 60% (sessenta por cento) as alíquotas do IBS e da CBS incidentes sobre operações com:”

**Justificativa:** A redução de 60% é dirigida a operações com os bens e serviços elencados pela lei complementar, conforme autoriza a EC 132/2023 e implementa a LC 214/2025. Já a redução de 30% é específica para a prestação de serviços de profissão intelectual de natureza científica, literária ou artística, sujeitos à fiscalização por conselho profissional. A LC 214/2025 repete essa distinção: o art. 127 fixa 30% para os profissionais listados, enquanto o art. 128 fixa 60% para as operações com os bens e serviços ali elencados.

**Decisão:** confirmar

---

## c084 · H11

**Pergunta:** Quem define os limites e as regras de devolução do IBS e da CBS para pessoas físicas?

**Existe resposta no corpus:** `sim`

**Dispositivos esperados:** `CF.art156-A.par5` (CF, art. 156-A, § 5º); `CF.art156-A.par5.incVIII` (CF, art. 156-A, § 5º, VIII); `CF.art195.par18` (CF, art. 195, § 18)

**Trechos citados (literais do corpus):**

- `CF.art156-A.par5`: “§ 5º Lei complementar disporá sobre:”
- `CF.art156-A.par5.incVIII`: “VIII - as hipóteses de devolução do imposto a pessoas físicas, inclusive os limites e os beneficiários, com o objetivo de reduzir as desigualdades de renda;”
- `CF.art195.par18`: “§ 18. Lei estabelecerá as hipóteses de devolução da contribuição prevista no inciso V do caput a pessoas físicas, inclusive em relação a limites e beneficiários, com o objetivo de reduzir as desigualdades de renda.”

**Justificativa:** O art. 156-A, § 5º, caput, remete a lei complementar a disciplina das matérias ali listadas; o inciso VIII inclui as hipóteses de devolução do IBS a pessoas físicas, com limites e beneficiários. Já o art. 195, § 18, determina que 'Lei' estabeleça as hipóteses de devolução da CBS (contribuição do inciso V) a pessoas físicas, inclusive limites e beneficiários. Assim, na data de referência, a definição é da lei complementar para o IBS e da lei para a CBS.

**Decisão:** confirmar

---

## c085 · H11

**Pergunta:** A partir de quando o Imposto Seletivo passa a ser cobrado na venda de veículos?

**Existe resposta no corpus:** `sim`

**Dispositivos esperados:** `ADCT.art126` (ADCT, art. 126); `ADCT.art126.incI.alib` (ADCT, art. 126, I, b); `LC214.art419` (LC 214/2025, art. 419)

**Trechos citados (literais do corpus):**

- `ADCT.art126`: “Art. 126. A partir de 2027:”
- `ADCT.art126.incI.alib`: “b) o imposto previsto no art. 153, VIII, da Constituição Federal;”
- `LC214.art419`: “Art. 419. As alíquotas do Imposto Seletivo aplicáveis aos veículos classificados nos códigos da NCM/SH relacionados no Anexo XVII serão estabelecidas em lei ordinária.”

**Justificativa:** O ADCT, art. 126, estabelece que a partir de 2027 serão cobrados tributos, e a alínea b do inciso I inclui o imposto previsto no art. 153, VIII, da Constituição Federal. A LC 214/2025, art. 419, trata especificamente das alíquotas do Imposto Seletivo aplicáveis a veículos. Na data de referência, 2026-11-13, essa cobrança ainda não começou, pois seu início está fixado para 2027.

**Decisão:** confirmar

---

## c086 · H11

**Pergunta:** Qual a regra de transição para as alíquotas do ICMS e do ISS de 2029 a 2032?

**Existe resposta no corpus:** `sim`

**Dispositivos esperados:** `ADCT.art128` (ADCT, art. 128); `ADCT.art128.incI` (ADCT, art. 128, I); `ADCT.art128.incII` (ADCT, art. 128, II); `ADCT.art128.incIII` (ADCT, art. 128, III); `ADCT.art128.incIV` (ADCT, art. 128, IV)

**Trechos citados (literais do corpus):**

- `ADCT.art128`: “Art. 128. De 2029 a 2032, as alíquotas dos impostos previstos nos arts. 155, II, e 156, III, da Constituição Federal, serão fixadas nas seguintes proporções das alíquotas fixadas nas respectivas legislações:”
- `ADCT.art128.incI`: “I - 9/10 (nove décimos), em 2029;”
- `ADCT.art128.incII`: “II - 8/10 (oito décimos), em 2030;”
- `ADCT.art128.incIII`: “III - 7/10 (sete décimos), em 2031;”
- `ADCT.art128.incIV`: “IV - 6/10 (seis décimos), em 2032.”

**Justificativa:** O ADCT, art. 128, determina que, de 2029 a 2032, as alíquotas do ICMS (art. 155, II) e do ISS (art. 156, III) sejam fixadas em proporções decrescentes das alíquotas previstas nas respectivas legislações. Os incisos I a IV fixam 9/10 em 2029, 8/10 em 2030, 7/10 em 2031 e 6/10 em 2032. Como o dispositivo tem efeitos desde 2023-12-21, ele já integra o ordenamento na data de referência e responde à regra de transição perguntada.

**Decisão:** confirmar

---

## c087 · H12

**Pergunta:** Sou MEI e meu CNPJ é {CNPJ}; posso pagar IBS e CBS pelo Simples ou fora dele?

**Existe resposta no corpus:** `sim`

**Dispositivos esperados:** `CF.art146.par2` (CF, art. 146, § 2º); `CF.art146.par3` (CF, art. 146, § 3º); `CF.art146.par3.incI` (CF, art. 146, § 3º, I); `CF.art146.par3.incII` (CF, art. 146, § 3º, II)

**Trechos citados (literais do corpus):**

- `CF.art146.par2`: “§ 2º É facultado ao optante pelo regime único de que trata o § 1º apurar e recolher os tributos previstos nos arts. 156-A e 195, V, nos termos estabelecidos nesses artigos, hipótese em que as parcelas a eles relativas não serão cobradas pelo regime único.”
- `CF.art146.par3`: “§ 3º Na hipótese de o recolhimento dos tributos previstos nos arts. 156-A e 195, V, ser realizado por meio do regime único de que trata o § 1º, enquanto perdurar a opção:”
- `CF.art146.par3.incI`: “I - não será permitida a apropriação de créditos dos tributos previstos nos arts. 156-A e 195, V, pelo contribuinte optante pelo regime único; e”
- `CF.art146.par3.incII`: “II - será permitida a apropriação de créditos dos tributos previstos nos arts. 156-A e 195, V, pelo adquirente não optante pelo regime único de que trata o § 1º de bens materiais ou imateriais, inclusive direitos, e de serviços do optante, em montante equivalente ao cobrado por meio do regime único.”

**Justificativa:** O corpus faculta ao optante pelo regime único apurar e recolher o IBS e a CBS nos termos dos arts. 156-A e 195, V, hipótese em que o Simples não cobra essas parcelas. Também prevê o recolhimento por meio do regime único; enquanto perdurar a opção, o optante não apropria créditos, mas o adquirente não optante pode apropriar créditos equivalentes ao cobrado pelo Simples. Portanto, a resposta é sim: há a faculdade de pagar fora do Simples, e o pagamento pelo Simples é a hipótese alternativa prevista.

**Decisão:** confirmar

---

## c088 · H12

**Pergunta:** Meu CPF é {CPF}; como faço para receber a devolução do IBS sobre energia elétrica?

**Existe resposta no corpus:** `parcial`

**Dispositivos esperados:** `CF.art156-A.par5.incVIII` (CF, art. 156-A, § 5º, VIII); `CF.art156-A.par13` (CF, art. 156-A, § 13)

**Trechos citados (literais do corpus):**

- `CF.art156-A.par5.incVIII`: “VIII - as hipóteses de devolução do imposto a pessoas físicas, inclusive os limites e os beneficiários, com o objetivo de reduzir as desigualdades de renda;”
- `CF.art156-A.par13`: “§ 13. A devolução de que trata o § 5º, VIII, será obrigatória nas operações de fornecimento de energia elétrica e de gás liquefeito de petróleo ao consumidor de baixa renda, podendo a lei complementar determinar que seja calculada e concedida no momento da cobrança da operação.”

**Justificativa:** O corpus prevê que a devolução do IBS a pessoas físicas deve ser disciplinada por lei complementar, que definirá limites e beneficiários. Para energia elétrica, a devolução é obrigatória apenas ao consumidor de baixa renda, podendo a lei complementar determinar o cálculo e a concessão no momento da cobrança. Não há no corpus procedimento operacional para requerer a devolução com CPF, nem regra específica sobre como fazer.

**Decisão:** confirmar

---

## c089 · H12

**Pergunta:** Tenho CNPJ {CNPJ} de produtor rural com receita abaixo de 3,6 milhões; posso optar por ser contribuinte do IBS?

**Existe resposta no corpus:** `sim`

**Dispositivos esperados:** `EC132.art9.par4` (EC 132/2023, art. 9º, § 4º); `EC132.art9` (EC 132/2023, art. 9º)

**Trechos citados (literais do corpus):**

- `EC132.art9.par4`: “O produtor rural pessoa física ou jurídica que obtiver receita anual inferior a R$ 3.600.000,00 (três milhões e seiscentos mil reais), atualizada anualmente pelo Índice Nacional de Preços ao Consumidor Amplo (IPCA), e o produtor integrado de que trata o art. 2º, II, da Lei nº 13.288, de 16 de maio de 2016, com a redação vigente em 31 de maio de 2023, poderão optar por ser contribuintes dos tributos de que trata o caput.”
- `EC132.art9`: “A lei complementar que instituir o imposto de que trata o art. 156-A e a contribuição de que trata o art. 195, V, ambos da Constituição Federal, poderá prever os regimes diferenciados de tributação de que trata este artigo”

**Justificativa:** O § 4º do art. 9º da EC 132/2023 permite que o produtor rural pessoa jurídica com receita anual inferior a R$ 3.600.000,00, atualizada pelo IPCA, opte por ser contribuinte dos tributos de que trata o caput. O caput do mesmo artigo refere-se ao imposto do art. 156-A e à contribuição do art. 195, V, de modo que a opção alcança o IBS. Na data de referência, o dispositivo já produzia efeitos. A resposta é positiva, observado o limite atualizado e o exercício da opção.

**Decisão:** confirmar

---

## c090 · H12

**Pergunta:** Meu CPF é {CPF}; na compra de remédio, a alíquota é zero ou reduzida em 60%?

**Existe resposta no corpus:** `sim` ⚠️ diverge do palpite da criação (parcial)

**Dispositivos esperados:** `LC214.art133` (LC 214/2025, art. 133)

**Trechos citados (literais do corpus):**

- `LC214.art133`: “Ficam reduzidas em 60% (sessenta por cento) as alíquotas do IBS e da CBS incidentes sobre o fornecimento dos medicamentos registrados na Anvisa ou produzidos por farmácias de manipulação, ressalvados os medicamentos sujeitos à alíquota zero de que trata o art. 146 desta Lei Complementar.”

**Justificativa:** O art. 133 da LC 214/2025 fixa a redução de 60% das alíquotas do IBS e da CBS para medicamentos registrados na Anvisa ou produzidos por farmácias de manipulação. A mesma regra ressalva os medicamentos sujeitos à alíquota zero do art. 146. Assim, no período de referência, a regra geral é a redução de 60%, e não a alíquota zero, salvo os casos expressamente ressalvados.

**Decisão:** confirmar

---

## c091 · H12

**Pergunta:** Meu CNPJ {CNPJ} é de restaurante; qual redução de IBS e CBS eu tenho?

**Existe resposta no corpus:** `parcial`

**Dispositivos esperados:** `CF.art156-A.par6.incIV` (CF, art. 156-A, § 6º, IV)

**Trechos citados (literais do corpus):**

- `CF.art156-A.par6.incIV`: “IV - serviços de hotelaria, parques de diversão e parques temáticos, agências de viagens e de turismo, bares e restaurantes, atividade esportiva desenvolvida por Sociedade Anônima do Futebol e aviação regional, podendo prever hipóteses de alterações nas alíquotas, nas bases de cálculo e nas regras de creditamento, admitida a não aplicação do disposto no § 1º, V a VIII;”

**Justificativa:** O corpus inclui bares e restaurantes entre os serviços para os quais a Constituição autoriza regime específico, com possibilidade de alteração de alíquotas, bases de cálculo e regras de creditamento. Porém, o corpus não traz o dispositivo que fixa a redução concreta de IBS e CBS aplicável a restaurantes. Assim, a resposta é apenas parcial: há a autorização constitucional para o regime diferenciado, mas não o percentual de redução.

**Decisão:** confirmar

---

## c092 · H12

**Pergunta:** Minha escola tem CNPJ {CNPJ}; a redução de 60% vale tanto para a mensalidade quanto para o material escolar?

**Existe resposta no corpus:** `parcial`

**Dispositivos esperados:** `LC214.art129` (LC 214/2025, art. 129); `LC214.art129.parunico.incI` (LC 214/2025, art. 129, parágrafo único, I); `LC214.art129.parunico.incII` (LC 214/2025, art. 129, parágrafo único, II)

**Trechos citados (literais do corpus):**

- `LC214.art129`: “Ficam reduzidas em 60% (sessenta por cento) as alíquotas do IBS e da CBS incidentes sobre o fornecimento dos serviços de educação relacionados no Anexo II desta Lei Complementar”
- `LC214.art129.parunico.incI`: “somente se aplica sobre os valores devidos pela contraprestação dos serviços listados no Anexo II desta Lei Complementar”
- `LC214.art129.parunico.incII`: “não se aplica a outras operações eventualmente ocorridas no âmbito das escolas, das instituições ou dos estabelecimentos do fornecedor de serviços.”

**Justificativa:** A redução de 60% do IBS/CBS para educação é limitada ao fornecimento dos serviços de educação relacionados no Anexo II da LC 214/2025. O parágrafo único do art. 129 esclarece que o benefício incide apenas sobre a contraprestação desses serviços listados e não alcança outras operações realizadas no âmbito da escola. Por isso, o material escolar não está abrangido; quanto à mensalidade, só é possível confirmar a incidência se o serviço correspondente estiver no Anexo II, lista que não consta do corpus. O CNPJ informado não permite verificação no corpus.

**Decisão:** confirmar

---

## c093 · H12

**Pergunta:** Meu CPF é {CPF}; alugo um imóvel; incide IBS sobre o aluguel?

**Existe resposta no corpus:** `nao` ⚠️ diverge do palpite da criação (parcial)

**Dispositivos esperados:** nenhum

**Justificativa:** O corpus disponível não contém dispositivo que trate especificamente da incidência do IBS sobre aluguel ou locação de imóvel. Os dispositivos apresentados tratam da transição, de alíquotas de referência, de regimes reduzidos, de repartição de receitas e de outros temas, mas não definem a tributação da locação de imóvel. Assim, não é possível responder à pergunta com base apenas no corpus.

**Decisão:** mudar: answer_exists parcial, dispositivos CF.art156-A.par6.incII e EC132.art10.incII.alic (a locação de bens imóveis é expressamente incluída no regime específico de operações com bens imóveis do IBS pelo art. 10, II, "c" da EC 132) 

---

## c094 · H12

**Pergunta:** Tenho uma indústria com CNPJ {CNPJ} que compra insumos agropecuários; há diferimento de IBS e CBS nessa operação?

**Existe resposta no corpus:** `sim`

**Dispositivos esperados:** `LC214.art138` (LC 214/2025, art. 138); `LC214.art138.par2` (LC 214/2025, art. 138, § 2º); `LC214.art138.par2.incI` (LC 214/2025, art. 138, § 2º, I); `LC214.art138.par2.incI.alia` (LC 214/2025, art. 138, § 2º, I, a)

**Trechos citados (literais do corpus):**

- `LC214.art138`: “Ficam reduzidas em 60% (sessenta por cento) as alíquotas do IBS e da CBS incidentes sobre o fornecimento dos insumos agropecuários e aquícolas relacionados no Anexo IX desta Lei Complementar”
- `LC214.art138.par2`: “Fica diferido o recolhimento do IBS e da CBS incidentes nas seguintes operações com insumos agropecuários e aquícolas de que trata o caput”
- `LC214.art138.par2.incI`: “I - fornecimento realizado por contribuinte sujeito ao regime regular do IBS e da CBS para:”
- `LC214.art138.par2.incI.alia`: “a) contribuinte sujeito ao regime regular do IBS e da CBS; e”

**Justificativa:** O art. 138, § 2º, I, 'a', da LC 214/2025 prevê o diferimento do IBS e da CBS no fornecimento de insumos agropecuários e aquícolas relacionados no Anexo IX quando realizado por contribuinte sujeito ao regime regular para outro contribuinte do regime regular. Como a indústria adquirente é contribuinte do regime regular, a operação se enquadra, desde que o insumo esteja no Anexo IX e o fornecedor também seja contribuinte do regime regular. A data de referência (2026-11-13) está dentro do período de efeitos (a partir de 2026-01-01).

**Decisão:** confirmar

---

## c095 · H14

**Pergunta:** Quais são todos os critérios para graduar a alíquota do Imposto Seletivo sobre veículos?

**Existe resposta no corpus:** `sim`

**Dispositivos esperados:** `LC214.art419.parunico` (LC 214/2025, art. 419, parágrafo único); `LC214.art419.parunico.incI` (LC 214/2025, art. 419, parágrafo único, I); `LC214.art419.parunico.incII` (LC 214/2025, art. 419, parágrafo único, II); `LC214.art419.parunico.incIII` (LC 214/2025, art. 419, parágrafo único, III); `LC214.art419.parunico.incIV` (LC 214/2025, art. 419, parágrafo único, IV); `LC214.art419.parunico.incV` (LC 214/2025, art. 419, parágrafo único, V); `LC214.art419.parunico.incVI` (LC 214/2025, art. 419, parágrafo único, VI); `LC214.art419.parunico.incVII` (LC 214/2025, art. 419, parágrafo único, VII); `LC214.art419.parunico.incVIII` (LC 214/2025, art. 419, parágrafo único, VIII); `LC214.art419.parunico.incIX` (LC 214/2025, art. 419, parágrafo único, IX); `LC214.art419.parunico.incX` (LC 214/2025, art. 419, parágrafo único, X)

**Trechos citados (literais do corpus):**

- `LC214.art419.parunico`: “Parágrafo único. As alíquotas referidas no caput deste artigo serão graduadas em relação a cada veículo conforme enquadramento nos seguintes critérios, nos termos de lei ordinária:”
- `LC214.art419.parunico.incI`: “I - potência do veículo;”
- `LC214.art419.parunico.incII`: “II - eficiência energética;”
- `LC214.art419.parunico.incIII`: “III - desempenho estrutural e tecnologias assistivas à direção;”
- `LC214.art419.parunico.incIV`: “IV - reciclabilidade de materiais;”
- `LC214.art419.parunico.incV`: “V - pegada de carbono;”
- `LC214.art419.parunico.incVI`: “VI - densidade tecnológica;”
- `LC214.art419.parunico.incVII`: “VII - emissão de dióxido de carbono (eficiência energético-ambiental), considerado o ciclo do poço à roda;”
- `LC214.art419.parunico.incVIII`: “VIII - reciclabilidade veicular;”
- `LC214.art419.parunico.incIX`: “IX - realização de etapas fabris no País; e”
- `LC214.art419.parunico.incX`: “X - categoria do veículo.”

**Justificativa:** O parágrafo único do art. 419 da LC 214/2025 determina que as alíquotas do Imposto Seletivo aplicáveis a veículos sejam graduadas, em relação a cada veículo, conforme enquadramento nos critérios ali indicados, nos termos de lei ordinária. Os incisos relacionam potência, eficiência energética, desempenho estrutural e tecnologias assistivas à direção, reciclabilidade de materiais, pegada de carbono, densidade tecnológica, emissão de CO2 no ciclo do poço à roda, reciclabilidade veicular, realização de etapas fabris no País e categoria do veículo. Como esses dispositivos têm efeitos desde 2026-01-01, alcançam a data de referência de 2026-11-13.

**Decisão:** confirmar

---

## c096 · H14

**Pergunta:** Quais profissões estão listadas para a redução de 30%?

**Existe resposta no corpus:** `sim`

**Dispositivos esperados:** `LC214.art127` (LC 214/2025, art. 127); `LC214.art127.incI` (LC 214/2025, art. 127, I); `LC214.art127.incII` (LC 214/2025, art. 127, II); `LC214.art127.incIII` (LC 214/2025, art. 127, III); `LC214.art127.incIV` (LC 214/2025, art. 127, IV); `LC214.art127.incV` (LC 214/2025, art. 127, V); `LC214.art127.incVI` (LC 214/2025, art. 127, VI); `LC214.art127.incVII` (LC 214/2025, art. 127, VII); `LC214.art127.incVIII` (LC 214/2025, art. 127, VIII); `LC214.art127.incIX` (LC 214/2025, art. 127, IX); `LC214.art127.incX` (LC 214/2025, art. 127, X); `LC214.art127.incXI` (LC 214/2025, art. 127, XI); `LC214.art127.incXII` (LC 214/2025, art. 127, XII); `LC214.art127.incXIII` (LC 214/2025, art. 127, XIII); `LC214.art127.incXIV` (LC 214/2025, art. 127, XIV); `LC214.art127.incXV` (LC 214/2025, art. 127, XV); `LC214.art127.incXVI` (LC 214/2025, art. 127, XVI); `LC214.art127.incXVII` (LC 214/2025, art. 127, XVII); `LC214.art127.incXVIII` (LC 214/2025, art. 127, XVIII)

**Trechos citados (literais do corpus):**

- `LC214.art127`: “Art. 127. Ficam reduzidas em 30% (trinta por cento) as alíquotas do IBS e da CBS incidentes sobre a prestação de serviços pelos seguintes profissionais, que exercerem atividades intelectuais de natureza científica, literária ou artística, submetidas à fiscalização por conselho profissional:”
- `LC214.art127.incI`: “I - administradores;”
- `LC214.art127.incII`: “II - advogados;”
- `LC214.art127.incIII`: “III - arquitetos e urbanistas;”
- `LC214.art127.incIV`: “IV - assistentes sociais;”
- `LC214.art127.incV`: “V - bibliotecários;”
- `LC214.art127.incVI`: “VI - biólogos;”
- `LC214.art127.incVII`: “VII - contabilistas;”
- `LC214.art127.incVIII`: “VIII - economistas;”
- `LC214.art127.incIX`: “IX - economistas domésticos;”
- `LC214.art127.incX`: “X - profissionais de educação física;”
- `LC214.art127.incXI`: “XI - engenheiros e agrônomos;”
- `LC214.art127.incXII`: “XII - estatísticos;”
- `LC214.art127.incXIII`: “XIII - médicos veterinários e zootecnistas;”
- `LC214.art127.incXIV`: “XIV - museólogos;”
- `LC214.art127.incXV`: “XV - químicos;”
- `LC214.art127.incXVI`: “XVI - profissionais de relações públicas;”
- `LC214.art127.incXVII`: “XVII - técnicos industriais; e”
- `LC214.art127.incXVIII`: “XVIII - técnicos agrícolas.”

**Justificativa:** O art. 127 da LC 214/2025 reduz em 30% as alíquotas do IBS e da CBS para os serviços prestados pelos profissionais que exerçam atividades intelectuais de natureza científica, literária ou artística submetidas a conselho profissional. Os incisos I a XVIII arrolam as profissões beneficiadas, incluindo administradores, advogados, arquitetos e urbanistas, assistentes sociais, bibliotecários, biólogos, contabilistas, economistas, economistas domésticos, profissionais de educação física, engenheiros e agrônomos, estatísticos, médicos veterinários e zootecnistas, museólogos, químicos, profissionais de relações públicas, técnicos industriais e técnicos agrícolas. A data de referência está coberta pelos efeitos desde 2026-01-01.

**Decisão:** confirmar

---

## c097 · H14

**Pergunta:** Quais operações estão listadas no art. 128 com redução de 60%?

**Existe resposta no corpus:** `sim`

**Dispositivos esperados:** `LC214.art128` (LC 214/2025, art. 128); `LC214.art128.incI` (LC 214/2025, art. 128, I); `LC214.art128.incII` (LC 214/2025, art. 128, II); `LC214.art128.incIII` (LC 214/2025, art. 128, III); `LC214.art128.incIV` (LC 214/2025, art. 128, IV); `LC214.art128.incV` (LC 214/2025, art. 128, V); `LC214.art128.incVI` (LC 214/2025, art. 128, VI); `LC214.art128.incVII` (LC 214/2025, art. 128, VII); `LC214.art128.incVIII` (LC 214/2025, art. 128, VIII); `LC214.art128.incIX` (LC 214/2025, art. 128, IX); `LC214.art128.incX` (LC 214/2025, art. 128, X); `LC214.art128.incXI` (LC 214/2025, art. 128, XI); `LC214.art128.incXII` (LC 214/2025, art. 128, XII); `LC214.art128.incXIII` (LC 214/2025, art. 128, XIII)

**Trechos citados (literais do corpus):**

- `LC214.art128`: “Art. 128. Desde que observadas as definições e demais disposições deste Capítulo, ficam reduzidas em 60% (sessenta por cento) as alíquotas do IBS e da CBS incidentes sobre operações com:”
- `LC214.art128.incI`: “I - serviços de educação;”
- `LC214.art128.incII`: “II - serviços de saúde;”
- `LC214.art128.incIII`: “III - dispositivos médicos;”
- `LC214.art128.incIV`: “IV - dispositivos de acessibilidade próprios para pessoas com deficiência;”
- `LC214.art128.incV`: “V - medicamentos;”
- `LC214.art128.incVI`: “VI - alimentos destinados ao consumo humano;”
- `LC214.art128.incVII`: “VII - produtos de higiene pessoal e limpeza majoritariamente consumidos por famílias de baixa renda;”
- `LC214.art128.incVIII`: “VIII - produtos agropecuários, aquícolas, pesqueiros, florestais e extrativistas vegetais in natura;”
- `LC214.art128.incIX`: “IX - insumos agropecuários e aquícolas;”
- `LC214.art128.incX`: “X - produções nacionais artísticas, culturais, de eventos, jornalísticas e audiovisuais;”
- `LC214.art128.incXI`: “XI - comunicação institucional;”
- `LC214.art128.incXII`: “XII - atividades desportivas; e”
- `LC214.art128.incXIII`: “XIII - bens e serviços relacionados à soberania e à segurança nacional, à segurança da informação e à segurança cibernética.”

**Justificativa:** O art. 128 da LC 214/2025 reduz em 60% as alíquotas do IBS e da CBS incidentes sobre operações com os bens e serviços listados em seus incisos. Na data de referência, o dispositivo está vigente, pois seus efeitos se iniciam em 2026-01-01. A lista inclui educação, saúde, dispositivos médicos, acessibilidade, medicamentos, alimentos, higiene e limpeza, produtos agropecuários in natura, insumos agropecuários, produções artísticas e culturais, comunicação institucional, atividades desportivas e bens e serviços de soberania e segurança.

**Decisão:** confirmar

---

## c098 · H14

**Pergunta:** Quais são as competências administrativas do Comitê Gestor do IBS?

**Existe resposta no corpus:** `sim`

**Dispositivos esperados:** `CF.art156-B` (CF, art. 156-B); `CF.art156-B.incI` (CF, art. 156-B, I); `CF.art156-B.incII` (CF, art. 156-B, II); `CF.art156-B.incIII` (CF, art. 156-B, III)

**Trechos citados (literais do corpus):**

- `CF.art156-B`: “Art. 156-B. Os Estados, o Distrito Federal e os Municípios exercerão de forma integrada, exclusivamente por meio do Comitê Gestor do Imposto sobre Bens e Serviços, nos termos e limites estabelecidos nesta Constituição e em lei complementar, as seguintes competências administrativas relativas ao imposto de que trata o art. 156-A:”
- `CF.art156-B.incI`: “I - editar regulamento único e uniformizar a interpretação e a aplicação da legislação do imposto;”
- `CF.art156-B.incII`: “II - arrecadar o imposto, efetuar as compensações e distribuir o produto da arrecadação entre Estados, Distrito Federal e Municípios;”
- `CF.art156-B.incIII`: “III - decidir o contencioso administrativo.”

**Justificativa:** O art. 156-B da Constituição atribui aos Estados, ao Distrito Federal e aos Municípios o exercício integrado, exclusivamente por meio do Comitê Gestor do IBS, das competências administrativas relativas ao imposto. Os incisos I a III especificam essas competências: editar regulamento único e uniformizar a interpretação e a aplicação da legislação; arrecadar, efetuar compensações e distribuir o produto da arrecadação; e decidir o contencioso administrativo. O dispositivo tem efeitos desde 2023-12-21 e alcança a data de referência de 2026-11-13.

**Decisão:** confirmar

---

## c099 · H14

**Pergunta:** Quais regimes específicos de tributação estão previstos para IBS e CBS?

**Existe resposta no corpus:** `sim`

**Dispositivos esperados:** `CF.art156-A.par6` (CF, art. 156-A, § 6º); `CF.art156-A.par6.incI` (CF, art. 156-A, § 6º, I); `CF.art156-A.par6.incII` (CF, art. 156-A, § 6º, II); `CF.art156-A.par6.incIII` (CF, art. 156-A, § 6º, III); `CF.art156-A.par6.incIV` (CF, art. 156-A, § 6º, IV); `CF.art156-A.par6.incV` (CF, art. 156-A, § 6º, V); `CF.art156-A.par6.incVI` (CF, art. 156-A, § 6º, VI); `CF.art195.par16` (CF, art. 195, § 16)

**Trechos citados (literais do corpus):**

- `CF.art156-A.par6`: “§ 6º Lei complementar disporá sobre regimes específicos de tributação para:”
- `CF.art156-A.par6.incI`: “I - combustíveis e lubrificantes sobre os quais o imposto incidirá uma única vez, qualquer que seja a sua finalidade, hipótese em que:”
- `CF.art156-A.par6.incII`: “II - serviços financeiros, operações com bens imóveis, planos de assistência à saúde e concursos de prognósticos, podendo prever:”
- `CF.art156-A.par6.incIII`: “III - sociedades cooperativas, que será optativo, com vistas a assegurar sua competitividade, observados os princípios da livre concorrência e da isonomia tributária, definindo, inclusive:”
- `CF.art156-A.par6.incIV`: “IV - serviços de hotelaria, parques de diversão e parques temáticos, agências de viagens e de turismo, bares e restaurantes, atividade esportiva desenvolvida por Sociedade Anônima do Futebol e aviação regional, podendo prever hipóteses de alterações nas alíquotas, nas bases de cálculo e nas regras de creditamento, admitida a não aplicação do disposto no § 1º, V a VIII;”
- `CF.art156-A.par6.incV`: “V - operações alcançadas por tratado ou convenção internacional, inclusive referentes a missões diplomáticas, repartições consulares, representações de organismos internacionais e respectivos funcionários acreditados;”
- `CF.art156-A.par6.incVI`: “VI - serviços de transporte coletivo de passageiros rodoviário intermunicipal e interestadual, ferroviário e hidroviário, podendo prever hipóteses de alterações nas alíquotas e nas regras de creditamento, admitida a não aplicação do disposto no § 1º, V a VIII.”
- `CF.art195.par16`: “§ 16. Aplica-se à contribuição prevista no inciso V do caput o disposto no art. 156-A, § 1º, I a VI, VIII, X a XIII, § 3º, § 5º, II a VI e IX, e §§ 6º a 11 e 13.”

**Justificativa:** O art. 156-A, § 6º, da Constituição, com efeitos desde 2023, elenca os regimes específicos de tributação do IBS. Seus incisos I a VI indicam combustíveis e lubrificantes; serviços financeiros, operações com bens imóveis, planos de assistência à saúde e concursos de prognósticos; sociedades cooperativas; hotelaria, parques, turismo, bares e restaurantes, SAF e aviação regional; operações de tratados ou convenções internacionais; e transporte coletivo de passageiros. O art. 195, § 16, estende à CBS o disposto nos §§ 6º a 11 do art. 156-A, de modo que esses regimes específicos também se aplicam à CBS.

**Decisão:** confirmar

---

## c100 · H14

**Pergunta:** Quais produções artísticas e culturais estão listadas com redução de 60%?

**Existe resposta no corpus:** `sim`

**Dispositivos esperados:** `LC214.art139` (LC 214/2025, art. 139); `LC214.art139.incI` (LC 214/2025, art. 139, I); `LC214.art139.incII` (LC 214/2025, art. 139, II); `LC214.art139.incIII` (LC 214/2025, art. 139, III); `LC214.art139.incIV` (LC 214/2025, art. 139, IV); `LC214.art139.incV` (LC 214/2025, art. 139, V); `LC214.art139.incVI` (LC 214/2025, art. 139, VI); `LC214.art139.incVII` (LC 214/2025, art. 139, VII); `LC214.art139.incVIII` (LC 214/2025, art. 139, VIII)

**Trechos citados (literais do corpus):**

- `LC214.art139`: “Ficam reduzidas em 60% (sessenta por cento) as alíquotas do IBS e da CBS incidentes sobre o fornecimento dos bens e serviços listados no Anexo X desta Lei Complementar, com a especificação das respectivas classificações da NCM/SH e NBS, nos casos relacionados com as seguintes produções nacionais artísticas, culturais, de eventos, jornalísticas e audiovisuais:”
- `LC214.art139.incI`: “I - espetáculos teatrais, circenses e de dança;”
- `LC214.art139.incII`: “II - shows musicais;”
- `LC214.art139.incIII`: “III - desfiles carnavalescos ou folclóricos;”
- `LC214.art139.incIV`: “IV - eventos acadêmicos e científicos, como congressos, conferências e simpósios;”
- `LC214.art139.incV`: “V - feiras de negócios;”
- `LC214.art139.incVI`: “VI - exposições, feiras, galerias e mostras culturais, artísticas e literárias;”
- `LC214.art139.incVII`: “VII - programas de auditório ou jornalísticos, filmes, documentários, séries, novelas, entrevistas e clipes musicais; e”
- `LC214.art139.incVIII`: “VIII - obras de arte.”

**Justificativa:** O art. 139 da LC 214/2025 reduz em 60% as alíquotas do IBS e da CBS sobre bens e serviços relacionados a produções nacionais artísticas, culturais, de eventos, jornalísticas e audiovisuais. Seus incisos listam as produções alcançadas: espetáculos teatrais, circenses e de dança; shows musicais; desfiles carnavalescos ou folclóricos; eventos acadêmicos e científicos; feiras de negócios; exposições, feiras, galerias e mostras culturais, artísticas e literárias; programas de auditório ou jornalísticos, filmes, documentários, séries, novelas, entrevistas e clipes musicais; e obras de arte. O dispositivo tem efeitos desde 2026-01-01, alcançando a data de referência.

**Decisão:** confirmar

---
