import argparse
import json
import sys

from .avaliacao import avaliar
from .grafo import atender, construir


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="agente-langgraph")
    sub = p.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("atender", help="responde uma mensagem")
    a.add_argument("mensagem")
    a.add_argument("--cliente", default=None)
    sub.add_parser("avaliar", help="roda os casos de teste e imprime a taxa")
    args = p.parse_args(argv)
    if args.cmd == "atender":
        r = atender(construir(), args.mensagem, args.cliente)
        print(json.dumps(r, ensure_ascii=False, indent=2))
        return 0
    r = avaliar()
    print(f"{r['ok']}/{r['total']} casos ({r['taxa']:.0%})")
    for f in r["falhas"]:
        print("FALHOU:", f["caso"], f["obtido"])
    return 0 if not r["falhas"] else 1


if __name__ == "__main__":
    sys.exit(main())
