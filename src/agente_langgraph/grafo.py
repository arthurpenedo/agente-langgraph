"""Grafo LangGraph: identificar -> consultar -> responder, com desvio para escalar.

Estados explícitos: cada nó lê e escreve só os campos do `Estado`. A intenção é classificada por regras
(determinístico, grátis); `classificador` pode ser trocado por um modelo aberto (função `str -> intenção`).
"""
import re
import unicodedata
from collections.abc import Callable
from typing import TypedDict

from langgraph.graph import END, START, StateGraph

from . import ferramentas

SENSIVEL = ("senha", "cpf", "token", "codigo de seguranca")
INTENCOES = [
    ("bloquear_cartao", ("bloque", "perdi o cartao", "roubaram", "cartao roubado")),
    ("fatura", ("fatura",)),
    ("transacoes", ("extrato", "transac", "ultimas compras")),
    ("saldo", ("saldo", "quanto tenho")),
]


class Estado(TypedDict, total=False):
    cliente_id: str | None
    mensagem: str
    intencao: str
    resposta: str
    escalado: bool
    motivo: str
    caminho: list


def _norm(texto: str) -> str:
    sem = unicodedata.normalize("NFD", texto.lower())
    return re.sub(r"[̀-ͯ]", "", sem)


def classificar(mensagem: str) -> str:
    t = _norm(mensagem)
    if any(s in t for s in SENSIVEL):
        return "sensivel"
    for nome, chaves in INTENCOES:
        if any(c in t for c in chaves):
            return nome
    return "desconhecida"


def _local(nome: str, cliente_id: str) -> str:
    return ferramentas.FERRAMENTAS[nome](cliente_id)


def construir(classificador: Callable[[str], str] = classificar, executor: Callable[[str, str], str] = _local):
    def identificar(e: Estado) -> Estado:
        caminho = e.get("caminho", []) + ["identificar"]
        if not e.get("cliente_id") or e["cliente_id"] not in ferramentas.CLIENTES:
            return {"intencao": "sem_cliente", "caminho": caminho}
        return {"intencao": classificador(e["mensagem"]), "caminho": caminho}

    def consultar(e: Estado) -> Estado:
        caminho = e["caminho"] + ["consultar"]
        try:
            resp = executor(e["intencao"], e["cliente_id"])
        except ferramentas.ClienteNaoEncontrado:
            return {"escalado": True, "motivo": "cliente_nao_encontrado", "caminho": caminho}
        return {"resposta": resp, "escalado": False, "caminho": caminho}

    def escalar(e: Estado) -> Estado:
        motivo = {"sensivel": "dado_sensivel", "sem_cliente": "cliente_nao_identificado"}.get(
            e["intencao"], "intencao_desconhecida"
        )
        msg = "Vou transferir você para um atendente humano."
        if motivo == "dado_sensivel":
            msg += " Por segurança, nunca informe senha, CPF ou token por aqui."
        return {"resposta": msg, "escalado": True, "motivo": motivo, "caminho": e["caminho"] + ["escalar"]}

    def rota(e: Estado) -> str:
        return "consultar" if e["intencao"] in ferramentas.FERRAMENTAS else "escalar"

    g = StateGraph(Estado)
    g.add_node("identificar", identificar)
    g.add_node("consultar", consultar)
    g.add_node("escalar", escalar)
    g.add_edge(START, "identificar")
    g.add_conditional_edges("identificar", rota, {"consultar": "consultar", "escalar": "escalar"})
    g.add_edge("consultar", END)
    g.add_edge("escalar", END)
    return g.compile()


def atender(grafo, mensagem: str, cliente_id: str | None = None) -> Estado:
    return grafo.invoke({"mensagem": mensagem, "cliente_id": cliente_id, "caminho": []})
