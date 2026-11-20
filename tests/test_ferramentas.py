

def test_listar_transacoes_limite_zero_ou_negativo_nao_corta_errado():
    from agente_langgraph import ferramentas
    assert ferramentas.listar_transacoes("c1", 0) == "Não há transações para mostrar."
    assert ferramentas.listar_transacoes("c1", -1) == "Não há transações para mostrar."
    assert ferramentas.listar_transacoes("c1", 1).count(";") == 0
