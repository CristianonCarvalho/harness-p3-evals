# Passo 57: fechamento da Fase 3 e lições aprendidas

Tarefa 16 do plano e encerramento formal do Projeto 3 (P3) do roadmap de Engenharia de Software com Agentes de IA (Fase 3: Evals).

## O que mudou

- **[README.md](../../README.md):** atualizado de *"Em construção"* para **Concluído**, com a consolidação dos 5 critérios de conclusão, árvore final de módulos do repositório, comandos de execução e limites empíricos conhecidos.
- **[docs/o-que-deu-errado.md](../o-que-deu-errado.md):** preenchido com as reflexões exigidas pelo roadmap sobre os aprendizados práticos do projeto:
  1. *O que a previsão errou:* a escassez de reprovações em C2/C4 e o efeito nulo na formatação da skill.
  2. *Erros inesperados do juiz:* rigidez com citações temáticas/faixas e necessidade de comparar C3 contra o gabarito.
  3. *O que cortaria da suíte:* a anotação revisada com rascunho de IA (viés de ancoragem sem calibrar o juiz) e subconjuntos com poucas amostras.
  4. *O que o teste de mutação revelou:* testes que passavam por falso positivo em quatro tarefas, reforçando o rigor nos testes de núcleo.

## Como rodar

```bash
# Executar a suíte de testes completa (offline)
python3 -m pytest -q

# Verificar a consistência completa do repositório
python3 -m evals.cli check-repo

# Scan de privacidade (garante ausência de documentos sensíveis)
python3 -m evals.cli scan-privacy
```

## O que observar

**Conclusão dos 5 critérios de concluído da Fase 3:**
1. **Relatório numérico ao trocar modelo ou prompt:** Atendido. Medição por intervalos de Wilson e marca de ruído (`evals.cli compare`).
2. **100 traces anotados:** Atendido com **124 traces anotados** (54 cegas e 70 revisadas), mais 10 de consistência.
3. **Juiz LLM calibrado:** Atendido em C1 (TPR 76%, TNR 100%) e C3 (TPR 91%, TNR 91%); C2 e C4 com limites empíricos declarados.
4. **Antes/depois:** Demonstrado no Passo 50.
5. **Regressão em CI a cada mudança:** Workflow offline ativo no GitHub Actions com execução dupla de testes.

**Teto empírico confirmado:**
A medição de autoconsistência (Passo 56) registrou **100% de concordância**, provando que as diretrizes de avaliação foram assimiladas de forma consistente e determinística pelo anotador humano.

## Pergunta de previsão

Na Fase 4 (P4: Segurança e CI/CD), como a suíte de evals do P3 será integrada aos gates de aprovação de PRs abertos por agentes de IA?
