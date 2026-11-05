"""Formatação em português, isolada dos cálculos financeiros."""

from decimal import Decimal, localcontext

from .modelos import Carteira
from .validacao import contexto_decimal


def numero(valor: Decimal) -> str:
    texto = format(valor, "f")
    if "." in texto:
        texto = texto.rstrip("0").rstrip(".")
    return texto.replace(".", ",")


def percentual(valor: Decimal) -> str:
    with localcontext(contexto_decimal()):
        return format(valor, ".6f").replace(".", ",") + "%"


def mostrar_carteira(rotulo: str, carteira: Carteira) -> None:
    print(f"{rotulo}: {numero(carteira.usdt)} USDT e {numero(carteira.btc)} BTC")
