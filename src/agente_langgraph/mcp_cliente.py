"""Cliente MCP síncrono para o grafo: sobe o servidor por stdio e mantém UMA sessão aberta.

A sessão fica viva porque o estado (cartão bloqueado) mora no processo do servidor.
"""
import asyncio
import sys
import threading
from contextlib import AsyncExitStack

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from . import ferramentas


class ClienteMCP:
    def __init__(self, comando: str = sys.executable, args: tuple = ("-m", "agente_langgraph.servidor_mcp")):
        self._params = StdioServerParameters(command=comando, args=list(args))
        self._loop = asyncio.new_event_loop()
        self._thread = threading.Thread(target=self._loop.run_forever, daemon=True)
        self._sessao: ClientSession | None = None

    def _rodar(self, coro):
        return asyncio.run_coroutine_threadsafe(coro, self._loop).result(timeout=30)

    async def _vida(self):
        """Abre e fecha a sessão na MESMA task (o anyio exige isso para os cancel scopes)."""
        self._parar = asyncio.Event()
        try:
            async with AsyncExitStack() as stack:
                read, write = await stack.enter_async_context(stdio_client(self._params))
                self._sessao = await stack.enter_async_context(ClientSession(read, write))
                await self._sessao.initialize()
                self._pronto.set()
                await self._parar.wait()
        finally:
            self._pronto.set()

    def __enter__(self):
        self._thread.start()
        self._pronto = threading.Event()
        self._tarefa = asyncio.run_coroutine_threadsafe(self._vida(), self._loop)
        self._pronto.wait(timeout=30)
        if self._sessao is None:
            self._tarefa.result(timeout=5)  # propaga o erro de abertura
        return self

    def __exit__(self, *exc):
        self._loop.call_soon_threadsafe(self._parar.set)
        self._tarefa.result(timeout=30)
        self._loop.call_soon_threadsafe(self._loop.stop)
        self._thread.join(timeout=5)

    def ferramentas(self) -> list[str]:
        return [t.name for t in self._rodar(self._sessao.list_tools()).tools]

    def chamar(self, nome: str, cliente_id: str) -> str:
        r = self._rodar(self._sessao.call_tool(nome, {"cliente_id": cliente_id}))
        texto = "".join(c.text for c in r.content if getattr(c, "text", None))
        if r.is_error:
            if "cliente_nao_encontrado" in texto:
                raise ferramentas.ClienteNaoEncontrado(cliente_id)
            raise RuntimeError(texto)
        return texto

    def executor(self):
        """Mesma assinatura que o grafo espera: (nome_da_ferramenta, cliente_id) -> texto."""
        return self.chamar
