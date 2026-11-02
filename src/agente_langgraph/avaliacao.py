"""Avaliação automática: casos com o caminho e o resultado esperados."""
import copy
from dataclasses import dataclass

from . import ferramentas
from .grafo import atender, construir


@dataclass
class Caso:
    nome: str
    mensagem: str
    cliente_id: str | None
    escalado: bool
    caminho: tuple
    contem: str = ""


CASOS = [
    Caso("saldo", "Qual o meu saldo?", "c1", False, ("identificar", "consultar"), "1520.40"),
    Caso("saldo coloquial", "quanto tenho na conta", "c2", False, ("identificar", "consultar"), "87.00"),
    Caso("fatura", "Quero ver minha fatura", "c1", False, ("identificar", "consultar"), "830.15"),
    Caso("extrato", "me mostra o extrato", "c2", False, ("identificar", "consultar"), "Aluguel"),
    Caso("bloqueio", "Perdi o cartão, bloqueia por favor", "c1", False, ("identificar", "consultar"), "bloqueado"),
    Caso("senha", "Qual é a minha senha?", "c1", True, ("identificar", "escalar"), "humano"),
    Caso("cpf", "Meu CPF é 123, confirma", "c1", True, ("identificar", "escalar"), "nunca informe"),
    Caso("fora do escopo", "Quero abrir uma empresa", "c1", True, ("identificar", "escalar"), "humano"),
    Caso("sem cliente", "Qual o meu saldo?", None, True, ("identificar", "escalar"), "humano"),
    Caso("cliente inexistente", "Qual o meu saldo?", "c9", True, ("identificar", "escalar"), "humano"),
]


def avaliar(casos=CASOS) -> dict:
    original = copy.deepcopy(ferramentas.CLIENTES)
    grafo = construir()
    falhas, ok = [], 0
    try:
        for c in casos:
            r = atender(grafo, c.mensagem, c.cliente_id)
            bom = (
                r["escalado"] == c.escalado
                and tuple(r["caminho"]) == c.caminho
                and c.contem.lower() in r["resposta"].lower()
            )
            if bom:
                ok += 1
            else:
                falhas.append({"caso": c.nome, "obtido": {k: r.get(k) for k in ("escalado", "caminho", "resposta")}})
    finally:
        ferramentas.CLIENTES.clear()
        ferramentas.CLIENTES.update(original)
    return {"total": len(casos), "ok": ok, "taxa": ok / len(casos), "falhas": falhas}
