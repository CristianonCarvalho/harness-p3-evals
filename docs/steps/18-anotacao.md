# Passo 18: anotação e validação versionada

## O que mudou

Implementação do contrato de anotação humana em `evals/annotation.py` e sua suíte em `tests/test_annotation.py` (Tarefa 5 do roadmap, Passo 18):
- **`validate_annotation(ann, case, trace)`:** valida conteúdo em memória sem campos de versão/data.
  - Combinação: garante correspondência estrita de `trace_id`, `case_id` e exige trace com `status == "ok"`.
  - Forma: exige exatamente `C1`, `C2`, `C3`, `C4`, vereditos em `("pass", "fail", "n/a")` e `kind` em `("blind", "revised")`.
  - Aplicabilidade: proíbe `n/a` em `C1` a `C3`; `C4` é `n/a` se e somente se o caso não envolve hipóteses de segurança (`H12` e `H13`).
  - Nota e incerteza: qualquer `fail` ou item em `uncertain` exige nota explicativa (rejeita vazios, espaços e quebras de linha); `uncertain` deve ser lista e proíbe critérios `n/a` ou desconhecidos.
  - Rascunho (`draft`): obrigatório em revisadas e proibido em cegas; caminho relativo posix estritamente no formato `drafts/annotations/<trace_id>.json`.
  - Privacidade: nota inspecionada por `find_taxpayer_ids` contra CPF/CNPJ colado ou pontuado, emitindo mensagem sem vazar os dígitos.
- **`write_annotation(ann, case, trace, annotations_dir, *, date)`:**
  - Recusa anotações que já tragam `version` ou `date`.
  - Confere formato de data ISO `AAAA-MM-DD` com validação dupla (regex estrito + `date.fromisoformat`).
  - Valida o conteúdo antes de tocar no disco (não cria diretório se inválido).
  - Incrementa versão numericamente (`v10 -> v11`, nunca alfabética).
  - Grava com `open(path, "x")`, que nunca sobrescreve um arquivo existente. Não é gravação atômica: se o processo cair no meio, pode ficar um arquivo pela metade, e a leitura o recusa como JSON corrompido.
- **`load_history(annotations_dir, trace_id)` e `load_annotation(annotations_dir, trace_id)`:**
  - Leitura ordenada por versão numérica.
  - Validação de integridade do arquivo lido: confere se tem `version`, se o número bate com o nome do arquivo (`.v<N>.json`) e se a data é válida.
  - Defesa contra duplicidades e corrupção: recusa nomes não-canônicos com zeros à esquerda (ex: `v01` colidindo com `v1`), recusa arquivos cujo `trace_id` interno divirja do nome do arquivo, e captura `json.JSONDecodeError` encapsulando com o nome do arquivo corrompido para facilitar depuração.
  - Histórico de trace sem arquivos devolve `[]` e `load_annotation` devolve `None`.

## Como rodar

```bash
uv run pytest tests/test_annotation.py -v
```

## O que observar

- **Suíte:** 76 testes em `tests/test_annotation.py`, 257 no total, verde duas vezes seguidas.
- **Vermelho antes e dentes:** cada linha da tabela de aceitação foi escrita primeiro como teste. A revisão encontrou e fechou testes que passariam pelo motivo errado:
  - teste 5: `"c01"` aparecia também no `trace_id`, então a mensagem podia omitir o `case_id` do caso; o caso passou a ser `c09`;
  - teste 20: todos os caminhos ruins tinham também o nome de arquivo errado, e só a regra do nome era exercida; cada caminho passou a ter um defeito só, e a regra virou uma comparação das partes do caminho;
  - mensagens localizadas pelo critério **e** por uma palavra própria da regra (`"desconhecido"`, `"inválido"`, `"nota"`), porque `"fail"` e `"se aplica"` aparecem em mensagens de outras regras.
- **Teste de mutação sistemático (como nos passos 25 e 26): não rodado neste passo.** A prova de cada regra foi apagá-la e ver o teste dela falhar. Um resto conhecido: a checagem de versão duplicada em `load_history` (`seen_versions`) não dispara nunca, porque a regra do nome canônico já impede dois arquivos com a mesma versão.
- **Segurança contra vazamento:** a validação de privacidade emite mensagem com contagem de documentos encontrados, sem jamais ecoar o número do documento na mensagem de erro.
- **Duas conferências na data:** `date.fromisoformat("20261111")` do Python 3.11+ aceita datas sem hífen; a combinação com `_DATE_RE.fullmatch` garante estritamente `AAAA-MM-DD`.

## Pergunta de previsão

Nas 5 primeiras anotações feitas com o validador, quantas vezes ele vai recusar? E o tempo por trace sobe, desce ou fica igual aos 5 minutos do teste?

*Previsão:*
- **Recusas nas 5 primeiras:** prevejo **2 recusas** — os erros mais comuns esperados no início são esquecer a nota ao marcar `fail` e tentar usar `n/a` por hábito em `C1`/`C2` quando "não havia o que citar".
- **Tempo por trace:** deve **subir ligeiramente** nos primeiros traces (para cerca de 6 a 7 minutos) devido ao tempo gasto lendo mensagens de validação e refinando as notas explicativas; após os primeiros 5 a 10 traces e com o hábito formado, a tendência é convergir para a média de 4 a 5 minutos.
