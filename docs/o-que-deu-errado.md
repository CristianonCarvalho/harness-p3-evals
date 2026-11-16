# O que deu errado

Um relato reflexivo sobre o que não saiu como previsto durante o desenvolvimento da suíte de avaliação (P3), conforme exigido pelas diretrizes do roadmap de Engenharia de Software com Agentes de IA.

---

## 1. O que a previsão errou?

### A raridade de reprovações em C2 e C4
A previsão inicial assumia que uma amostra aleatória de 30 a 50 traces distribuiria falhas de forma equilibrada entre os quatro critérios. A realidade empírica mostrou o oposto:
- **C2 (Datas de efeitos):** Em 54 traces cegos, o modelo avaliado (Haiku com ferramentas do MCP) errou datas apenas 1 vez quando respondeu. O modelo é conservador: quando encontra a norma, copia a data de efeitos fornecida pela ferramenta com alta fidelidade. Seriam necessários mais de 300 traces cegos para obter 10 reprovações humanas e calibrar o juiz.
- **C4 (Segurança):** Não houve nenhuma reprovação no conjunto de teste. O hook local bloqueia chamadas com documentos antes de chegarem ao servidor, e o modelo não repetiu documentos nem caiu em injeções nas condições de teste.
- **Lição:** Não se pode planejar o tamanho de uma amostra de calibração supondo distribuição uniforme de erros. Quando um modelo erra muito pouco em determinada dimensão, essa métrica se torna um limite empírico de dados, e tentar forçar a calibração com amostras infladas seria antieconômico.

### O efeito real da skill na acurácia (Passo 50)
A intuição prévia sugeria que pedir expressamente o `id` do dispositivo entre crases na skill do P2 faria a aprovação de citação (C1) subir. 
- O resultado numérico mostrou que a variação ficou estritamente **dentro do ruído estatístico** (de 52,9% para 44,1%).
- A análise dos dados revelou a causa: a grande maioria das reprovações em C1 (44 de 47 reprovações em código) decorria da regra rígida do critério de exigir **todos** os dispositivos previstos no gabarito ("esperado ausente"), e não de alucinação de citações ou formatação. A medição numérica impediu que uma suposição intuitiva virasse verdade aceita.

---

## 2. Que erro o juiz cometeu que você não esperava?

### Rigidez excessiva com menções temáticas e faixas de artigos
No C1, o juiz LLM inicialmente reprovava respostas corretas por tratarem referências contextuais como citações formais sem lastro:
- Citações de intervalos como "arts. 419 a 423 da LC 214/2025" (que servem apenas para situar o tema) eram tratadas pelo juiz como se o modelo tivesse afirmado e citado cada um dos artigos individualmente.
- O mesmo ocorria com menções ao nome da lei ("segundo a Constituição" ou "conforme a LC 214/2025").
- **Ajuste:** Foi necessário refinar o prompt do juiz (`C1.md`) para diferenciar citação pontual de dispositivo (que exige devolução literal das ferramentas) de mera indicação de fonte ou faixa temática.

### Comparação de C3 contra a ferramenta em vez do gabarito
Inicialmente, o juiz do C3 tentava deduzir se o modelo devia admitir ignorância examinando se as ferramentas de busca haviam retornado algo no trace. 
- Isso gerava falsos positivos quando a busca do modelo falhava por formulação ruim da query: o modelo dizia "não encontrei" e o juiz aprovava porque a ferramenta realmente não trouxera nada, quando na verdade o corpus continha a resposta.
- **Ajuste:** A calibração do C3 só foi estabilizada (atingindo TPR e TNR superiores a 90%) quando o prompt do juiz passou a confrontar a resposta diretamente com o campo estruturado do gabarito (`answer_exists`: sim, parcial ou não).

---

## 3. O que você cortaria da suíte se o tempo apertasse?

### A anotação revisada com rascunho de IA (os 70 traces)
Embora os 70 traces revisados tenham sido úteis para atingir a marca de 100+ anotações e para medir e comprovar o fenômeno da **ancoragem** (onde o usuário mudou o rascunho da IA em apenas 12,9% dos casos no C1, apesar de o rascunhador errar 40% na amostra cega), eles não puderam ser usados para calibrar o juiz.
- A calibração do juiz dependeu exclusivamente dos 54 traces anotados às cegas.
- Se o tempo fosse restrito, seria mais eficiente concentrar todo o tempo humano disponível na anotação cega (por exemplo, 40 ou 50 traces cegos diretos), eliminando o fluxo e o custo dos rascunhos de anotação.

### Recortes de subconjuntos com amostras muito reduzidas
Subconjuntos como a condição "sem skill" (14 casos) geram intervalos de confiança de Wilson tão amplos ($\pm 25\%$) que tornam praticamente impossível distinguir efeito real de ruído amostral. Em projetos futuros, subconjuntos de comparação devem ter um piso mínimo de 30 casos cada para justificar o esforço de execução e análise.

---

## 4. O que o teste de mutação revelou?

### Cobertura de código sem capacidade de detecção
Durante as Tarefas 4 (casos/splits), 8 (checagens em código), 9 (conferência do gabarito) e 14 (relatórios), a aplicação manual de testes de mutação (inversão de operadores booleanos `>`, `<`, desativação de filtros de regex e retorno estático de constantes) revelou que vários testes automatizados passavam mesmo com o código adulterado.

### Lições para o código do núcleo
1. **Testar asserções negativas com rigor:** Testar apenas que um trace válido passa não garante que um trace inválido seja barrado. É fundamental testar que violações específicas disparam as mensagens de erro esperadas.
2. **Propriedades matemáticas em vez de valores únicos:** Nas métricas de TPR/TNR e intervalos de Wilson, mutações simples (como somar 1 no denominador errado) passavam em fixtures simétricas ($5/10$). O teste só se tornou robusto ao usar valores assimétricos e testar propriedades de fronteira ($n=0$, $n=1$, $100\%$ e $0\%$).
3. **Imutabilidade real:** O teste de mutação expôs que se o validador de anotações permitisse sobrescrita silenciosa de arquivos, a suíte de testes original não capturaria. Isso levou à implementação de travas estritas contra sobrescrita em `trace.py`, `annotation.py` e nos relatórios.
