# PySpot — Sprint 02

Laboratório local de Python aplicado a execuções Spot fictícias de BTC/USDT.
Pratica `Decimal`, modelos de dados, validação, funções puras, exceções,
horários UTC e testes. É independente da Sprint 01 e não usa rede ou dinheiro real.

O diretório existente `pyspot` é a raiz do projeto; o subdiretório `pyspot/`
é o pacote Python. O escopo original permanece em [docs/sprint02.md](docs/sprint02.md).

## Requisitos e execução

Python **3.11 ou superior**, somente biblioteca padrão. Não é necessário instalar
dependências. Execute na raiz deste repositório:

```bash
python --version
python -m pyspot
python -m pyspot --cenario a
python -m pyspot --cenario b
python -m pyspot --cenario c
python -m pyspot --cenario d
python -m pyspot --cenario e
python -m pyspot --help
python -m unittest discover -s tests -v
```

Se `python` não apontar para uma versão compatível, use `python3` nos comandos.
Sem `--cenario`, a ordem é sempre A, B, C, D, E. Cada cenário começa com seu
próprio estado e horários fixos. Argumentos inválidos encerram com código 2;
falhas inesperadas propagam e encerram com código diferente de zero. Apenas os
erros esperados dos exemplos C, D e E são capturados e explicados.

## Estrutura

```text
pyproject.toml                 metadados e versão mínima de Python
pyspot/
  __init__.py                 identificação do pacote
  __main__.py                 argumentos e seleção dos cenários
  validacao.py                conversão, exceções, contexto decimal e UTC
  modelos.py                  Par, Lado, Execucao, Carteira e Resultado
  operacoes.py                registro, aplicação e resultado financeiro
  apresentacao.py             números, percentuais e carteiras no terminal
  cenarios.py                 exemplos A a E
tests/test_pyspot.py           contratos financeiros, temporais e de terminal
docs/sprint02.md               escopo da sprint
docs/sprint02-glossario.md     conceitos e comparações com Java
docs/sprint02-validacao.md     comandos executados e resultados observados
```

## Exemplo de saída do cenário B

Trecho de `python -m pyspot --cenario b` (a saída inclui também horários e explicações):

```text
Antes da compra: 1000 USDT e 0 BTC
Compra bruta: 100 USDT; taxa: 0,1 USDT; desembolso (bruto + taxa): 100,1 USDT
Após a compra / antes da venda: 899,9 USDT e 0,001 BTC
Venda bruta: 101 USDT; taxa: 0,101 USDT; recebimento líquido (bruto - taxa): 100,899 USDT
Após a venda: 1000,799 USDT e 0 BTC
Taxas totais: 0,201 USDT; lucro bruto: 1 USDT; lucro líquido: 0,799 USDT
Retorno líquido sobre desembolso de 100,1 USDT: 0,798202%
```

## Valores, cálculos e contratos

A entrada financeira é **texto com ponto decimal**, sem separador de milhares:
`decimal_de_texto("100000")`, `decimal_de_texto("0.001")`. Expoente decimal é
aceito, como `"1e-3"`. Espaços, vírgulas e underscores são rejeitados.
A conversão aceita números negativos finitos; o domínio rejeita os negativos
onde eles não fazem sentido. `NaN`, `sNaN`, infinitos, texto vazio ou malformado
e tipos diferentes de string são rejeitados antes de entrar no fluxo financeiro.
Não há conversão intermediária para `float`. Seu uso fica nos exemplos do
problema de representação e na entrada propositalmente inválida do cenário C.

Os modelos validam também construções diretas: tipagem não garante tipos em
tempo de execução. Preço e quantidade são positivos; saldos e taxas em USDT
são não negativos e finitos. A alíquota padrão é `Decimal("0.001")` (0,10%) e
deve estar em `0 <= taxa < 1`. Uma execução construída diretamente exige taxa
em USDT menor que o bruto, consistente com esse intervalo.

Os cálculos usam um contexto decimal **local**, com precisão de 28 dígitos
significativos e `ROUND_HALF_EVEN`. Precisão, arredondamento, traps e flags do
chamador são preservados. Não há quantização a cada operação. `Decimal` tem
precisão finita: divisões, e operações com muitos dígitos, podem arredondar no
contexto local. Na apresentação, o dinheiro mostra todas as casas disponíveis
sem zeros finais desnecessários; o retorno tem seis casas decimais. São regras
do laboratório, não regras de precisão ou tamanho de lote de uma exchange.

Com preço `p`, quantidade `q` e alíquota `t`:

| Valor | Fórmula |
| --- | --- |
| Bruto | `p * q` |
| Taxa em USDT | `bruto * t` |
| Desembolso da compra | `bruto_compra + taxa_compra` |
| Recebimento líquido da venda | `bruto_venda - taxa_venda` |
| Taxas totais | `taxa_compra + taxa_venda` |
| Lucro bruto | `bruto_venda - bruto_compra` |
| Lucro líquido | `recebimento_liquido - desembolso` |
| Retorno líquido (%) | `lucro_liquido / desembolso * 100` |

Na compra, BTC aumenta em `q` e USDT diminui pelo desembolso. Na venda, BTC
diminui em `q` e USDT aumenta pelo recebimento líquido. Os preços já são preços
de execução: não se desconta spread ou slippage novamente. Resultado completo
exige compra e venda do mesmo par e quantidade, com venda em horário igual ou
posterior. Perdas são aceitas; posições parcialmente encerradas são rejeitadas.

`criar_execucao` registra uma execução fictícia **já confirmada**; uma solicitação
de ordem não é uma execução. `aplicar_execucao` retorna nova carteira e mantém
a anterior. A carteira suporta somente BTC/USDT; outros pares cotados em USDT
podem ser representados e comparados, mas não aplicados a essa carteira.

`DadosInvalidosError` indica entrada ou combinação de registros incompatível.
`SaldoInsuficienteError` indica falta de USDT para bruto mais taxa ou falta de
BTC para vender. Nenhuma rejeição altera a carteira ou ajusta a quantidade.
Os registros usam `dataclass(frozen=True)`: impede reatribuição normal dos campos,
mas não torna profundamente imutáveis objetos mutáveis que fossem armazenados
neles. Os campos adotados aqui contêm valores imutáveis.

Horários devem ter fuso e são normalizados para UTC preservando o instante:
`2026-11-05T09:00:00-03:00` equivale a `2026-11-05T12:00:00+00:00`.
Intervalos usam `[início, fim)`: incluem início, excluem fim e exigem início
anterior ao fim. Datas sem fuso são rejeitadas.

## Limites

Cada execução é aplicada uma única vez pelo cenário. Não há deduplicação,
histórico persistente, API de exchange, credenciais, envio de ordens, reservas,
livro de ofertas, casamento de ordens, estratégias, backtest, banco de dados,
candles, interface web, Docker, AWS ou assincronismo. Taxas são somente em USDT,
sem BTC/BNB ou distinção maker/taker. O exemplo não é recomendação de investimento.

Consulte o [glossário](docs/sprint02-glossario.md) e o
[registro de validação](docs/sprint02-validacao.md).
