"""Funções puras: calculam valores e retornam novos registros, sem apresentação."""

from datetime import datetime
from decimal import Decimal, localcontext

from .modelos import Carteira, Execucao, Lado, Par, Resultado
from .validacao import (
    DadosInvalidosError, SaldoInsuficienteError, contexto_decimal,
    validar_aliquota, validar_decimal,
)


def criar_execucao(
    identificador: str, par: Par, lado: Lado, preco: Decimal,
    quantidade: Decimal, horario: datetime, aliquota: Decimal = Decimal("0.001"),
) -> Execucao:
    """Registra uma execução fictícia já confirmada; não envia uma ordem."""
    validar_decimal(preco, "preço", positivo=True)
    validar_decimal(quantidade, "quantidade", positivo=True)
    validar_aliquota(aliquota)
    with localcontext(contexto_decimal()):
        taxa = preco * quantidade * aliquota
        return Execucao(identificador, par, lado, preco, quantidade, taxa, horario)


def aplicar_execucao(carteira: Carteira, execucao: Execucao) -> Carteira:
    if not isinstance(carteira, Carteira) or not isinstance(execucao, Execucao):
        raise DadosInvalidosError("Aplicação exige Carteira e Execucao válidas.")
    if execucao.par != Par():
        raise DadosInvalidosError("Esta carteira só mantém BTC e USDT.")
    with localcontext(contexto_decimal()):
        bruto = execucao.preco * execucao.quantidade
        if execucao.lado is Lado.COMPRA:
            custo = bruto + execucao.taxa_usdt
            if carteira.usdt < custo:
                raise SaldoInsuficienteError("USDT insuficiente para valor bruto mais taxa da compra.")
            return Carteira(carteira.btc + execucao.quantidade, carteira.usdt - custo)
        if carteira.btc < execucao.quantidade:
            raise SaldoInsuficienteError("BTC insuficiente para a quantidade da venda.")
        return Carteira(carteira.btc - execucao.quantidade, carteira.usdt + (bruto - execucao.taxa_usdt))


def calcular_resultado(compra: Execucao, venda: Execucao) -> Resultado:
    if not isinstance(compra, Execucao) or not isinstance(venda, Execucao):
        raise DadosInvalidosError("Resultado exige duas execuções válidas.")
    if compra.lado is not Lado.COMPRA or venda.lado is not Lado.VENDA:
        raise DadosInvalidosError("Resultado exige uma compra seguida de uma venda.")
    if compra.par != venda.par or compra.quantidade != venda.quantidade:
        raise DadosInvalidosError("Compra e venda devem ter o mesmo par e quantidade.")
    if venda.horario < compra.horario:
        raise DadosInvalidosError("Venda não pode ser anterior à compra.")
    with localcontext(contexto_decimal()):
        compra_bruta = compra.preco * compra.quantidade
        venda_bruta = venda.preco * venda.quantidade
        desembolso = compra_bruta + compra.taxa_usdt
        recebimento = venda_bruta - venda.taxa_usdt
        lucro = recebimento - desembolso
        return Resultado(
            compra_bruta, venda_bruta, compra.taxa_usdt, venda.taxa_usdt,
            compra.taxa_usdt + venda.taxa_usdt, desembolso, recebimento,
            venda_bruta - compra_bruta, lucro, lucro / desembolso * Decimal("100"),
        )
