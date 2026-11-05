# Sprint 02 — Python aplicado ao robô

**Projeto fictício:** PySpot  
**Diretório sugerido:** `pyspot`  
**Etapa de estudo:** 2 — Python aplicado ao robô  
**Objetivo:** criar um exemplo didático de operações Spot para praticar valores decimais, modelos de dados, validações, horários UTC, tratamento de erros e testes.

O PySpot é um projeto de exemplo independente do SpotLab e do robô principal. Não depende dos arquivos da Sprint 01. Os conceitos de compra, venda e custos da etapa anterior serão usados como contexto para aprender Python.

## 1. Conhecimentos trabalhados

| Conhecimento | Aplicação no exemplo |
| --- | --- |
| `Decimal` e `localcontext` | Calcular preços, quantidades, taxas e resultado líquido |
| `dataclass(frozen=True)` | Representar valores e registros de execução |
| `Enum` e anotações de tipo | Identificar compra e venda e esclarecer contratos |
| Funções puras | Separar cálculo de alteração de estado e apresentação |
| Validação e exceções | Rejeitar entradas inválidas sem modificar saldos |
| `datetime` com fuso UTC | Registrar e comparar eventos sem ambiguidade |
| `unittest` | Conferir resultados financeiros e invariantes observáveis |
| Organização em pacote | Executar exemplos pelo terminal |

## 2. Resultado esperado

Um pacote Python executável com exemplos determinísticos, explicações em português, testes e documentação. A implementação deve facilitar a leitura por alguém com experiência em Java, sem exigir frameworks ou bibliotecas de terceiros.

## 3. Prompt autossuficiente de execução

Copie o bloco abaixo para o agente responsável pela implementação. Ele contém o escopo completo; não é necessário ter acesso a outros documentos.

````text
Você é um desenvolvedor Python experiente. Implemente a Sprint 02 do projeto fictício PySpot, um laboratório de Python aplicado à representação e ao cálculo de operações Spot.

OBJETIVO E CONTEXTO

O usuário conhece Java, APIs e bancos de dados. Agora precisa praticar recursos de Python usados em um futuro robô de criptomoedas. Use operações fictícias de BTC/USDT para demonstrar Decimal, dataclasses, Enum, tipagem, funções puras, validações, exceções, datas UTC e testes.

Implemente código e documentação; não entregue apenas um plano. Esta é uma aplicação didática local, sem dinheiro real e sem recomendação de investimento.

DIRETÓRIO E INDEPENDÊNCIA

Crie um diretório próprio chamado pyspot dentro do diretório de trabalho indicado pelo usuário ou, na ausência de indicação, dentro do diretório atual. Se ele já existir, inspecione seu conteúdo e preserve trabalho existente. Não altere o SpotLab, o robô principal ou projetos vizinhos. O exemplo deve funcionar sem arquivos, dependências ou importações da Sprint 01.

TECNOLOGIA E LIMITES

1. Python 3.11 ou superior; somente biblioteca padrão, inclusive unittest e argparse.
2. Sem acesso à rede na execução, API de exchange, SDK, credenciais ou envio de ordens.
3. Não implemente livro de ofertas, casamento de ordens, reservas, estratégias, backtest, banco de dados, interface web, Docker, AWS ou processamento assíncrono nesta sprint.
4. A aplicação registra execuções fictícias já confirmadas e aplica seus efeitos em uma carteira local. Uma solicitação de ordem não deve ser confundida com uma execução confirmada.
5. Textos de terminal e documentação em português. Identificadores de código devem seguir uma convenção consistente.

ORGANIZAÇÃO SUGERIDA

Use pyproject.toml, um pacote pyspot na raiz do projeto, tests e docs. Separe modelos, conversão/validação, cálculos, aplicação na carteira e apresentação apenas quando houver responsabilidade clara. Não crie camadas, interfaces ou padrões sem necessidade didática.

Parte financeira deve retornar valores estruturados; print e formatação pertencem à interface. Não use variáveis globais mutáveis para saldo, taxa ou histórico. Cada cenário deve começar com seu próprio estado.

REPRESENTAÇÃO DOS VALORES

- Use Decimal para preços, quantidades, taxas e saldos. Não use float no fluxo financeiro válido.
- A entrada textual deve usar ponto como separador decimal, sem separador de milhares. Documente essa convenção, mesmo que a explicação em português use vírgula.
- Crie uma função de conversão de string para Decimal que rejeite tipo diferente de string, texto vazio, texto malformado, NaN, sNaN e infinitos. Não faça uma conversão intermediária para float.
- Valide novamente os objetos de domínio: anotações de tipo não impedem a construção com valores inválidos.
- Preço e quantidade devem ser finitos e maiores que zero; saldos, finitos e não negativos; taxa, finita e no intervalo 0 <= taxa < 1.
- Adote contexto decimal local com precisão 28 e ROUND_HALF_EVEN. Não altere permanentemente o contexto decimal global do processo.
- Não quantize valores a cada operação. Arredonde somente a apresentação. Explique que Decimal também tem precisão finita e divisões podem exigir arredondamento.
- Exiba dinheiro com precisão suficiente para conferir todos os valores dos cenários. Mostre retorno percentual com seis casas decimais. Explique que estas são regras do laboratório, não regras de precisão de uma exchange.
- Inclua uma demonstração isolada comparando 0.1 + 0.2 com Decimal("0.1") + Decimal("0.2"). O uso de float deve ficar restrito a essa demonstração do problema.

MODELOS E CONTRATOS

Use Enum para o lado COMPRA/VENDA e dataclass(frozen=True) para os registros apropriados. Represente pelo menos:

- Par: ativo base BTC e ativo de cotação USDT.
- Execução confirmada: identificador não vazio, par, lado, preço, quantidade, taxa em USDT e horário.
- Carteira: saldo de BTC e saldo de USDT.
- Resultado da operação completa: valores brutos, taxas, desembolso, recebimento líquido, lucro líquido e retorno percentual.

Documente que frozen=True impede a reatribuição normal dos campos, mas não cria imutabilidade profunda de objetos mutáveis contidos nos campos.

Para aplicar uma execução, prefira uma função que recebe uma carteira válida e retorna uma nova carteira, preservando a anterior. Não precisa haver histórico persistente ou controle de duplicidade nesta sprint; declare que cada execução fictícia é aplicada uma única vez pelo cenário.

REGRAS DE CÁLCULO

Taxa fictícia padrão: Decimal("0.001"), equivalente a 0,10%, cobrada em USDT em compras e vendas. Não implemente taxa em BTC ou BNB nem distinção maker/taker.

- Valor bruto = preço * quantidade.
- Taxa em USDT = valor bruto * alíquota.
- Compra: diminui USDT em valor bruto + taxa; aumenta BTC na quantidade executada.
- Venda: diminui BTC na quantidade executada; aumenta USDT em valor bruto - taxa.
- Lucro líquido de uma operação completa = recebimento líquido da venda - desembolso da compra.
- Retorno líquido (%) = lucro líquido / desembolso da compra * 100.

O cálculo de resultado deve aceitar uma compra e uma venda do mesmo par e da mesma quantidade, com venda em horário igual ou posterior ao da compra. Rejeite pares, quantidades, lados ou cronologia incompatíveis. Não implemente lucro de posições parcialmente encerradas.

Os preços fornecidos já são preços de execução. Não desconte spread ou slippage novamente.

ERROS E PRESERVAÇÃO DO ESTADO

Crie exceções claras, como DadosInvalidosError e SaldoInsuficienteError, e explique quando cada uma ocorre. Verifique as condições antes de produzir a nova carteira.

Rejeite compra quando USDT não cobre valor bruto mais taxa e venda quando falta BTC. Em ambos os casos, a carteira original deve permanecer intacta. Não permita saldo negativo nem altere silenciosamente a quantidade solicitada.

Capture apenas erros esperados nas fronteiras da aplicação; não esconda falhas com except Exception, retorno zero ou mensagem de sucesso. Cenários didáticos de erro esperado devem explicar o erro e continuar normalmente. Um cenário que deveria passar e falha deve resultar em código de saída diferente de zero.

HORÁRIOS UTC

- Use datetime com informação de fuso. Rejeite datetime ingênuo, sem timezone.
- Se a entrada tiver outro deslocamento, normalize para UTC preservando o instante.
- Use horários fixos nos cenários, sem datetime.now() nos resultados determinísticos.
- Formate horários em ISO 8601 com +00:00 ou Z.
- Demonstre que 2026-11-05T09:00:00-03:00 equivale a 2026-11-05T12:00:00+00:00.
- Inclua uma função pequena que verifica se um evento pertence a [início, fim). Valide início < fim e datas com fuso. Evento exatamente no início pertence ao intervalo; exatamente no fim fica fora. Não implemente agregação de candles nesta etapa.

CENÁRIOS OBRIGATÓRIOS

A. Precisão decimal
   Compare float e Decimal em 0.1 + 0.2; explique a diferença. Demonstre que o laboratório usa Decimal a partir de strings e preserva o contexto decimal externo.

B. Compra e venda completas
   Saldo inicial: 1.000 USDT e 0 BTC.
   Compra: 0,001 BTC a 100.000 USDT, em 2026-11-05T12:00:00+00:00.
   Venda: 0,001 BTC a 101.000 USDT, em 2026-11-05T12:05:00+00:00.
   Taxa: 0,10% em cada ponta, paga em USDT.
   Resultados exatos esperados:
   - Compra bruta: 100 USDT; taxa de compra: 0,1 USDT; desembolso: 100,1 USDT.
   - Carteira após compra: 899,9 USDT e 0,001 BTC.
   - Venda bruta: 101 USDT; taxa de venda: 0,101 USDT; recebimento líquido: 100,899 USDT.
   - Taxas totais: 0,201 USDT; lucro bruto: 1 USDT; lucro líquido: 0,799 USDT.
   - Carteira final: 1.000,799 USDT e 0 BTC.
   - Retorno líquido exibido: 0,798202%, calculado sobre 100,1 USDT.
   Explique cada etapa e mostre carteiras anterior e posterior, sem misturar dados e apresentação.

C. Entradas inválidas
   Demonstre rejeição de preço negativo, quantidade zero, NaN, infinito, alíquota negativa, alíquota igual a 1 e tentativa de passar float para a conversão financeira. Demonstre também entrada textual vazia ou malformada. Exiba erros compreensíveis.

D. Saldo insuficiente
   Com 100 USDT e 0 BTC, tente comprar 0,001 BTC a 100.000 USDT: falta saldo para a taxa de 0,1 USDT.
   Com 0 BTC, tente vender 0,001 BTC.
   Em ambos os casos, mostre que os saldos originais permaneceram iguais.

E. UTC e limites de intervalo
   Demonstre a equivalência dos dois horários com deslocamentos distintos e a rejeição de data sem fuso.
   Para [12:00:00, 12:01:00) UTC, demonstre inclusão do início e exclusão do fim.

COMANDOS E DOCUMENTAÇÃO

Implemente:
- python -m pyspot: executa todos os cenários, sempre na mesma ordem.
- python -m pyspot --cenario a: executa um cenário; aceite a, b, c, d e e.
- python -m pyspot --help: explica os comandos.
- python -m unittest discover -s tests -v: executa os testes.

Os comandos devem funcionar a partir da raiz do projeto, sem instalação de dependências. Documente python3 como alternativa quando python não apontar para a versão correta.

Entregue:
- pyproject.toml com nome, descrição e versão mínima de Python.
- Pacote pyspot e testes.
- README.md com objetivo, estrutura, requisitos, execução, exemplo de saída, fórmulas e limites.
- docs/sprint02-glossario.md com Decimal, precisão, arredondamento, dataclass, Enum, tipagem, função pura, imutabilidade, exceção, UTC e teste automatizado. Use comparações pontuais com BigDecimal e objetos de dados em Java; explique que os comportamentos não são idênticos.
- docs/sprint02-validacao.md com passo a passo, valores esperados, comandos efetivamente executados, resultados observados e pendências reais.

TESTES E CRITÉRIOS DE ACEITE

Verifique resultados observáveis, incluindo:
1. Valores exatos de compra, venda, taxas, carteiras e lucro do cenário B com Decimal.
2. Formatação do retorno 0,798202%, separada do cálculo interno.
3. Compra e venda com saldo exatamente suficiente, incluindo taxa de compra.
4. Rejeição de saldo insuficiente com preservação da carteira original.
5. Entradas inválidas dos cenários, incluindo construção direta dos modelos com valores incorretos.
6. Taxa zero aceita; taxa fora do intervalo rejeitada.
7. Normalização de fuso preservando o instante; data ingênua rejeitada; limites [início, fim).
8. Pares/quantidades/lados incompatíveis e venda anterior à compra rejeitados no cálculo do resultado completo.
9. Contexto decimal externo preservado após os cálculos e resultados reproduzíveis quando o chamador usa outra precisão.

Execute todos os cenários juntos, cada cenário individualmente, --help e a suíte unittest. Corrija os problemas encontrados. Não declare verificações que não executou.

Ao concluir, apresente arquivos criados, comandos executados, resultados e limitações. Não faça commits nem publique o projeto sem solicitação. Se algum comando não puder ser executado, registre o motivo e a pendência exata.
````

## 4. Conclusão da etapa

A etapa estará concluída quando for possível explicar e verificar como os valores são representados, validados e calculados, como o estado é preservado em rejeições e como os horários são normalizados para UTC.

A próxima etapa será coleta e armazenamento de dados. Integrações externas e persistência ficam fora deste exemplo.
