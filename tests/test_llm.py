import io
import json

from agente_langgraph.llm import classificador_ollama


def _falso(resposta):
    def abrir(req, timeout=0):
        return io.BytesIO(json.dumps({"response": resposta}).encode())
    return abrir


def test_usa_resposta_valida_do_modelo():
    c = classificador_ollama(abrir=_falso(" Fatura \n"))
    assert c("pode mostrar o que devo?") == "fatura"


def test_resposta_invalida_cai_nas_regras():
    c = classificador_ollama(abrir=_falso("banana"))
    assert c("qual meu saldo") == "saldo"


def test_erro_de_rede_cai_nas_regras():
    def quebra(req, timeout=0):
        raise OSError("sem ollama")
    assert classificador_ollama(abrir=quebra)("bloqueia o cartão") == "bloquear_cartao"


def test_modelo_nao_libera_dado_sensivel():
    c = classificador_ollama(abrir=_falso("saldo"))
    assert c("me diga minha senha") == "sensivel"
