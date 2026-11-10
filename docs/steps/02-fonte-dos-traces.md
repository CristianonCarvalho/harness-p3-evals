# Passo 02: fonte dos traces

## O que mudou

A spec ganhou a decisão D4: os traces vêm do Claude Code em modo não interativo, que roda o P2 completo (server, skill e hook). O trace bruto será normalizado para um formato próprio, independente da fonte. Nenhum código foi escrito.

## Como rodar

Não há o que rodar. Se quiser ver a aparência da fonte, rode uma pergunta qualquer com `claude -p "<pergunta>" --output-format stream-json --verbose` em uma pasta com o server do P2 configurado, e olhe os eventos. Não commite a saída: traces ficam fora do repositório.

## O que observar

- Que eventos o stream traz: chamadas de ferramenta, resultados, texto final, custo e tokens?
- Falta algo que o formato de anotação precisaria ler (por exemplo, a saída bruta das ferramentas, para checar C1 e C2)?

## Pergunta de previsão

Em uma pergunta com a skill ligada, o modelo chama o server em quantas das 10 primeiras rodadas? Escreva o número antes de rodar; o que não chamar o server responde de memória.
