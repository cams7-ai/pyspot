# Registro de validação — Sprint 02

Validação executada em **5 de novembro de 2026**, na raiz do repositório
`pyspot`, com **Python 3.12.14**, sem instalação de dependências.

## Passo a passo e comandos executados

1. Conferido o escopo em `docs/sprint02.md` e o conteúdo existente. A raiz já
   se chamava `pyspot`, então foi reutilizada; `pyspot/` é o pacote importável.
   O documento original foi preservado.
2. Criados os modelos, validações, operações puras, apresentação e cenários.
3. Executados os comandos abaixo na raiz, sem configuração de `PYTHONPATH`:

| Comando executado | Resultado observado | Código de saída |
| --- | --- | --- |
| `python --version` | Python 3.12.14 | 0 |
| `python -m pyspot` | Cenários A, B, C, D e E, nessa ordem, com resultados descritos abaixo | 0 |
| `python -m pyspot --cenario a` | Apenas A; float aproximado, Decimal com resultado 0.3 e contexto preservado | 0 |
| `python -m pyspot --cenario b` | Apenas B; valores financeiros iguais aos esperados | 0 |
| `python -m pyspot --cenario c` | Apenas C; entradas inválidas rejeitadas com explicações | 0 |
| `python -m pyspot --cenario d` | Apenas D; compra e venda sem saldo rejeitadas e carteiras preservadas | 0 |
| `python -m pyspot --cenario e` | Apenas E; equivalência UTC, rejeição de data sem fuso e limites corretos | 0 |
| `python -m pyspot --help` | Uso, descrição e opções em português | 0 |
| `python -m unittest discover -s tests -v` | **23 testes passaram**, resultado `OK` na execução final | 0 |
| `git diff --check` | Nenhum problema reportado no diff rastreado; arquivos novos ainda não estavam staged | 0 |

4. A suíte também executou o CLI em subprocessos: todos os cenários juntos,
   os cinco cenários individuais, ajuda e `--cenario z`. O argumento inválido
   retornou código **2**, como esperado.
5. O teste de contexto usou precisões externas 3 e 50, arredondamento
   `ROUND_DOWN`, trap de `Inexact` ativada e flag já marcada. Criação das
   execuções, cálculos, aplicação, formatação e rejeição de saldo preservaram
   o contexto do chamador. Os resultados permaneceram iguais aos valores de referência.

## Valores esperados e observados

Todos os valores da tabela foram conferidos pela saída e por asserções com
`Decimal`; o percentual formatado foi conferido separadamente do valor interno.

| Etapa/valor | Esperado | Observado |
| --- | --- | --- |
| Carteira inicial | 1000 USDT e 0 BTC | Igual |
| Compra bruta | 100 USDT | Igual |
| Taxa de compra | 0,1 USDT | Igual |
| Desembolso | 100,1 USDT | Igual |
| Carteira após compra | 899,9 USDT e 0,001 BTC | Igual |
| Venda bruta | 101 USDT | Igual |
| Taxa de venda | 0,101 USDT | Igual |
| Recebimento líquido | 100,899 USDT | Igual |
| Taxas totais | 0,201 USDT | Igual |
| Lucro bruto | 1 USDT | Igual |
| Lucro líquido | 0,799 USDT | Igual |
| Carteira final | 1000,799 USDT e 0 BTC | Igual |
| Retorno exibido | 0,798202% | Igual |
| Retorno interno com precisão 28 | 0.7982017982017982017982017982 | Igual |

No cenário A, `0.1 + 0.2` exibiu `0.30000000000000004`; a soma de `Decimal`
construídos de strings exibiu `0.3`. A mensagem de contexto preservado foi `True`.

No cenário C, foram rejeitados preço negativo, quantidade zero, alíquotas
negativa e igual a 1, `NaN`, `sNaN`, infinitos, texto vazio ou malformado,
vírgula decimal e um float passado à conversão. Nos testes, construções diretas
dos modelos também recusaram valores e tipos inválidos. Taxa zero foi aceita.

No cenário D, uma compra de 100 USDT brutos foi recusada com saldo de 100 USDT,
pois faltavam 0,1 USDT de taxa. A venda de 0,001 BTC com saldo zero também foi
recusada. As carteiras antes e depois permaneceram com 100 USDT e 0 BTC.
Os testes conferiram ainda compra e venda com saldos exatamente suficientes.

No cenário E, `2026-11-05T09:00:00-03:00` foi normalizado para
`2026-11-05T12:00:00+00:00`. Data ingênua foi rejeitada; no intervalo
`[12:00:00, 12:01:00)` UTC, o início pertenceu e o fim ficou fora.
Testes adicionais recusaram intervalos invertidos, vazios e datas sem fuso em
cada posição do intervalo.

A suíte recusou pares, quantidades, lados e cronologia incompatíveis no
resultado completo. Aceitou venda no mesmo instante e resultado com prejuízo.
Verificou também bloqueio de reatribuição dos registros e empates de
arredondamento na apresentação com `ROUND_HALF_EVEN`.

## Pendências e limites reais

Não há pendências funcionais conhecidas no escopo desta sprint. A execução foi
validada com Python 3.12.14; Python 3.11 e outros sistemas operacionais não foram
executados neste ambiente. O código usa recursos disponíveis em Python 3.11+.

Não foram implementados rede, exchange, ordens reais, persistência, deduplicação,
estratégias ou posições parcialmente encerradas. Cada execução é aplicada uma
única vez pelos cenários. A carteira é exclusiva de BTC/USDT e as taxas são em
USDT. Precisão e formatação são convenções didáticas; não reproduzem filtros de
uma exchange. Não foram feitos commits nem publicação.
