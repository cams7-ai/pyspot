"""Exemplos determinísticos; cada execução é aplicada uma única vez."""

from collections.abc import Callable
from datetime import datetime, timedelta
from decimal import Decimal, getcontext, localcontext

from .apresentacao import mostrar_carteira, numero, percentual
from .modelos import Carteira, Execucao, Lado, Par
from .operacoes import aplicar_execucao, calcular_resultado, criar_execucao
from .validacao import (
    DadosInvalidosError, SaldoInsuficienteError, contexto_decimal,
    decimal_de_texto, em_utc, pertence_ao_intervalo,
)


def horario_compra() -> datetime:
    return datetime.fromisoformat("2026-11-05T12:00:00+00:00")


def execucoes_exemplo() -> tuple[Execucao, Execucao]:
    compra = criar_execucao("compra-1", Par(), Lado.COMPRA, Decimal("100000"),
                            Decimal("0.001"), horario_compra())
    venda = criar_execucao("venda-1", Par(), Lado.VENDA, Decimal("101000"),
                           Decimal("0.001"), horario_compra() + timedelta(minutes=5))
    return compra, venda


def erro_esperado(rotulo: str, acao: Callable[[], object], tipo: type[ValueError]) -> None:
    try:
        acao()
    except tipo as erro:
        print(f"{rotulo}: rejeitado — {erro}")
    else:
        raise AssertionError(f"{rotulo}: o erro esperado não ocorreu.")


def cenario_a() -> None:
    print("\nA. Precisão decimal")
    print(f"float: 0.1 + 0.2 = {0.1 + 0.2}")
    externo = getcontext().copy()
    with localcontext(contexto_decimal()):
        soma = decimal_de_texto("0.1") + decimal_de_texto("0.2")
    print(f'Decimal: Decimal("0.1") + Decimal("0.2") = {soma}')
    print("float usa representação binária aproximada; Decimal parte de textos decimais.")
    print("Decimal também tem precisão finita: usamos 28 dígitos e ROUND_HALF_EVEN.")
    print(f"Contexto externo preservado: {str(getcontext()) == str(externo)}")


def cenario_b() -> None:
    print("\nB. Compra e venda completas — taxa fictícia de 0,10% em USDT")
    compra, venda = execucoes_exemplo()
    inicial = Carteira(Decimal("0"), Decimal("1000"))
    apos_compra = aplicar_execucao(inicial, compra)
    final = aplicar_execucao(apos_compra, venda)
    resultado = calcular_resultado(compra, venda)
    mostrar_carteira("Antes da compra", inicial)
    print(f"Compra confirmada em {compra.horario.isoformat()}: 0,001 BTC a 100000 USDT")
    print(f"Compra bruta: {numero(resultado.compra_bruta)} USDT; "
          f"taxa: {numero(resultado.taxa_compra)} USDT; "
          f"desembolso (bruto + taxa): {numero(resultado.desembolso)} USDT")
    mostrar_carteira("Após a compra / antes da venda", apos_compra)
    print(f"Venda confirmada em {venda.horario.isoformat()}: 0,001 BTC a 101000 USDT")
    print(f"Venda bruta: {numero(resultado.venda_bruta)} USDT; "
          f"taxa: {numero(resultado.taxa_venda)} USDT; "
          f"recebimento líquido (bruto - taxa): {numero(resultado.recebimento_liquido)} USDT")
    mostrar_carteira("Após a venda", final)
    print(f"Taxas totais: {numero(resultado.taxas_totais)} USDT; "
          f"lucro bruto: {numero(resultado.lucro_bruto)} USDT; "
          f"lucro líquido: {numero(resultado.lucro_liquido)} USDT")
    print(f"Retorno líquido sobre desembolso de 100,1 USDT: {percentual(resultado.retorno_percentual)}")
    print("Os preços já são de execução; spread e slippage não são descontados novamente.")


def cenario_c() -> None:
    print("\nC. Entradas inválidas")
    casos = [
        ("Preço negativo", {"preco": Decimal("-1")}),
        ("Quantidade zero", {"quantidade": Decimal("0")}),
        ("Alíquota negativa", {"aliquota": Decimal("-0.001")}),
        ("Alíquota igual a 1", {"aliquota": Decimal("1")}),
    ]
    for rotulo, mudancas in casos:
        dados = dict(identificador="inválida", par=Par(), lado=Lado.COMPRA,
                     preco=Decimal("100000"), quantidade=Decimal("0.001"), horario=horario_compra())
        dados.update(mudancas)
        erro_esperado(rotulo, lambda: criar_execucao(**dados), DadosInvalidosError)
    # float aqui é somente uma entrada propositalmente inválida, nunca um valor financeiro.
    for entrada in ("NaN", "sNaN", "Infinity", "-Infinity", "", "abc", "1,25", 0.1):
        erro_esperado(f"Conversão de {entrada!r}", lambda: decimal_de_texto(entrada), DadosInvalidosError)


def cenario_d() -> None:
    print("\nD. Saldo insuficiente")
    compra, venda = execucoes_exemplo()
    for execucao in (compra, venda):
        carteira = Carteira(Decimal("0"), Decimal("100"))
        antes = Carteira(carteira.btc, carteira.usdt)
        mostrar_carteira("Antes da tentativa", carteira)
        erro_esperado(execucao.lado.value, lambda: aplicar_execucao(carteira, execucao),
                      SaldoInsuficienteError)
        mostrar_carteira("Após a rejeição", carteira)
        print(f"Carteira original preservada: {carteira == antes}")
    print("A compra exige 100,1 USDT: os 100 USDT disponíveis não cobrem a taxa de 0,1 USDT.")


def cenario_e() -> None:
    print("\nE. UTC e limites de intervalo")
    local = datetime.fromisoformat("2026-11-05T09:00:00-03:00")
    inicio = horario_compra()
    fim = inicio + timedelta(minutes=1)
    print(f"{local.isoformat()} = {em_utc(local).isoformat()}: {em_utc(local) == inicio}")
    erro_esperado("Data sem fuso", lambda: em_utc(datetime(2026, 11, 5, 12)), DadosInvalidosError)
    print(f"Intervalo [{inicio.isoformat()}, {fim.isoformat()})")
    print(f"Início pertence: {pertence_ao_intervalo(inicio, inicio, fim)}")
    print(f"Fim pertence: {pertence_ao_intervalo(fim, inicio, fim)}")
