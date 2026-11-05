# Glossário — Sprint 02

| Conceito | Significado e aplicação |
| --- | --- |
| `Decimal` | Número decimal construído a partir de texto, como `Decimal("0.1")`. Evita a aproximação binária desse valor em `float`. Lembra `BigDecimal` em Java, mas operadores, contexto, igualdade e regras de escala não são idênticos. Em Python, `Decimal("1.0") == Decimal("1.00")`; em Java, `BigDecimal.equals` considera a escala, enquanto `compareTo` compara o valor numérico. |
| Precisão | Quantidade de dígitos significativos disponíveis nas operações. O contexto local usa 28; isso não significa 28 casas depois do ponto. Como em cálculos com `BigDecimal` e `MathContext`, divisões podem exigir arredondamento. Não há precisão infinita. |
| Arredondamento | Regra usada quando o resultado não cabe na precisão ou apresentação. `ROUND_HALF_EVEN` escolhe o último dígito par no empate. O cálculo não quantiza a cada etapa; o percentual é formatado com seis casas somente ao exibir. |
| `dataclass` | Gera métodos como inicialização, representação e igualdade a partir de campos. Facilita objetos de dados; tem alguma semelhança com records ou classes de dados em Java, mas não possui o mesmo contrato. `__post_init__` valida após a inicialização gerada. |
| `Enum` | Conjunto explícito de valores nomeados. `Lado.COMPRA` e `Lado.VENDA` evitam strings soltas no domínio. Como enums Java, dão nomes aos estados, mas os mecanismos da linguagem diferem. |
| Tipagem | Anotações como `preco: Decimal` documentam contratos e ajudam ferramentas. Diferentemente das verificações estáticas usuais do compilador Java, Python não impede automaticamente passar uma string nesse argumento. As validações de execução continuam necessárias. |
| Função pura | Retorna resultados a partir dos argumentos, sem alterar estado externo nem imprimir. `calcular_resultado` retorna um registro; `aplicar_execucao` retorna nova carteira. A apresentação usa esses dados separadamente. |
| Imutabilidade | Estado que não muda após a criação. `frozen=True` bloqueia reatribuição normal, mas não oferece imutabilidade profunda: uma lista contida no objeto ainda poderia mudar. `final` em Java também não torna o objeto referenciado profundamente imutável. Os modelos usam valores imutáveis, não listas. |
| Exceção | Sinalização de que o contrato não pode ser cumprido. `DadosInvalidosError` rejeita dados incompatíveis e `SaldoInsuficienteError` rejeita aplicação sem saldo. Capturam-se apenas erros esperados na fronteira; falhas inesperadas propagam. |
| UTC | Referência de horário sem deslocamento local. Um `datetime` com fuso identifica o instante; a normalização preserva esse instante. A comparação com `OffsetDateTime`/`Instant` em Java ajuda, mas as APIs não são iguais. `datetime` ingênuo é recusado. |
| Intervalo `[início, fim)` | Convenção semiaberta: o início pertence, o fim não. Evita contar duas vezes uma fronteira compartilhada por intervalos adjacentes; não implementa candles neste laboratório. |
| Teste automatizado | Verificação executável de comportamento esperado, usando `unittest` da biblioteca padrão. Asserções verificam valores exatos, erros, preservação de estado, fusos e saída do terminal; não dependem de rede nem do relógio atual. |
| Execução confirmada | Registro de uma compra ou venda fictícia que já ocorreu. Não representa uma solicitação pendente e não é enviada a uma exchange. |
| Taxa e alíquota | Alíquota é a fração `0.001`; taxa em USDT é o valor monetário `bruto * alíquota`. Na compra, soma-se ao custo; na venda, subtrai-se do recebimento. |

Os exemplos com Java são pontos de comparação para leitura, não equivalências
completas entre as linguagens. Veja os contratos concretos em
[README.md](../README.md) e os resultados em [sprint02-validacao.md](sprint02-validacao.md).
