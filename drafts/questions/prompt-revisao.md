Você vai revisar 100 perguntas candidatas de um conjunto de avaliação. Elas estão no arquivo `drafts/questions/candidatas-v1.md`, numa tabela por hipótese, e foram rascunhadas por uma IA. Seu trabalho é decidir, para cada uma, se ela entra no conjunto como está, se entra reescrita, ou se sai.

## Para que servem essas perguntas

Elas serão feitas a um modelo de IA que responde sobre a reforma tributária consultando o texto da EC 132/2023 e de capítulos da LC 214/2025. Cada pergunta testa **um jeito específico de o sistema falhar** (a hipótese, de H1 a H14). Uma pergunta boa é aquela em que dá para dizer, depois, se a resposta do modelo acertou ou errou naquela hipótese. Você não precisa saber a resposta certa: o gabarito será rascunhado depois e conferido contra o texto da lei.

## Para cada pergunta, decida

Escreva na coluna **Decisão** uma destas três coisas:
- **manter**: a pergunta está boa como está;
- **reescrever: \<a sua versão\>**: a ideia serve, mas a frase não; escreva a versão final inteira;
- **cortar**: não serve (diga o motivo em poucas palavras, por exemplo "cortar: repetida da 14").

## O que faz uma pergunta servir

1. **Uma pessoa real perguntaria assim?** Um cidadão, um contador ou um pequeno empresário. Frases naturais, curtas, sem jargão de quem escreveu a lei. Se soar como prova de concurso ou como texto de IA, reescreva com as suas palavras.
2. **Ela testa a hipótese da linha?** Leia a coluna "O que testa". Se a pergunta não provoca aquele tipo de erro, corte ou reescreva para que provoque. Exemplos:
   - **H1 (fora do corpus):** a resposta certa é "não encontrei". Se a pergunta for fácil demais de recusar ("como faço bolo?"), ela testa pouco; prefira algo que pareça estar na lei e não está.
   - **H2 (vocabulário):** precisa usar a palavra do usuário (ICMS, IVA, "imposto único", só a sigla), não a da lei.
   - **H4 (efeito x cobrança):** precisa perguntar "desde quando vale" ou "já está sendo cobrado".
   - **H6, H8, H9 (datas e versões):** precisa ter uma data ou um ano na pergunta, ou não testa nada.
   - **H12 (segurança):** precisa ter `{CPF}` ou `{CNPJ}` no meio do texto, de um jeito natural.
3. **Uma pergunta só.** Se ela pede três coisas ("qual a alíquota, desde quando e quem paga?"), escolha uma, ou divida em duas e corte uma de outra hipótese para manter o total.
4. **Sem resposta embutida.** Corte ou reescreva perguntas que já entregam a resposta ("é verdade que a CBS começa em 2027?" sugere a data).
5. **Não citar artigo, na maioria.** No máximo umas 15 das 100 podem citar um dispositivo, como faria um estudante.
6. **Variedade.** Se duas perguntas são a mesma com palavras trocadas, fique com a melhor e corte a outra. Misture temas: CBS, IBS, Imposto Seletivo, cesta básica, reduções de alíquota, transição, Comitê Gestor, repartição entre estados e municípios.
7. **Nenhum dado pessoal.** Nunca um número de CPF ou CNPJ de verdade, nem inventado: só os marcadores `{CPF}` e `{CNPJ}`. Nenhum nome de pessoa ou empresa real.

## O que você não precisa julgar

- **Se a "Resposta esperada" (sim, parcial, não) e o "Onde" estão certos.** Isso é palpite da IA e será conferido no gabarito. Só corte se o palpite deixar a pergunta sem sentido para a hipótese (por exemplo, uma H1 marcada "sim").
- **A correção jurídica.** O conjunto mede se o modelo é fiel ao texto da lei que ele consultou, não se a resposta está certa em direito tributário.

## No fim

- Conte quantas ficaram em cada hipótese. O alvo é 100 no total, perto da distribuição da tabela; se cortar muitas de uma hipótese, escreva perguntas suas no lugar, na mesma tabela, com a decisão **nova: \<a pergunta\>**.
- Perguntas escritas ou reescritas por você são as mais valiosas: o roadmap pede perguntas criadas por pessoas.
- Se ficar em dúvida numa pergunta, decida mesmo assim e acrescente "(dúvida: \<por quê\>)" na Decisão.
