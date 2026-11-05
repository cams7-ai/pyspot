"""Interface local: python -m pyspot [--cenario a|b|c|d|e]."""

import argparse

from .cenarios import cenario_a, cenario_b, cenario_c, cenario_d, cenario_e


class Argumentos(argparse.ArgumentParser):
    def format_help(self) -> str:
        return super().format_help().replace("usage:", "Uso:", 1)

    def error(self, message: str) -> None:
        self.exit(2, "Argumentos inválidos. Use --cenario com a, b, c, d ou e.\n"
                  "Use --help para consultar os comandos.\n")


def main() -> None:
    parser = Argumentos(
        description="PySpot — cenários didáticos de execuções Spot fictícias, sem rede.",
        usage="python -m pyspot [--cenario {a,b,c,d,e}] [--help]", add_help=False,
    )
    parser._optionals.title = "Opções"
    parser.add_argument("-h", "--help", action="help", help="mostra esta ajuda e encerra")
    parser.add_argument("--cenario", choices=tuple("abcde"), help="executa apenas o cenário escolhido (a até e)")
    argumentos = parser.parse_args()
    cenarios = dict(zip("abcde", (cenario_a, cenario_b, cenario_c, cenario_d, cenario_e)))
    print("PySpot: laboratório local. Cada execução fictícia é aplicada uma única vez.")
    for chave in (argumentos.cenario,) if argumentos.cenario else cenarios:
        cenarios[chave]()


if __name__ == "__main__":
    main()
