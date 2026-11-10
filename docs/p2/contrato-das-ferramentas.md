# O contrato das ferramentas do P2

- **Fonte:** spec do P2, seções 5 a 7 (`../projeto02/docs/superpowers/specs/2026-11-05-mcp-reforma-tributaria-design.md`) e README do P2, conferidos em 2026-11-10.
- **Versão a fixar no P3:** a tag `step-16` do repositório `CristianonCarvalho/harness-p2-MCP` (suíte de 479 testes, corpus `c269388fb2bd53b0a326d2b8b516c592478e3a41d8f2c3bceb0bf51caaf41e3a`, coletado em 2026-11-06).
- **Por que fixar:** um eval só compara duas rodadas se o sistema avaliado não mudou entre elas. Todo relatório do P3 deve registrar a tag do P2, o `corpus.versao` e o modelo.

## Duas ferramentas

### `buscar_dispositivos`

| Entrada | Tipo | Regra |
|---|---|---|
| `consulta` | texto | obrigatória, 1 a 500 caracteres |
| `data_referencia` | data ISO (`AAAA-MM-DD`) | opcional; ausente vale a data de hoje, ecoada na resposta |
| `limite` | inteiro | padrão 5, de 1 a 10 |

Saída: `encontrado`, `consulta`, `data_referencia`, `resultados[]`, `motivo` (`null` quando encontrou) e `corpus{versao, coletado_em}`. Cada resultado traz `id`, `versao`, `citacao`, `trecho` (até 300 caracteres), `pontuacao` (relevância de 0 a 1, não o BM25 bruto), `efeitos{desde, ate, fundamento, fundamento_ate, metodo, produz_efeitos_na_data}` e `outras_versoes[]`. As versões de um mesmo `id` vêm agrupadas num só resultado.

### `obter_dispositivo`

Entrada: `id` (obrigatório), `data_referencia` (opcional), `incluir_filhos` (padrão `true`).

Saída: `encontrado`, `id`, `data_referencia`, `versao`, `citacao`, `norma`, `origem`, `alteracao`, `texto`, `filhos[]`, `vigor_desde`, `efeitos{...}`, `outras_versoes[]`, `observacao`, `truncado`, `fonte_url` e `corpus{...}`. Id inexistente: `encontrado: false` com `id`, `data_referencia`, `motivo` e `corpus`.

Os filhos são os diretos, na ordem da lei. A lista vem da versão escolhida do pai; o texto de cada filho segue a mesma regra de data.

## Os campos que o P3 vai conferir

O P2 foi desenhado para que a resposta seja **verificável**. Para cada afirmação do modelo, a conferência determinística é possível:

| O modelo afirma | Confere-se contra |
|---|---|
| "Segundo o art. X…" | `citacao` / `id` devolvidos pela ferramenta, e a existência do id no corpus |
| "Vale desde DD/MM/AAAA" | `efeitos.desde` da versão escolhida para a data |
| "Já está valendo em tal data" | `produz_efeitos_na_data` (`true`, `false` ou `null`) |
| Um trecho entre aspas | substring de `texto` ou `trecho` devolvido |
| "Não encontrei" | `encontrado: false` e, quando houver, `motivo` |

## Regra de escolha da versão

A versão escolhida é a cujo intervalo `[efeitos_desde, efeitos_ate]` contém a `data_referencia`.
- Data anterior a todas as versões: devolve a primeira, com `produz_efeitos_na_data: false` e, se for `alterado`, a observação "redação anterior não incluída no corpus".
- Data posterior ao fim da última versão (revogado): devolve a última, com `produz_efeitos_na_data: false` e a observação "revogado a partir de <data> (<fundamento>)". O dispositivo **não** vira "não encontrado".
- Mais de uma versão possível (término indeterminado): devolve a mais antiga, com `produz_efeitos_na_data: null`.

## Os três "não sei" (todos com `isError: false`)

1. `encontrado: false`: a busca não passou do limiar de relevância (0,15, relativo) ou o id não existe.
2. `produz_efeitos_na_data: null`: o efeito é indeterminado; **nunca** `false` no lugar de "não sei".
3. `observacao: "redação anterior não incluída no corpus"`: o texto que valia antes não está no corpus.

## Erros (`isError: true`)

Só dois códigos, com texto apenas `{"erro", "mensagem"}`:
- `entrada_invalida`;
- `dados_de_contribuinte` (CPF/CNPJ válido pelo dígito verificador em qualquer argumento de texto ou chave). A mensagem diz o tipo e o campo, **nunca o número**.

## Limites de tamanho

`trecho` de até 300 caracteres; até 10 resultados; `obter_dispositivo` com teto de 4.000 caracteres entre texto e filhos. Ao cortar: `truncado: true`, o texto termina em "…" e os filhos que não couberam ficam na lista com `texto: null`.

## Identificadores

`CF.art156-A.par1.incIX`, `LC214.art125`, `LC214.art126.par6`, `ADCT.art125`… O formato é `NORMA.artN[.parN][.incROMANO][.alíneaX]`. Uma pergunta de eval pode citar um id esperado como gabarito.

## Como o P3 chama o server

| Modo | Como | Observação |
|---|---|---|
| stdio (local) | `uv run --quiet python -m taxlaw.server`, a partir de um checkout do P2 na tag fixada | Sem rede, determinístico. Sem hook do Claude Code no caminho |
| HTTP (remoto) | `<URL do server remoto>/mcp`, com `Authorization: Bearer <token>` | O token vem só da variável de ambiente `TAXLAW_HTTP_TOKEN`, nunca de argumento nem de arquivo versionado. Stateless. Tem limite de taxa no nginx (429) |
| Cliente de terminal | `client/taxlaw_client.py` do P2 (`buscar`, `obter`, `--json`, `--url`) | Consulta sem modelo nenhum: serve para as verificações determinísticas do gabarito |

**Duas camadas de avaliação**, que o P3 deve manter separadas:
1. **Camada determinística** (offline, grátis): dada uma consulta e uma data, a ferramenta devolve o que o gabarito espera? Isso avalia o server.
2. **Camada com modelo** (paga): dada uma pergunta em linguagem natural, o modelo, usando o server (com e sem a skill), responde certo e cita certo? Isso avalia o conjunto modelo + skill + server.

## Onde está cada coisa no P2

| O quê | Onde |
|---|---|
| Spec, contrato completo | `../projeto02/docs/superpowers/specs/2026-11-05-mcp-reforma-tributaria-design.md`, seção 6 |
| Corpus | `../projeto02/corpus/dispositivos.json` (cabeçalho `fontes`) |
| Skill | `../projeto02/.claude/skills/consultar-reforma-tributaria/` |
| Falhas já achadas | `../projeto02/docs/o-que-deu-errado.md` (24 falhas) |
