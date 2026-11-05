"""Registros validados; frozen impede reatribuição, não imutabilidade profunda."""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal, localcontext
from enum import Enum

from .validacao import DadosInvalidosError, contexto_decimal, em_utc, validar_decimal


class Lado(Enum):
    COMPRA = "compra"
    VENDA = "venda"


@dataclass(frozen=True)
class Par:
    base: str = "BTC"
    cotacao: str = "USDT"

    def __post_init__(self) -> None:
        for ativo in (self.base, self.cotacao):
            if not isinstance(ativo, str) or not ativo.strip() or ativo != ativo.strip():
                raise DadosInvalidosError("Ativos devem ser textos não vazios, sem espaços nas pontas.")
        if self.base == self.cotacao:
            raise DadosInvalidosError("Base e cotação devem ser diferentes.")


@dataclass(frozen=True)
class Execucao:
    identificador: str
    par: Par
    lado: Lado
    preco: Decimal
    quantidade: Decimal
    taxa_usdt: Decimal
    horario: datetime

    def __post_init__(self) -> None:
        if not isinstance(self.identificador, str) or not self.identificador.strip():
            raise DadosInvalidosError("Identificador deve ser texto não vazio.")
        if not isinstance(self.par, Par) or not isinstance(self.lado, Lado):
            raise DadosInvalidosError("Execução exige Par e Lado válidos.")
        if self.par.cotacao != "USDT":
            raise DadosInvalidosError("Taxas deste laboratório são cobradas em USDT.")
        validar_decimal(self.preco, "preço", positivo=True)
        validar_decimal(self.quantidade, "quantidade", positivo=True)
        validar_decimal(self.taxa_usdt, "taxa em USDT")
        with localcontext(contexto_decimal()):
            if self.taxa_usdt >= self.preco * self.quantidade:
                raise DadosInvalidosError("Taxa em USDT deve ser menor que o valor bruto.")
        object.__setattr__(self, "horario", em_utc(self.horario))


@dataclass(frozen=True)
class Carteira:
    btc: Decimal
    usdt: Decimal

    def __post_init__(self) -> None:
        validar_decimal(self.btc, "saldo BTC")
        validar_decimal(self.usdt, "saldo USDT")


@dataclass(frozen=True)
class Resultado:
    compra_bruta: Decimal
    venda_bruta: Decimal
    taxa_compra: Decimal
    taxa_venda: Decimal
    taxas_totais: Decimal
    desembolso: Decimal
    recebimento_liquido: Decimal
    lucro_bruto: Decimal
    lucro_liquido: Decimal
    retorno_percentual: Decimal

    def __post_init__(self) -> None:
        for nome, valor in vars(self).items():
            # Lucros e retorno podem ser negativos em uma operação com perda.
            if nome in ("lucro_bruto", "lucro_liquido", "retorno_percentual"):
                if not isinstance(valor, Decimal) or not valor.is_finite():
                    raise DadosInvalidosError(f"{nome} deve ser Decimal finito.")
            else:
                validar_decimal(valor, nome, positivo=nome in ("compra_bruta", "venda_bruta", "desembolso"))
