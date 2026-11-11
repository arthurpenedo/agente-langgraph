"""Ramos da CLI que usam Ollama e MCP, com os dois trocados por falsos (sem rede, sem subprocesso)."""
import json

from agente_langgraph import cli, llm, mcp_cliente


def test_atender_com_classificador_ollama(monkeypatch, capsys):
    usados = []

    def falso(mensagem):
        usados.append(mensagem)
        return "saldo"

    monkeypatch.setattr(llm, "classificador_ollama", lambda: falso)
    assert cli.main(["atender", "quanto tenho?", "--cliente", "c1", "--modelo", "ollama"]) == 0
    assert usados == ["quanto tenho?"]
    assert "resposta" in json.loads(capsys.readouterr().out)


def test_atender_com_mcp_usa_o_executor_do_cliente_mcp(monkeypatch, capsys):
    chamadas = []

    class ClienteFalso:
        def __enter__(self):
            return self

        def __exit__(self, *exc):
            return False

        def executor(self):
            def executar(nome, cliente_id):
                chamadas.append((nome, cliente_id))
                return "R$ 10,00"
            return executar

    monkeypatch.setattr(mcp_cliente, "ClienteMCP", ClienteFalso)
    assert cli.main(["atender", "qual meu saldo?", "--cliente", "c1", "--mcp"]) == 0
    assert chamadas and chamadas[0][1] == "c1"
    assert json.loads(capsys.readouterr().out)


def test_avaliar_imprime_falhas_e_sai_com_1(monkeypatch, capsys):
    monkeypatch.setattr(cli, "avaliar", lambda: {"ok": 1, "total": 2, "taxa": 0.5,
                                                  "falhas": [{"caso": "x", "obtido": "y"}]})
    assert cli.main(["avaliar"]) == 1
    saida = capsys.readouterr().out
    assert "1/2 casos (50%)" in saida and "FALHOU: x y" in saida

