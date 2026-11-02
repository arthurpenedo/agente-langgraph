# agente-langgraph

[![CI](https://github.com/arthurpenedo/agente-langgraph/actions/workflows/ci.yml/badge.svg)](https://github.com/arthurpenedo/agente-langgraph/actions/workflows/ci.yml)

Agente de atendimento bancário feito com **LangGraph**: o fluxo é um grafo com estados explícitos
(`identificar` → `consultar` ou `escalar`), não um prompt gigante. Grátis: sem API paga, dados sintéticos.

```
START → identificar ─┬─ intenção conhecida → consultar → END
                     └─ sensível / sem cliente / desconhecida → escalar (humano) → END
```

- **identificar**: confere o cliente e classifica a intenção (regras; dá para trocar por um modelo aberto passando `construir(classificador=...)`).
- **consultar**: chama a ferramenta (saldo, fatura, transações, bloquear cartão). As regras ficam dentro da ferramenta.
- **escalar**: senha/CPF/token, cliente não identificado ou pedido fora do escopo vão para um humano.

## Usar
```
pip install -e ".[dev]"
agente-langgraph atender "qual meu saldo?" --cliente c1
agente-langgraph avaliar
```

## Avaliação
10 casos (`avaliacao.py`) checam o **caminho no grafo**, se escalou e o texto da resposta. Resultado local: **10/10 (100%)**,
12 testes pytest passando. É um conjunto pequeno e escrito por mim, então mostra que o fluxo está correto, não que o
agente resolve qualquer conversa.

## Limites
- A classificação é por palavras-chave; frases fora do vocabulário vão para humano (falha segura, mas escala demais).
- O classificador com Ollama (`atender --modelo ollama`, `llm.py`) foi testado só com respostas simuladas; execução real não medida. Ferramentas via MCP ainda não foram ligadas.
- O ecossistema de agentes do mesmo autor com tool calling e modelos abertos: [agente-banco](https://github.com/arthurpenedo/agente-banco).
