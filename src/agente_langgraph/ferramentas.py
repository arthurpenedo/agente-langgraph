"""Ferramentas do banco (dados sintéticos). As regras ficam aqui dentro, não no prompt."""

CLIENTES = {
    "c1": {"nome": "Ana", "saldo": 1520.40, "cartao_bloqueado": False,
           "fatura": 830.15, "transacoes": [("Mercado", -212.90), ("Salário", 4000.00), ("Farmácia", -58.30)]},
    "c2": {"nome": "Bruno", "saldo": 87.00, "cartao_bloqueado": False,
           "fatura": 1290.00, "transacoes": [("Aluguel", -1500.00), ("Pix recebido", 300.00)]},
}


class ClienteNaoEncontrado(Exception):
    pass


def _cliente(cliente_id: str) -> dict:
    if cliente_id not in CLIENTES:
        raise ClienteNaoEncontrado(cliente_id)
    return CLIENTES[cliente_id]


def consultar_saldo(cliente_id: str) -> str:
    return f"Seu saldo é R$ {_cliente(cliente_id)['saldo']:.2f}."


def consultar_fatura(cliente_id: str) -> str:
    return f"Sua fatura atual é R$ {_cliente(cliente_id)['fatura']:.2f}."


def listar_transacoes(cliente_id: str, limite: int = 3) -> str:
    itens = _cliente(cliente_id)["transacoes"][:limite]
    return "Últimas transações: " + "; ".join(f"{d} R$ {v:.2f}" for d, v in itens) + "."


def bloquear_cartao(cliente_id: str) -> str:
    c = _cliente(cliente_id)
    if c["cartao_bloqueado"]:
        return "Seu cartão já estava bloqueado."
    c["cartao_bloqueado"] = True
    return "Cartão bloqueado com sucesso."


FERRAMENTAS = {
    "saldo": consultar_saldo,
    "fatura": consultar_fatura,
    "transacoes": listar_transacoes,
    "bloquear_cartao": bloquear_cartao,
}
