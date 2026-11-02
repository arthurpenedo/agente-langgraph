"""Classificador de intenção com modelo aberto (Ollama). Opcional: cai nas regras se falhar."""
import json
import urllib.request

from . import ferramentas
from .grafo import classificar

VALIDAS = set(ferramentas.FERRAMENTAS) | {"sensivel", "desconhecida"}


def classificador_ollama(modelo: str = "qwen2.5:3b", url: str = "http://localhost:11434", abrir=urllib.request.urlopen):
    """Devolve uma função `mensagem -> intenção`. Resposta fora da lista ou erro de rede usa as regras."""

    def classificar_llm(mensagem: str) -> str:
        pedido = {
            "model": modelo,
            "stream": False,
            "options": {"temperature": 0},
            "prompt": f"Classifique a mensagem em UMA palavra entre: {', '.join(sorted(VALIDAS))}.\n"
                      f"Mensagem: {mensagem}\nPalavra:",
        }
        req = urllib.request.Request(f"{url}/api/generate", json.dumps(pedido).encode(),
                                     {"Content-Type": "application/json"})
        try:
            with abrir(req, timeout=60) as r:
                resposta = json.load(r)["response"].strip().lower()
        except (OSError, KeyError, ValueError):
            return classificar(mensagem)
        # nunca deixa o modelo liberar dado sensível: as regras têm a palavra final
        if classificar(mensagem) == "sensivel":
            return "sensivel"
        return resposta if resposta in VALIDAS else classificar(mensagem)

    return classificar_llm
