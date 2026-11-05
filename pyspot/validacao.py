"""Conversão explícita, contratos de valores e horários UTC."""

import re
from datetime import datetime, timezone
from decimal import Context, Decimal, InvalidOperation, ROUND_HALF_EVEN


class DadosInvalidosError(ValueError):
    """Entrada ou combinação de registros incompatível com o laboratório."""


class SaldoInsuficienteError(ValueError):
    """Carteira sem saldo suficiente para aplicar a execução completa."""


def contexto_decimal() -> Context:
    """Contexto novo: não herda precisão, flags ou traps do chamador."""
    return Context(prec=28, rounding=ROUND_HALF_EVEN)


def decimal_de_texto(texto: str) -> Decimal:
    """Aceita ponto decimal e expoente opcional, sem milhares ou underscores."""
    if not isinstance(texto, str) or not re.fullmatch(
        r"[+-]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)(?:[eE][+-]?[0-9]+)?", texto
    ):
        raise DadosInvalidosError("Informe texto decimal finito com ponto, sem separador de milhares.")
    try:
        valor = Decimal(texto)
    except InvalidOperation as erro:
        raise DadosInvalidosError("Texto decimal inválido.") from erro
    if not valor.is_finite():
        raise DadosInvalidosError("Texto deve representar um decimal finito.")
    return valor


def validar_decimal(valor: Decimal, nome: str, *, positivo: bool = False) -> None:
    if not isinstance(valor, Decimal) or not valor.is_finite():
        raise DadosInvalidosError(f"{nome} deve ser Decimal finito.")
    if valor < 0 or (positivo and valor == 0):
        limite = "maior que zero" if positivo else "não negativo"
        raise DadosInvalidosError(f"{nome} deve ser {limite}.")


def validar_aliquota(aliquota: Decimal) -> None:
    validar_decimal(aliquota, "alíquota")
    if aliquota >= 1:
        raise DadosInvalidosError("Alíquota deve estar no intervalo 0 <= taxa < 1.")


def em_utc(horario: datetime) -> datetime:
    if not isinstance(horario, datetime) or horario.utcoffset() is None:
        raise DadosInvalidosError("Horário deve ser datetime com fuso.")
    return horario.astimezone(timezone.utc)


def pertence_ao_intervalo(evento: datetime, inicio: datetime, fim: datetime) -> bool:
    evento, inicio, fim = map(em_utc, (evento, inicio, fim))
    if inicio >= fim:
        raise DadosInvalidosError("Início deve ser anterior ao fim.")
    return inicio <= evento < fim
