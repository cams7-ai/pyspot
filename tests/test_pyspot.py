"""Contratos observáveis do laboratório, sem dependências externas."""

import subprocess
import sys
import unittest
from dataclasses import FrozenInstanceError, replace
from datetime import datetime, timedelta
from decimal import Decimal, Inexact, ROUND_DOWN, localcontext
from pathlib import Path

from pyspot.apresentacao import numero, percentual
from pyspot.cenarios import execucoes_exemplo, horario_compra
from pyspot.modelos import Carteira, Lado, Par
from pyspot.operacoes import aplicar_execucao, calcular_resultado, criar_execucao
from pyspot.validacao import (
    DadosInvalidosError, SaldoInsuficienteError, decimal_de_texto,
    em_utc, pertence_ao_intervalo,
)


class OperacoesTest(unittest.TestCase):
    def setUp(self):
        self.compra, self.venda = execucoes_exemplo()

    def test_resultados_exatos_e_carteiras(self):
        inicial = Carteira(Decimal("0"), Decimal("1000"))
        intermediaria = aplicar_execucao(inicial, self.compra)
        final = aplicar_execucao(intermediaria, self.venda)
        self.assertEqual(inicial, Carteira(Decimal("0"), Decimal("1000")))
        self.assertEqual(intermediaria, Carteira(Decimal("0.001"), Decimal("899.9")))
        self.assertEqual(final, Carteira(Decimal("0"), Decimal("1000.799")))
        self.assertIsNot(inicial, intermediaria)
        resultado = calcular_resultado(self.compra, self.venda)
        esperados = dict(compra_bruta="100", venda_bruta="101", taxa_compra="0.1",
                         taxa_venda="0.101", taxas_totais="0.201", desembolso="100.1",
                         recebimento_liquido="100.899", lucro_bruto="1", lucro_liquido="0.799",
                         retorno_percentual="0.7982017982017982017982017982")
        for campo, valor in esperados.items():
            with self.subTest(campo=campo):
                self.assertEqual(getattr(resultado, campo), Decimal(valor))
        self.assertEqual(percentual(resultado.retorno_percentual), "0,798202%")
        self.assertEqual(numero(final.usdt), "1000,799")

    def test_saldos_exatamente_suficientes(self):
        inicial = Carteira(Decimal("0"), Decimal("100.1"))
        comprada = aplicar_execucao(inicial, self.compra)
        self.assertEqual(comprada, Carteira(Decimal("0.001"), Decimal("0")))
        self.assertEqual(aplicar_execucao(comprada, self.venda),
                         Carteira(Decimal("0"), Decimal("100.899")))

    def test_rejeicoes_preservam_saldos(self):
        for execucao, carteira in (
            (self.compra, Carteira(Decimal("0"), Decimal("100"))),
            (self.venda, Carteira(Decimal("0"), Decimal("1000"))),
        ):
            with self.subTest(lado=execucao.lado):
                saldos = (carteira.btc, carteira.usdt)
                with self.assertRaises(SaldoInsuficienteError):
                    aplicar_execucao(carteira, execucao)
                self.assertEqual((carteira.btc, carteira.usdt), saldos)

    def test_taxa_zero(self):
        compra = criar_execucao("sem-taxa", Par(), Lado.COMPRA, Decimal("100000"),
                                Decimal("0.001"), horario_compra(), Decimal("0"))
        self.assertEqual(compra.taxa_usdt, Decimal("0"))
        self.assertEqual(aplicar_execucao(Carteira(Decimal("0"), Decimal("100")), compra),
                         Carteira(Decimal("0.001"), Decimal("0")))

    def test_arredondamento_somente_na_apresentacao(self):
        self.assertEqual(percentual(Decimal("1.2345665")), "1,234566%")
        self.assertEqual(percentual(Decimal("1.2345675")), "1,234568%")
        resultado = calcular_resultado(self.compra, self.venda)
        antes = resultado.retorno_percentual
        percentual(antes)
        self.assertEqual(resultado.retorno_percentual, antes)

    def test_aliquotas_invalidas(self):
        for taxa in (Decimal("-0.1"), Decimal("1"), Decimal("2"),
                     Decimal("NaN"), Decimal("sNaN"), Decimal("Infinity"), "0.001", None):
            with self.subTest(taxa=taxa), self.assertRaises(DadosInvalidosError):
                criar_execucao("inválida", Par(), Lado.COMPRA, Decimal("100000"),
                               Decimal("0.001"), horario_compra(), taxa)

    def test_resultado_rejeita_incompatibilidades(self):
        for compra, venda in (
            (self.venda, self.compra),
            (self.compra, self.compra),
            (self.venda, self.venda),
            (self.compra, replace(self.venda, par=Par("ETH", "USDT"))),
            (self.compra, replace(self.venda, quantidade=Decimal("0.002"))),
            (self.compra, replace(self.venda, horario=self.compra.horario - timedelta(seconds=1))),
            (None, self.venda),
        ):
            with self.subTest(compra=compra, venda=venda), self.assertRaises(DadosInvalidosError):
                calcular_resultado(compra, venda)

    def test_venda_no_mesmo_instante_e_resultado_com_perda(self):
        venda = replace(self.venda, horario=self.compra.horario, preco=Decimal("99000"))
        resultado = calcular_resultado(self.compra, venda)
        self.assertEqual(resultado.lucro_bruto, Decimal("-1"))
        self.assertEqual(resultado.lucro_liquido, Decimal("-1.201"))
        self.assertLess(resultado.retorno_percentual, 0)

    def test_carteira_rejeita_outro_ativo(self):
        with self.assertRaises(DadosInvalidosError):
            aplicar_execucao(Carteira(Decimal("0"), Decimal("1000")),
                             replace(self.compra, par=Par("ETH", "USDT")))

    def test_contexto_externo_preservado_e_resultados_reproduziveis(self):
        esperado = calcular_resultado(self.compra, self.venda)
        for precisao in (3, 50):
            with self.subTest(precisao=precisao), localcontext() as externo:
                externo.prec = precisao
                externo.rounding = ROUND_DOWN
                externo.traps[Inexact] = True
                externo.flags[Inexact] = True
                antes = str(externo)
                compra, venda = execucoes_exemplo()
                self.assertEqual(calcular_resultado(compra, venda), esperado)
                inicial = Carteira(Decimal("0"), Decimal("1000"))
                final = aplicar_execucao(aplicar_execucao(inicial, compra), venda)
                self.assertEqual(final.usdt, Decimal("1000.799"))
                self.assertEqual(percentual(esperado.retorno_percentual), "0,798202%")
                with self.assertRaises(SaldoInsuficienteError):
                    aplicar_execucao(Carteira(Decimal("0"), Decimal("100")), compra)
                self.assertEqual(str(externo), antes)


class ValidacaoTest(unittest.TestCase):
    def test_conversao_textual(self):
        for texto, esperado in (("0.1", "0.1"), ("-2.5", "-2.5"), ("1e-3", "0.001")):
            self.assertEqual(decimal_de_texto(texto), Decimal(esperado))

    def test_conversao_rejeita_entradas_invalidas(self):
        for entrada in ("", " ", " 1", "1 ", "abc", "1,2", "1_000", "1,000.2", "NaN",
                        "sNaN", "Infinity", "-Infinity", 0.1, 1, None, Decimal("1")):
            with self.subTest(entrada=entrada), self.assertRaises(DadosInvalidosError):
                decimal_de_texto(entrada)

    def test_construcao_direta_de_execucao_revalida_campos(self):
        compra, _ = execucoes_exemplo()
        casos = [
            {"identificador": ""}, {"identificador": " "}, {"identificador": 1},
            {"par": "BTC/USDT"}, {"lado": "compra"},
            {"par": Par("BTC", "BRL")}, {"horario": datetime(2026, 11, 5)},
            {"horario": "2026-11-05"}, {"taxa_usdt": Decimal("100")},
        ]
        for campo in ("preco", "quantidade", "taxa_usdt"):
            for valor in (Decimal("-1"), Decimal("NaN"), Decimal("sNaN"),
                          Decimal("Infinity"), Decimal("-Infinity"), "1", None):
                casos.append({campo: valor})
        casos.extend(({"preco": Decimal("0")}, {"quantidade": Decimal("0")}))
        for caso in casos:
            with self.subTest(caso=caso), self.assertRaises(DadosInvalidosError):
                replace(compra, **caso)

    def test_carteira_revalida_campos(self):
        for valor in (Decimal("-1"), Decimal("NaN"), Decimal("sNaN"), Decimal("Infinity"), "0", None):
            for campo in ("btc", "usdt"):
                dados = dict(btc=Decimal("0"), usdt=Decimal("0"))
                dados[campo] = valor
                with self.subTest(campo=campo, valor=valor), self.assertRaises(DadosInvalidosError):
                    Carteira(**dados)

    def test_par_revalida_campos(self):
        for base, cotacao in (("", "USDT"), (None, "USDT"), (" BTC", "USDT"),
                              ("BTC", "BTC"), ("BTC", ""), ("BTC", 1)):
            with self.subTest(base=base, cotacao=cotacao), self.assertRaises(DadosInvalidosError):
                Par(base, cotacao)

    def test_resultado_revalida_valores(self):
        resultado = calcular_resultado(*execucoes_exemplo())
        for campo in vars(resultado):
            for invalido in ("1", Decimal("NaN"), Decimal("Infinity")):
                with self.subTest(campo=campo, invalido=invalido), self.assertRaises(DadosInvalidosError):
                    replace(resultado, **{campo: invalido})

    def test_registros_impedem_reatribuicao(self):
        carteira = Carteira(Decimal("0"), Decimal("1"))
        with self.assertRaises(FrozenInstanceError):
            carteira.usdt = Decimal("2")


class HorariosTest(unittest.TestCase):
    def test_normalizacao_preserva_instante(self):
        local = datetime.fromisoformat("2026-11-05T09:00:00-03:00")
        self.assertEqual(em_utc(local).isoformat(), "2026-11-05T12:00:00+00:00")
        compra, _ = execucoes_exemplo()
        self.assertEqual(replace(compra, horario=local).horario.isoformat(),
                         "2026-11-05T12:00:00+00:00")

    def test_limites_semiabertos(self):
        inicio = horario_compra()
        fim = inicio + timedelta(minutes=1)
        self.assertTrue(pertence_ao_intervalo(inicio, inicio, fim))
        self.assertTrue(pertence_ao_intervalo(inicio + timedelta(seconds=30), inicio, fim))
        self.assertFalse(pertence_ao_intervalo(fim, inicio, fim))
        self.assertFalse(pertence_ao_intervalo(inicio - timedelta(seconds=1), inicio, fim))

    def test_intervalos_invalidos_e_datas_sem_fuso(self):
        inicio = horario_compra()
        ingenuo = inicio.replace(tzinfo=None)
        for datas in ((inicio, inicio, inicio), (inicio, inicio + timedelta(seconds=1), inicio),
                      (ingenuo, inicio, inicio + timedelta(minutes=1)),
                      (inicio, ingenuo, inicio + timedelta(minutes=1)),
                      (inicio, inicio, ingenuo)):
            with self.subTest(datas=datas), self.assertRaises(DadosInvalidosError):
                pertence_ao_intervalo(*datas)


class TerminalTest(unittest.TestCase):
    def executar(self, *argumentos):
        return subprocess.run([sys.executable, "-m", "pyspot", *argumentos],
                              cwd=Path(__file__).resolve().parents[1],
                              capture_output=True, text=True, check=False)

    def test_todos_os_cenarios_na_ordem_e_resultados(self):
        processo = self.executar()
        self.assertEqual(processo.returncode, 0, processo.stderr)
        marcadores = [processo.stdout.index(f"\n{letra}.") for letra in "ABCDE"]
        self.assertEqual(marcadores, sorted(marcadores))
        for trecho in ("1000,799 USDT", "0,798202%", "Fim pertence: False",
                       "Contexto externo preservado: True", "Carteira original preservada: True"):
            self.assertIn(trecho, processo.stdout)

    def test_cenarios_individuais(self):
        for cenario in "abcde":
            with self.subTest(cenario=cenario):
                processo = self.executar("--cenario", cenario)
                self.assertEqual(processo.returncode, 0, processo.stderr)
                self.assertIn(f"\n{cenario.upper()}.", processo.stdout)
                for outro in set("abcde") - {cenario}:
                    self.assertNotIn(f"\n{outro.upper()}.", processo.stdout)

    def test_ajuda_e_opcao_invalida(self):
        ajuda = self.executar("--help")
        self.assertEqual(ajuda.returncode, 0)
        self.assertIn("--cenario", ajuda.stdout)
        invalido = self.executar("--cenario", "z")
        self.assertEqual(invalido.returncode, 2)


if __name__ == "__main__":
    unittest.main()
