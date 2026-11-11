"""Testes no mesmo processo do servidor MCP (os de test_mcp.py rodam o servidor em subprocesso)."""
import asyncio

import pytest
from mcp.server.mcpserver.exceptions import ToolError

from agente_langgraph import ferramentas, servidor_mcp


def test_cliente_inexistente_vira_tool_error_com_o_motivo():
    funcao = servidor_mcp._com_erro_legivel(ferramentas.consultar_saldo)
    with pytest.raises(ToolError, match="cliente_nao_encontrado"):
        funcao("cliente-que-nao-existe")


def test_wrapper_preserva_nome_e_resultado():
    assert servidor_mcp._com_erro_legivel(ferramentas.consultar_saldo).__name__ == "consultar_saldo"


def test_construir_servidor_registra_todas_as_ferramentas():
    servidor = servidor_mcp.construir_servidor()
    nomes = {t.name for t in asyncio.run(servidor.list_tools())}
    assert nomes == set(ferramentas.FERRAMENTAS)
