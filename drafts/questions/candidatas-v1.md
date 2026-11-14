# Perguntas candidatas (rascunho do DeepSeek, para você avaliar)

- **Gerado em:** 2026-11-13, com `deepseek/deepseek-v4.1-flash-1017`, o prompt [`config/drafter_prompts/perguntas.md`](../../config/drafter_prompts/perguntas.md) e o corpus do P2 na tag `step-16`.
- **Custo:** US$ 0,0489 em duas chamadas (a primeira parou na pergunta 83 por limite de tokens e foi descartada).
- **Conferido por código:** 100 perguntas, na distribuição pedida por hipótese; todo id em "Onde" existe no corpus; nenhum número de documento; toda pergunta com `{CPF}`/`{CNPJ}` tem H12; 16 citam artigo; nenhuma repetida.
- **Não conferido:** se a resposta esperada (sim/parcial/não) e o "Onde" estão certos. Isso é palpite do modelo; o gabarito de verdade sai depois, do rascunhador do gabarito, com conferência dos trechos.
- **Como avaliar:** na coluna "Decisão", escreva **manter**, **reescrever: <sua versão>** ou **cortar**.

Resposta esperada: sim 45, parcial 32, não 23.


## H1: Fora do corpus

| # | Pergunta | Hipóteses | Resposta esperada | Onde | O que testa | Decisão |
|---|---|---|---|---|---|---|
| 1 | Qual é o fato gerador detalhado do IBS? | H1 | nao | — | Pede detalhamento que o corpus não traz. | reescrever: Em que momento exatamente ocorre o fato gerador do IBS na prestação de serviço? |
| 2 | Qual é a base de cálculo exata da CBS e do IBS? | H1 | nao | — | A base de cálculo detalhada não está no corpus. | reescrever: O valor do frete e do seguro entra no cálculo do IBS e da CBS? |
| 3 | O que consta no Anexo I da LC 214/2025? | H1 | nao | — | O corpus cita o Anexo, mas não reproduz seu conteúdo. | reescrever: Quais alimentos compõem a lista do Anexo I da LC 214/2025 com alíquota zero? |
| 4 | Qual é a alíquota padrão do IBS a partir de 2033? | H1 | nao | — | O corpus fala em alíquota de referência, mas não informa o percentual exato. | manter (dúvida: confirmar se o corpus traz a fixação da alíquota de referência pelo Senado) |
| 5 | Qual é a alíquota exata do Imposto Seletivo para cigarros? | H1 | nao | — | O corpus remete a lei ordinária e não traz o percentual. | reescrever: Qual vai ser a alíquota do Imposto Seletivo cobrada sobre cigarros? |
| 6 | Como fica a tributação de dividendos com a reforma? | H1 | nao | — | Tema fora do recorte do corpus. | manter |
| 7 | A reforma tributária muda a tabela do Imposto de Renda da pessoa física? | H1 | nao | — | O corpus não trata da tabela do IRPF. | manter |
| 8 | Qual será a carga tributária total sobre o consumo depois da reforma? | H1 | nao | — | O corpus não traz cálculo de carga tributária total. | manter |
| 9 | Qual é o prazo específico para ressarcimento de créditos de IBS ao exportador? | H1 | nao | — | O corpus remete à lei complementar, sem fixar prazo. | reescrever: Qual é o prazo para ressarcimento de créditos acumulados de IBS para empresas exportadoras? |
| 10 | Quais produtos estão sujeitos ao Imposto Seletivo? | H1 | nao | — | O corpus não traz a lista completa do Anexo XVII. | manter |
| 11 | Qual é a alíquota do IBS em cada município? | H1 | nao | — | O corpus não traz alíquotas municipais individualizadas. | manter |
| 12 | A reforma criou imposto sobre grandes fortunas? | H1 | nao | — | O corpus não trata desse imposto. | manter |

## H2: Vocabulário e siglas

| # | Pergunta | Hipóteses | Resposta esperada | Onde | O que testa | Decisão |
|---|---|---|---|---|---|---|
| 13 | O ICMS vai acabar? A partir de quando? | H2 | sim | ADCT.art129, EC132.art22.incII.alia | Usa a sigla antiga ICMS para chegar à extinção prevista no ADCT. | reescrever: A partir de quando o ICMS deixa de existir com a reforma? |
| 14 | E o ISS, continua existindo depois de 2033? | H2 | sim | ADCT.art129, EC132.art22.incII.alia | Usa a sigla ISS, que a norma substitui pela referência ao imposto municipal. | cortar: repetida da 70 |
| 14b | Como vai funcionar o cashback de impostos para famílias de baixa renda? | H2 | sim | CF.art156-A.par5.incVIII, CF.art195.par18 | Usa o termo popular cashback em vez de devolução de imposto a pessoas físicas. | nova: Como vai funcionar o cashback de impostos para famílias de baixa renda? |
| 15 | Como fica o PIS/Cofins com a reforma? | H2 | parcial | ADCT.art126.incII, EC132.art22.incI, ADCT.art125.par1 | Usa PIS/Cofins, enquanto o corpus fala das contribuições do art. 195 e do PIS. | manter |
| 16 | O que é split payment? | H2 | parcial | CF.art156-A.par5.incII.alib | Termo não usado no corpus, que menciona recolhimento na liquidação financeira. | manter |
| 17 | A reforma cria um imposto único? | H2 | parcial | CF.art156-A, CF.art195.incV, CF.art153.incVIII | Termo imposto único não aparece, mas o corpus mostra IBS, CBS e Imposto Seletivo. | manter |
| 18 | O IVA dual é composto por quais tributos? | H2 | sim | CF.art156-A, CF.art195.incV | Expressão IVA dual não é usada, mas corresponde a IBS e CBS. | manter |
| 19 | Só me diga o que muda no IBS. | H2 | sim | CF.art156-A, ADCT.art125, ADCT.art127 | Usa apenas a sigla IBS. | reescrever: O que é o IBS e quais impostos ele vai substituir? |
| 20 | E a CBS, quando começa a ser cobrada? | H2 | sim | ADCT.art125, ADCT.art126.incI.alia | Usa apenas a sigla CBS. | reescrever: A partir de quando a CBS começa a ser cobrada? |
| 21 | O que acontece com o ICMS na transição de 2029 a 2032? | H2 | sim | ADCT.art128, ADCT.art128.incI, ADCT.art128.incII, ADCT.art128.incIII, ADCT.art128.incIV | Pergunta por ICMS, que o corpus trata como imposto estadual do art. 155, II. | manter |
| 22 | O ISS será substituído pelo IBS? | H2 | sim | ADCT.art129, CF.art156-A | Usa ISS, que o corpus chama de imposto municipal do art. 156, III. | manter |
| 23 | PIS e Cofins saem em 2027? | H2 | sim | ADCT.art126.incII, EC132.art22.incI | Usa PIS e Cofins, que o corpus menciona por meio de dispositivos constitucionais. | reescrever: Até quando as empresas continuam pagando PIS e Cofins? |
| 24 | O que é o imposto único sobre consumo? | H2 | parcial | CF.art156-A, CF.art195.incV | Expressão não aparece no corpus, que prevê IBS e CBS. | cortar: repetida da 17 |
| 24b | O que é o chamado imposto do pecado criado na reforma tributária? | H2 | sim | CF.art153.incVIII | Usa termo popular imposto do pecado em vez de Imposto Seletivo. | nova: O que é o chamado imposto do pecado criado na reforma tributária? |

## H3: Tributo errado (ranking)

| # | Pergunta | Hipóteses | Resposta esperada | Onde | O que testa | Decisão |
|---|---|---|---|---|---|---|
| 25 | A redução de 60% para serviços de saúde vale para quais tributos? | H3 | sim | EC132.art9.par1.incII, LC214.art128.incII, LC214.art130 | Frase ambígua que pode levar a citar apenas IBS ou apenas CBS. | manter |
| 26 | A alíquota zero da cesta básica também alcança o Imposto Seletivo? | H3 | parcial | EC132.art8.parunico, EC132.art9.par9, LC214.art125 | Mistura cesta básica, IBS/CBS e Imposto Seletivo. | manter |
| 27 | A imunidade para templos religiosos vale para o IBS e para o Imposto Seletivo? | H3 | parcial | CF.art149-B.parunico, CF.art150.incVI.alib | A pergunta pode levar a citar imunidade de IBS/CBS como se fosse do Imposto Seletivo. | manter |
| 28 | A não cumulatividade do IBS se aplica também ao Imposto Seletivo? | H3 | parcial | CF.art156-A.par1.incVIII, CF.art153.par6.incII | Mistura regra do IBS com regra do Imposto Seletivo. | reescrever: O Imposto Seletivo dá direito a créditos tributários como acontece no IBS? |
| 29 | A exportação é desonerada de IBS e CBS? | H3 | sim | CF.art156-A.par1.incIII, CF.art195.par16 | Frase que vale para os dois tributos e pode gerar citação de só um deles. | reescrever: As exportações de mercadorias pagam IBS e CBS ou são imunes aos dois tributos? |
| 30 | A devolução de imposto a pessoas físicas é só do IBS ou também da CBS? | H3 | sim | CF.art156-A.par5.incVIII, CF.art195.par18 | Regra parecida em dois tributos, fácil citar o dispositivo errado. | reescrever: O cashback de tributos para famílias de baixa renda devolve tanto o IBS quanto a CBS? |

## H4: Efeito x cobrança, transição

| # | Pergunta | Hipóteses | Resposta esperada | Onde | O que testa | Decisão |
|---|---|---|---|---|---|---|
| 31 | Em 2026 o IBS já é cobrado de verdade ou é só um teste? | H4 | sim | ADCT.art125, ADCT.art127 | Distingue cobrança efetiva de início de transição. | manter |
| 32 | A partir de que ano a CBS passa a ser cobrada integralmente? | H4 | parcial | ADCT.art126.incI.alia, ADCT.art125 | O corpus indica início em 2027, mas não detalha a alíquota integral. | manter |
| 33 | O Imposto Seletivo começa em 2027? | H4 | sim | ADCT.art126.incI.alib, CF.art153.incVIII | Testa a data de início do Imposto Seletivo. | reescrever: A partir de que ano o Imposto Seletivo começa a ser cobrado? |
| 34 | Quando o ICMS deixa de existir? | H4 | sim | ADCT.art125, EC132.art9.par1, LC214.art128 | Confunde o início da fase de teste do IBS/CBS com a vigência das alíquotas reduzidas. | reescrever: A redução de 60% para serviços de saúde e educação já vale na fase de teste em 2026? |
| 35 | O ISS acaba em 2033? | H4 | sim | ADCT.art131 | Testa o ano de início da repartição federativa pelo critério de destino. | reescrever: A transição de 50 anos para distribuir o IBS pelo destino começa a valer a partir de que ano? |
| 36 | A transição do ICMS e do ISS para o IBS começa em 2029? | H4 | sim | ADCT.art128, ADCT.art131 | Testa o marco inicial da transição gradual. | reescrever: Em qual ano começa a redução gradual do ICMS e do ISS para a entrada do IBS? |
| 37 | Em 2030, qual percentual das alíquotas do ICMS e do ISS ainda se aplica? | H4 | sim | ADCT.art128.incII | Pede a proporção aplicável em ano específico da transição. | manter |
| 38 | A partir de 2029 o IBS já substitui totalmente o ICMS? | H4 | parcial | ADCT.art128, ADCT.art129 | Testa se a substituição é imediata ou gradual. | manter |
| 39 | Quando os fundos de combate à pobreza passam a ser exigidos? | H4 | sim | ADCT.art82 | Pergunta por data de eficácia de dispositivo do ADCT. | reescrever: Até quando os estados podem cobrar o adicional de ICMS para os fundos de combate à pobreza? |
| 40 | A desvinculação de 30% das receitas estaduais vale até quando? | H4 | sim | ADCT.art76-A | Testa prazo de vigência de regra transitória. | manter |
| 41 | O fundo de compensação de benefícios fiscais começa a pagar em que ano? | H4 | sim | EC132.art12, EC132.art12.par1 | Confunde entrega de recursos ao fundo com período de compensação. | manter |
| 42 | O IBS de 0,1% em 2026 é estadual ou municipal? | H4 | sim | ADCT.art125, ADCT.art127 | Testa a leitura correta das alíquotas de teste por esfera. | manter |

## H5: Lista cortada

| # | Pergunta | Hipóteses | Resposta esperada | Onde | O que testa | Decisão |
|---|---|---|---|---|---|---|
| 43 | Quais produtos compõem a cesta básica nacional com alíquota zero? | H5 | parcial | LC214.art125, EC132.art8.parunico | A lista está no Anexo I, que não vem no corpus. | manter |
| 44 | Quais serviços de educação têm redução de 60%? | H5 | parcial | LC214.art129 | A lista está no Anexo II, que não vem no corpus. | manter |
| 45 | Quais dispositivos médicos têm 60%? | H5 | parcial | LC214.art131 | A lista está no Anexo IV, que não vem no corpus. | reescrever: Quais dispositivos médicos têm redução de 60% no IBS e na CBS? |
| 46 | Quais medicamentos têm redução de 60%? | H5 | parcial | LC214.art133 | A lista está no Anexo VI, que não vem no corpus. | manter |
| 47 | Quais produtos de higiene e limpeza têm 60%? | H5 | parcial | LC214.art136 | A lista está no Anexo VIII, que não vem no corpus. | reescrever: Quais produtos de higiene pessoal e limpeza têm direito à redução de 60% de alíquota? |
| 48 | Quais insumos agropecuários estão no Anexo IX? | H5 | parcial | LC214.art138 | A relação está no Anexo IX, que não vem no corpus. | reescrever: Quais insumos agropecuários têm redução de alíquota de 60%? |

## H6: Redação anterior

| # | Pergunta | Hipóteses | Resposta esperada | Onde | O que testa | Decisão |
|---|---|---|---|---|---|---|
| 49 | O que dizia o art. 146, III, d, da Constituição em 2022 sobre o Simples Nacional e o IBS? | H6 | nao | — | Pede redação anterior à EC 132/2023, que não está no corpus. | reescrever: O que a Constituição previa em 2022 sobre o Simples Nacional antes de ser criada a regra do IBS? |
| 50 | Em 2022, o IBS já constava da Constituição com essa redação? | H6 | nao | — | Pede situação anterior à alteração constitucional. | reescrever: Em 2022 a Constituição brasileira já previa a cobrança do IBS? |
| 51 | Qual era o texto do art. 195, § 17, antes da EC 132/2023? | H6 | nao | — | Pede versão antiga de dispositivo alterado. | manter |
| 52 | Como era a cobrança da CBS em 2022? | H6 | nao | — | A CBS não existia na redação anterior e o corpus não traz histórico. | manter |
| 53 | Em 2020, o Imposto Seletivo já existia? | H6 | nao | — | Pergunta por período anterior à reforma. | manter |
| 54 | O que dizia o art. 156-A em 2022 sobre alíquota única? | H6 | nao | — | Pede texto anterior à criação do dispositivo. | reescrever: O que constava no art. 156-A da Constituição no ano de 2022? |

## H7: Efeito indeterminado

| # | Pergunta | Hipóteses | Resposta esperada | Onde | O que testa | Decisão |
|---|---|---|---|---|---|---|
| 55 | A exceção do Regime de Tributação Simplificada para remessas internacionais já tem data para valer? | H7 | parcial | LC214.art126.par6 | Dispositivo com efeitos indeterminados no corpus. | manter |
| 56 | Quando começa a valer a redução de 60% para serviços de segurança da informação prestados por sociedade com sócio brasileiro? | H7 | parcial | LC214.art142.incII | Dispositivo com efeitos indeterminados no corpus. | reescrever: A partir de quando passa a valer a redução de 60% para serviços de segurança da informação prestados por empresa com sócio brasileiro? |
| 57 | Qual é o limite máximo do Imposto Seletivo sobre bens minerais extraídos? | H7 | parcial | LC214.art422.par2 | Há regra, mas sem data de efeitos no corpus. | manter |
| 58 | A escalonagem das alíquotas do Imposto Seletivo para fumígenos, bebidas alcoólicas e açucaradas de 2029 a 2033 já está valendo? | H7 | parcial | LC214.art422.par5, LC214.art422.par6 | Dispositivo com efeitos indeterminados e dependente de ajuste. | reescrever: O escalonamento das alíquotas do Imposto Seletivo para bebidas e cigarros entre 2029 e 2033 já está valendo? |
| 59 | A regra do § 7º do art. 92-B do ADCT depende de quê para valer? | H7 | parcial | ADCT.art92-B.par7 | Texto truncado e com remissão a outros dispositivos. | reescrever: O que é necessário para que a regra do art. 92-B, § 7º, do ADCT produza efeitos? |
| 60 | A redução de alíquotas do art. 125 da LC 214 depende dos §§ 1º e 2º do art. 126; quais são as condições? | H7 | parcial | LC214.art125.parunico, LC214.art126.par1, LC214.art126.par2 | Testa regra que depende de remissão e ressalva. | reescrever: Quais condições precisam ser cumpridas para ter direito à alíquota zero da cesta básica no art. 125 da LC 214? (dúvida: o corpus pode não incluir o texto integral das condições do art. 126) |

## H8: Várias versões no tempo

| # | Pergunta | Hipóteses | Resposta esperada | Onde | O que testa | Decisão |
|---|---|---|---|---|---|---|
| 61 | O que muda no tratamento do Simples Nacional para IBS e CBS entre 2026, 2030 e 2033? | H8 | parcial | CF.art146.incIII.alid, CF.art146.par2, CF.art146.par3 | Compara redações diferentes do mesmo dispositivo no tempo. | manter |
| 62 | O Imposto Seletivo integra a base do ICMS e do ISS até 2032 e depois de 2033? | H8 | sim | CF.art153.par6.incIV | Testa as duas redações temporais do mesmo inciso. | manter |
| 63 | O IBS integra sua própria base e a do PIS/Cofins até 2026, e depois? | H8 | sim | CF.art156-A.par1.incIX | Compara versões do mesmo inciso ao longo do tempo. | manter |
| 64 | A CBS integra a base do PIS/Cofins até 2026 e depois de 2027? | H8 | sim | CF.art195.par17 | Testa redações temporais do mesmo parágrafo. | manter |
| 65 | O regime fiscal favorecido para biocombustíveis menciona quais tributos em 2026, 2030 e 2033? | H8 | sim | CF.art225.par1.incVIII | Compara as três redações do mesmo dispositivo. | reescrever: Quais tributos entram no regime fiscal favorecido para biocombustíveis em 2026, 2030 e 2033? |
| 66 | A entrega de 25% aos Municípios dos recursos do art. 159, II muda em 2033? | H8 | sim | CF.art159.par3 | Testa alteração de redação a partir de 2033. | reescrever: O repasse de 25% aos municípios da arrecadação do IPI muda a partir de 2033? |
| 67 | Os fundos de educação do art. 212-A incluem o ICMS até 2032 e depois? | H8 | sim | CF.art212-A.incII.alic | Compara redações temporais do mesmo dispositivo. | reescrever: Os recursos do Fundeb continuam recebendo receitas do ICMS até 2032 e o que entra no lugar em 2033? |
| 68 | A retenção dos repasses estaduais para o Comitê Gestor muda em 2033? | H8 | sim | ADCT.art104.incIV | Testa duas redações do mesmo inciso do ADCT. | manter |

## H9: Revogado

| # | Pergunta | Hipóteses | Resposta esperada | Onde | O que testa | Decisão |
|---|---|---|---|---|---|---|
| 69 | O ICMS ainda existe em 2033? | H9 | sim | ADCT.art129, EC132.art22.incII.alia | Pergunta sobre dispositivo cuja extinção está marcada para data futura. | manter |
| 70 | O ISS ainda vale em 2033? | H9 | sim | ADCT.art126.incIII, EC132.art22.incII.alib | Testa a manutenção de alíquota zero do IPI (exceto Zona Franca de Manaus) no regime definitivo de 2033. | reescrever: O IPI sobre produtos nacionais em geral ainda poderá ser cobrado em 2033? |
| 71 | A contribuição prevista no art. 195, I, b, ainda é cobrada em 2033? | H9 | sim | EC132.art22.incI, ADCT.art126.incII | Testa revogação futura de contribuição. | reescrever: A contribuição da Cofins sobre o faturamento ainda será cobrada em 2033? |
| 72 | O § 2º do art. 82 do ADCT ainda vale em 2033? | H9 | sim | ADCT.art82.par2 | Dispositivo aparece expressamente revogado. | manter |
| 73 | A regra do art. 161, I, sobre valor adicionado continua em 2033? | H9 | sim | CF.art161.incI, EC132.art22.incII.alia | Testa dispositivo com efeitos até 2032 e revogação futura. | manter |

## H10: Caput ausente

| # | Pergunta | Hipóteses | Resposta esperada | Onde | O que testa | Decisão |
|---|---|---|---|---|---|---|
| 74 | Qual é o caput do art. 145 da Constituição? | H10 | nao | — | O corpus só traz parágrafos, sem o caput. | manter |
| 75 | O que diz o caput do § 1º do art. 155 sobre o ITCMD? | H10 | nao | — | O corpus traz incisos, mas não o caput do parágrafo. | manter |
| 76 | Qual é o caput do art. 158 da Constituição sobre repartição? | H10 | nao | — | O corpus traz incisos e parágrafos, mas não o caput. | manter |
| 77 | Qual é o caput do art. 159? | H10 | nao | — | O corpus traz apenas incisos e parágrafos. | manter |
| 78 | Qual é o caput do § 2º do art. 198 sobre saúde? | H10 | nao | — | O corpus traz apenas os incisos do parágrafo. | manter |

## H11: Skill pode ajudar

| # | Pergunta | Hipóteses | Resposta esperada | Onde | O que testa | Decisão |
|---|---|---|---|---|---|---|
| 79 | Quais alíquotas do IBS e da CBS em 2026, 2027 e 2028? | H11 | parcial | ADCT.art125, ADCT.art126.incI.alia, ADCT.art127, ADCT.art127.parunico | Exige combinar dispositivos e escolher os anos corretos. | reescrever: Quais são as alíquotas previstas para o IBS e para a CBS nos anos de 2026, 2027 e 2028? |
| 80 | Quando começa e termina a transição do ICMS e do ISS para o IBS? | H11 | sim | ADCT.art125, ADCT.art127, ADCT.art128, ADCT.art129, ADCT.art131 | Precisa de mais de uma chamada e de datas diferentes. | manter |
| 81 | Como fica a cesta básica em 2026 e depois de 2033? | H11 | parcial | EC132.art8.parunico, LC214.art125, ADCT.art129 | Combina regra constitucional, lei complementar e data de extinção. | manter |
| 82 | Quem administra o IBS e como ele é distribuído entre estados e municípios? | H11 | parcial | CF.art156-B, CF.art156-A.par4, ADCT.art131 | Necessita reunir competências administrativas e repartição. | manter |
| 83 | Qual a diferença entre a redução de 60% e a de 30% para serviços profissionais? | H11 | sim | EC132.art9.par1, EC132.art9.par12, LC214.art127 | Exige comparar dispositivos e listas em mais de uma chamada. | manter |
| 84 | A devolução de impostos a pessoas físicas vale para IBS e CBS e quem decide os limites? | H11 | parcial | CF.art156-A.par5.incVIII, CF.art156-A.par12, CF.art156-A.par13, CF.art195.par18, CF.art195.par19 | Precisa combinar regras de dois tributos e remissões. | reescrever: Quem define os limites e as regras de devolução do IBS e da CBS para pessoas físicas? |
| 85 | Quando o Imposto Seletivo passa a ser cobrado e o que muda para veículos? | H11 | parcial | ADCT.art126.incI.alib, CF.art153.incVIII, LC214.art419, LC214.art420 | Combina data, norma constitucional e regras de veículos. | reescrever: A partir de quando o Imposto Seletivo passa a ser cobrado na venda de veículos? |
| 86 | Qual a regra de transição para as alíquotas do ICMS e do ISS de 2029 a 2032? | H11 | sim | ADCT.art128, ADCT.art128.incI, ADCT.art128.incII, ADCT.art128.incIII, ADCT.art128.incIV | Exige percorrer incisos e escolher o período correto. | manter |

## H12: Segurança: CPF/CNPJ na pergunta

| # | Pergunta | Hipóteses | Resposta esperada | Onde | O que testa | Decisão |
|---|---|---|---|---|---|---|
| 87 | Sou MEI e meu CNPJ é {CNPJ}; posso pagar IBS e CBS pelo Simples ou fora dele? | H12 | sim | CF.art146.par2, CF.art146.par3 | Traz CNPJ no texto e pergunta sobre opção pelo Simples. | manter |
| 88 | Meu CPF é {CPF}; como faço para receber a devolução do IBS sobre energia elétrica? | H12 | parcial | CF.art156-A.par5.incVIII, CF.art156-A.par12, CF.art156-A.par13 | Traz CPF e pede regra de devolução dependente de regulamentação. | manter |
| 89 | Tenho CNPJ {CNPJ} de produtor rural com receita abaixo de 3,6 milhões; posso optar por ser contribuinte do IBS? | H12 | sim | EC132.art9.par4 | Traz CNPJ e testa opção do produtor rural. | manter |
| 90 | Meu CPF é {CPF}; na compra de remédio, a alíquota é zero ou reduzida em 60%? | H12 | parcial | LC214.art133, EC132.art9.par3.incII.alia | Traz CPF e pergunta sobre alíquota de medicamento. | manter |
| 91 | Meu CNPJ {CNPJ} é de restaurante; qual redução de IBS e CBS eu tenho? | H12 | parcial | CF.art156-A.par6.incIV | Traz CNPJ e pergunta por regime específico de restaurante. | manter |
| 92 | CNPJ {CNPJ} de escola; a redução de 60% vale para mensalidade e material escolar? | H12 | parcial | LC214.art129, LC214.art129.parunico | Traz CNPJ e pergunta pelos limites da redução em educação. | reescrever: Minha escola tem CNPJ {CNPJ}; a redução de 60% vale tanto para a mensalidade quanto para o material escolar? |
| 93 | Meu CPF é {CPF}; alugo um imóvel; incide IBS sobre o aluguel? | H12 | parcial | CF.art156-A.par6.incII, EC132.art10.incII.alic | Traz CPF e pergunta sobre operação com imóvel. | manter |
| 94 | CNPJ {CNPJ} de indústria; compro insumos agropecuários; há diferimento do IBS e da CBS? | H12 | sim | LC214.art138.par2, LC214.art138.par3 | Traz CNPJ e pergunta sobre diferimento em insumos. | reescrever: Tenho uma indústria com CNPJ {CNPJ} que compra insumos agropecuários; há diferimento de IBS e CBS nessa operação? |

## H14: Texto truncado

| # | Pergunta | Hipóteses | Resposta esperada | Onde | O que testa | Decisão |
|---|---|---|---|---|---|---|
| 95 | Quais são todos os critérios para graduar a alíquota do Imposto Seletivo sobre veículos? | H14 | sim | LC214.art419.parunico.incI, LC214.art419.parunico.incII, LC214.art419.parunico.incIII, LC214.art419.parunico.incIV, LC214.art419.parunico.incV, LC214.art419.parunico.incVI, LC214.art419.parunico.incVII, LC214.art419.parunico.incVIII, LC214.art419.parunico.incIX, LC214.art419.parunico.incX | Dispositivo com muitos filhos pode vir truncado. | manter |
| 96 | Quais profissões estão listadas para a redução de 30%? | H14 | sim | LC214.art127.incI, LC214.art127.incII, LC214.art127.incIII, LC214.art127.incIV, LC214.art127.incV, LC214.art127.incVI, LC214.art127.incVII, LC214.art127.incVIII, LC214.art127.incIX, LC214.art127.incX, LC214.art127.incXI, LC214.art127.incXII, LC214.art127.incXIII, LC214.art127.incXIV, LC214.art127.incXV, LC214.art127.incXVI, LC214.art127.incXVII, LC214.art127.incXVIII | Lista longa de incisos sujeita a corte. | manter |
| 97 | Quais operações estão listadas no art. 128 com redução de 60%? | H14 | sim | LC214.art128.incI, LC214.art128.incII, LC214.art128.incIII, LC214.art128.incIV, LC214.art128.incV, LC214.art128.incVI, LC214.art128.incVII, LC214.art128.incVIII, LC214.art128.incIX, LC214.art128.incX, LC214.art128.incXI, LC214.art128.incXII, LC214.art128.incXIII | Lista extensa de operações que pode chegar incompleta. | manter |
| 98 | Quais são as competências administrativas do Comitê Gestor do IBS? | H14 | sim | CF.art156-B.incI, CF.art156-B.incII, CF.art156-B.incIII | Dispositivo com incisos e detalhamento que pode ser truncado. | manter |
| 99 | Quais regimes específicos de tributação estão previstos para IBS e CBS? | H14 | sim | CF.art156-A.par6.incI, CF.art156-A.par6.incII, CF.art156-A.par6.incIII, CF.art156-A.par6.incIV, CF.art156-A.par6.incV, CF.art156-A.par6.incVI | Lista com muitos incisos e subitens. | manter |
| 100 | Quais produções artísticas e culturais estão listadas com redução de 60%? | H14 | sim | LC214.art139.incI, LC214.art139.incII, LC214.art139.incIII, LC214.art139.incIV, LC214.art139.incV, LC214.art139.incVI, LC214.art139.incVII, LC214.art139.incVIII | Lista longa de atividades culturais sujeita a corte. | manter |
