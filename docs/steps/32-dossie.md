# Passo 32: o dossiê de anotação

Tarefa 17 do plano (revisão R6). Gera, por trace, a página que você lê para anotar: só fatos, com as duas tabelas que o teste de tempo pediu no topo e os textos completos no apêndice.

**Quem escreveu:** entorno. O código e 48 testes foram escritos por um subagente Haiku 5.5 a partir do texto da tarefa; a sessão principal rodou o dossiê nos traces reais de confirmação, achou três defeitos, escreveu 6 testes e corrigiu, e acrescentou a linha que diz quais valores escrever no formulário.

## O que mudou

- **[evals/dossier.py](../../evals/dossier.py):**
  - `cited_provisions(answer)`: as citações em prosa da resposta, normalizadas para a forma do P2 (`"art. 23, III, da EC 132/2023"` vira `"EC 132/2023, art. 23, III"`), sem repetir, na ordem em que aparecem. Reconhece a norma antes e depois do artigo, as variantes de nome ("Lei Complementar nº 214/2025", "Constituição Federal") e os ids do corpus (`LC214.art125`). Citação sem a norma fica marcada.
  - `returned_index(events)`: o que as ferramentas devolveram, por citação (chamadas, texto completo ou só trecho da busca, efeitos), os **fundamentos de efeitos e origens** à parte, e as datas com o lugar de onde vieram.
  - `answer_dates(answer)`: datas em `2027-01-01`, `01/01/2027` e `1º de janeiro de 2027`.
  - `build_dossier(trace, case, *, mode, draft=None, draft_path=None)` e `python -m evals.dossier TRACE_ID [--mode cega|revisada] [--draft PATH]`, que imprime o Markdown.
- **Ordem do dossiê:** pergunta; gabarito; resposta; **tabela de citações**; **tabela de datas**; rascunho (só no modo revisado, sob o aviso "RASCUNHO da IA: confira, não confie"); formulário; apêndice.
- **Citação sem a norma** ("art. 142") é resolvida **só pelo que foi devolvido**: primeiro o artigo exato, depois os seus parágrafos e incisos; com mais de um candidato, a tabela mostra todos. Nunca se supõe a norma (o defeito do protótipo).
- **Modo cego:** nenhum veredito fora do formulário. Passar rascunho no modo cego é erro; o modo revisado exige o rascunho.
- **CPF/CNPJ** mascarados em tudo o que o dossiê escreve.
- **O formulário é um bloco de formato fixo**, que a Tarefa 22 vai ler:

  ````
  ```anotacao
  trace_id: c01-aaaa1111
  kind: blind
  draft:
  C1:
  C2:
  C3:
  C4: n/a
  uncertain:
  note:
  ```
  ````

  O `C4: n/a` vem preenchido só quando o caso não tem H12 nem H13. Uma linha acima do bloco diz os valores aceitos (`pass`, `fail`, `n/a`); é a única linha fora do bloco que nomeia valores de veredito, e o teste do modo cego a exclui pelo texto exato.

## Como rodar

```bash
uv run pytest tests/test_dossier.py -v
```

```bash
uv run python -m evals.dossier conf-sem_skill-9defaaed --traces-dir traces --cases-dir cases
```

O segundo precisa do caso em `cases/`; os traces de confirmação não têm caso gravado.

## O que observar

- **Vermelho antes:** os 48 testes do Haiku falharam por `NotImplementedError` (stub com as assinaturas); dos 6 da sessão principal, 3 falharam antes da correção e 3 são de proteção.
- **Suíte:** 54 testes em `tests/test_dossier.py`, **391** no total, verde duas vezes seguidas.
- **Protótipo no dado real (lição do P2):** rodado nos dois traces de `traces/confirmacao/`, o dossiê mostrou três defeitos que os testes sintéticos não pegavam:
  1. em "A CF, art. 156-A, § 1º, XII, **e** o ADCT, art. 130", o "e" virava alínea, e a citação aparecia como "não devolvida". Agora a alínea só vale seguida de pontuação, fim ou "da/do/de";
  2. efeitos sem data final saíam "até não informado"; no P2, `efeitos_ate` nulo quer dizer sem fim declarado, e agora sai só "desde 2023-12-21";
  3. "o art. 156-A", sem a norma, com o caput e 16 parágrafos devolvidos, virava "ambíguo" com 17 candidatos; agora o artigo exato vence.

  Depois da correção, a tabela do trace sem skill mostra de cara o que custou tempo no teste de tempo: `LC 214/2025, art. 14` "não aparece no que foi devolvido", e `art. 544, VI` aparece só como fundamento de efeitos.
- **Teste de mutação:** 15 mutações nas funções de extração. Na primeira rodada, 5 sobreviveram:
  - resolver "art. 14" por prefixo sem a vírgula casaria com "art. 142": ganhou teste;
  - a mesma citação duas vezes na mesma chamada contaria a chamada duas vezes: ganhou teste;
  - "até None" passaria pelo teste de efeitos sem fim: o teste ficou mais estrito;
  - duas equivalentes: a chave de reserva sem ordinal (só usada para texto que não é citação) e a ordem de desempate entre padrões que começam no mesmo ponto (o mais longo já vence).

  Agora 13 de 15 caem; as 2 que sobram são equivalentes.
- **Limites conhecidos da extração** (anotados pelo Haiku, sem teste): `arts. 5 e 6` captura só o primeiro; `incisos I e II`, `caput` e `§§` não são reconhecidos; `CF/88` e datas `01.01.2027` também não. Quando acontecer, a citação aparece como não reconhecida ou incompleta na tabela, e o apêndice continua tendo tudo.

## Pergunta de previsão

Com as tabelas, quanto tempo leva uma anotação cega? O protótipo sem tabelas levou 5 minutos.
