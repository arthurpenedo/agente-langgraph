from agente_langgraph import ferramentas
from agente_langgraph.avaliacao import Caso, avaliar
from agente_langgraph.grafo import atender, construir


def test_avaliar_registra_falha_com_o_que_foi_obtido():
    caso_errado = Caso("errado", "Qual o meu saldo?", "c1", True, ("identificar", "escalar"), "humano")
    r = avaliar([caso_errado])
    assert r["ok"] == 0 and r["taxa"] == 0
    assert r["falhas"][0]["caso"] == "errado"
    assert r["falhas"][0]["obtido"]["escalado"] is False


def test_cliente_que_some_no_meio_escala_para_humano():
    def executor(intencao, cliente_id):
        raise ferramentas.ClienteNaoEncontrado(cliente_id)

    r = atender(construir(executor=executor), "Qual o meu saldo?", "c1")
    assert r["escalado"] is True
    assert r["motivo"] == "cliente_nao_encontrado"
    assert r["caminho"] == ["identificar", "consultar"]
