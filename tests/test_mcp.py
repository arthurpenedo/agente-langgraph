import pytest

pytest.importorskip("mcp")

from agente_langgraph import ferramentas
from agente_langgraph.grafo import atender, construir
from agente_langgraph.mcp_cliente import ClienteMCP


@pytest.fixture(scope="module")
def cliente():
    with ClienteMCP() as c:
        yield c


def test_servidor_expoe_as_quatro_ferramentas(cliente):
    assert sorted(cliente.ferramentas()) == sorted(ferramentas.FERRAMENTAS)


def test_grafo_responde_via_mcp_igual_ao_local(cliente):
    via_mcp = atender(construir(executor=cliente.executor()), "qual meu saldo?", "c1")
    local = atender(construir(), "qual meu saldo?", "c1")
    assert via_mcp["resposta"] == local["resposta"]
    assert via_mcp["escalado"] is False


def test_estado_do_cartao_vive_no_servidor(cliente):
    g = construir(executor=cliente.executor())
    assert atender(g, "bloqueia meu cartão", "c2")["resposta"] == "Cartão bloqueado com sucesso."
    assert atender(g, "bloqueia meu cartão", "c2")["resposta"] == "Seu cartão já estava bloqueado."
    assert ferramentas.CLIENTES["c2"]["cartao_bloqueado"] is False  # processo do cliente intacto


def test_cliente_inexistente_levanta_a_mesma_excecao_local(cliente):
    with pytest.raises(ferramentas.ClienteNaoEncontrado):
        cliente.chamar("saldo", "zzz")
