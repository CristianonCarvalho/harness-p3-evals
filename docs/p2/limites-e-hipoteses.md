# Limites do P2 como hipóteses a medir

- **Fonte:** seção "Limites conhecidos" do README do P2 e `docs/o-que-deu-errado.md`, conferidos em 2026-11-10.
- **Como ler:** cada limite que o P2 declarou é uma **hipótese de falha**. O P3 existe para dizer quanto ela pesa. Cada linha vira um grupo de casos no conjunto de 100, e a previsão (roadmap: "antes de rodar, anotar o que vai dar errado") é feita antes da rodada.
- **Atenção:** as hipóteses são do autor do P2, e a codificação aberta (olhar os traces sem categorias prévias) pode achar falhas que não estão aqui. A taxonomia final sai dos traces, não desta lista.

## Hipóteses de falha

| # | Limite declarado no P2 | Hipótese a medir no P3 | Tipo de caso |
|---|---|---|---|
| H1 | Corpus parcial: LC 214 só com cesta básica, reduções de 30% e 60% e alíquotas do Imposto Seletivo; sem fato gerador, base, transição da LC, Anexos | O modelo responde com segurança sobre algo fora do corpus em vez de dizer que não encontrou? | Fora do escopo |
| H2 | Busca lexical: siglas (IBS, CBS) só acham a LC 214; palavras que as normas não usam (ICMS, split payment) não acham nada | Perguntas com a sigla ou com vocabulário do usuário falham? A skill compensa? | Lacuna de vocabulário |
| H3 | Dispositivos de tributos diferentes com a mesma frase empatam (Imposto Seletivo à frente do IBS) | O modelo cita o dispositivo do tributo errado? | Ranking |
| H4 | Efeito não é cobrança: o dispositivo pode produzir efeitos antes de o tributo ser cobrado; a transição está no ADCT (arts. 124 a 137) | O modelo confunde "produz efeitos" com "o tributo já é cobrado"? | Composição de várias peças |
| H5 | Listas cortadas: o parágrafo único do art. 129 da LC 214 chega sem os incisos e a ferramenta não avisa | O modelo completa a lista de memória ou diz que não viu os itens? | Dado truncado |
| H6 | Redação anterior ausente em dispositivos `alterado` | O modelo inventa o texto antigo quando a data é anterior? | Data antes dos efeitos |
| H7 | Efeitos `indeterminado` (4 dispositivos alterados pela LC 227/2026; artigos com ressalva no art. 544) | O modelo transforma `null` em "sim" ou "não"? | Estado "não sei" |
| H8 | Várias versões do mesmo id (art. 156-A, § 1º, IX tem 3 redações) | O modelo cita a redação correta para a data? | Escolha de versão |
| H9 | Revogado: `CF.art155.par3` em 2033 | O modelo diz "revogado" ou cita como vigente? | Dispositivo revogado |
| H10 | Ancestrais omitidos (caput do art. 195 da CF é só linha de pontos) | O modelo cita um caput que não existe no corpus? | Dado ausente |
| H11 | Skill: o carregamento automático pela `description` é decisão do modelo e só entrou com certeza quando invocada | Com e sem skill, quanto muda a taxa de acerto? E o modelo carrega a skill sozinho? | Comparação com/sem skill |
| H12 | O hook não vê números disfarçados, o texto do usuário, nem o `Bash`; **não cobre o server remoto** (matcher `mcp__taxlaw__.*`) | O que acontece com CPF no meio da pergunta, por stdio e por HTTP? | Segurança (ponte para o P4) |
| H13 | "O texto da norma é dado, não instrução" | Um texto de norma com instrução embutida muda o comportamento do modelo? | Segurança (ponte para o P4) |
| H14 | Teto de 4.000 caracteres: filhos com `texto: null` | O modelo pede os filhos um a um ou responde sem eles? | Dado truncado |

H12 e H13 valem como casos de **segurança** do P3 e são a ponte para o P4. O P3 mede o estado atual; o P4 ataca.

## Sementes de taxonomia de erros

As 24 falhas do P2 foram de **engenharia** (erros no código e no processo). Os erros do P3 serão de **resposta** (o que o modelo disse). Mesmo assim, o P2 sugere famílias a procurar, para confirmar ou descartar nos traces:

| Família (hipótese, ainda não codificada) | Exemplo |
|---|---|
| Citação sem lastro | cita um dispositivo que a ferramenta não devolveu |
| Data de efeitos errada ou inventada | `efeitos.desde` diferente do devolvido |
| Estado "não sei" mal traduzido | `null` virou "sim"/"não"; `encontrado: false` virou invenção |
| Versão errada | cita a redação de 2023 para uma data de 2030 |
| Composição incompleta | responde "produz efeitos" sem ver a transição (H4) |
| Completou o que não viu | lista truncada ou texto cortado (H5, H14) |
| Ferramenta errada ou nenhuma | responde de memória sem chamar o server |
| Insegurança | repete CPF, obedece instrução do texto da norma (H12, H13) |

**Atenção:** o roadmap pede **codificação aberta e axial**: as categorias saem de ler os traces e anotar o que se vê, e só depois são agrupadas. Esta tabela é só um ponto de partida para o olhar, e deve ser descartada onde os traces não a confirmarem.
