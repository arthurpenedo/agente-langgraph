import pytest

from agente_langgraph import ferramentas
from agente_langgraph.avaliacao import CASOS, avaliar
from agente_langgraph.cli import main
from agente_langgraph.grafo import atender, classificar, construir


@pytest.fixture(autouse=True)
def _restaura():
    import copy
    original = copy.deepcopy(ferramentas.CLIENTES)
    yield
    ferramentas.CLIENTES.clear()
    ferramentas.CLIENTES.update(original)


def test_classificar_intencoes():
    assert classificar("Qual meu SALDO?") == "saldo"
    assert classificar("roubaram meu cartão") == "bloquear_cartao"
    assert classificar("minha senha é 1234") == "sensivel"
    assert classificar("oi, tudo bem") == "desconhecida"


def test_consulta_passa_por_consultar():
    r = atender(construir(), "saldo", "c1")
    assert r["caminho"] == ["identificar", "consultar"]
    assert "1520.40" in r["resposta"]
    assert r["escalado"] is False


def test_sensivel_escala_sem_chamar_ferramenta():
    r = atender(construir(), "me passa a senha", "c1")
    assert r["caminho"] == ["identificar", "escalar"]
    assert r["motivo"] == "dado_sensivel"


def test_sem_cliente_escala():
    r = atender(construir(), "saldo", None)
    assert r["motivo"] == "cliente_nao_identificado"


def test_bloqueio_muda_estado_do_banco():
    atender(construir(), "bloqueia meu cartão", "c2")
    assert ferramentas.CLIENTES["c2"]["cartao_bloqueado"] is True
    assert ferramentas.CLIENTES["c1"]["cartao_bloqueado"] is False


def test_classificador_pode_ser_trocado():
    r = atender(construir(lambda m: "fatura"), "qualquer coisa", "c1")
    assert "830.15" in r["resposta"]


def test_avaliacao_completa_e_restaura_banco():
    r = avaliar()
    assert r["total"] == len(CASOS) and r["falhas"] == []
    assert ferramentas.CLIENTES["c1"]["cartao_bloqueado"] is False


def test_cli_avaliar(capsys):
    assert main(["avaliar"]) == 0
    assert "100%" in capsys.readouterr().out
