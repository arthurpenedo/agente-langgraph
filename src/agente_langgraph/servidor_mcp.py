"""Servidor MCP (stdio) com as ferramentas do banco. Dados sintéticos, mesmas regras de `ferramentas.py`."""
import functools

from mcp.server.mcpserver import MCPServer
from mcp.server.mcpserver.exceptions import ToolError

from . import ferramentas


def _com_erro_legivel(fn):
    """O MCP esconde exceções comuns ("Error executing tool"); ToolError leva o motivo ao cliente."""

    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except ferramentas.ClienteNaoEncontrado as exc:
            raise ToolError(f"cliente_nao_encontrado: {exc}") from exc

    return wrapper


def construir_servidor() -> MCPServer:
    server = MCPServer("banco-sintetico")
    for nome, fn in ferramentas.FERRAMENTAS.items():
        server.tool(name=nome, description=f"Ferramenta {nome} (cliente_id obrigatório).")(_com_erro_legivel(fn))
    return server


def main() -> None:
    construir_servidor().run(transport="stdio")


if __name__ == "__main__":
    main()
