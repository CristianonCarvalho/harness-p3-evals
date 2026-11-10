# Agent Directives

## Project context

- **Projeto:** P3, a suíte de avaliação do MCP server do P2 (`../projeto02`). Ainda sem código: a stack será decidida na spec.
- **Conventions:** identificadores em inglês; comentários, mensagens e notas em português; comentários didáticos explicam o porquê. Testes offline (nenhum chama modelo nem rede), sem `conftest.py`, independentes do diretório atual. Só dados públicos ou sintéticos: nunca CPF/CNPJ válido escrito no repositório; nunca exibir chaves.

## Regra do roadmap para este projeto

Na Fase 3, **o núcleo é escrito à mão pelo usuário**, e o agente só revisa. Não implemente o núcleo (formato de anotação, métricas, juiz) sem o usuário pedir explicitamente; explique, pergunte e revise. Ver `CLAUDE.md`.

## Task execution

- Follow the scope and target files specified in the assigned task.
- Preserve pre-existing changes and avoid changes outside the scope.
- Run relevant tests and clearly report results and limitations.
- Documentação (`docs/**`, `*.md`) pode ser editada direto.
