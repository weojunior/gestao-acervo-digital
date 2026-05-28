# Relatório de testes

Documento que descreve a estratégia de testes adotada no sistema de gestão de acervo digital, o conjunto de casos verificados, o resultado da execução, as limitações reconhecidas e o procedimento de reprodução.

## 1. Objetivo

Verificar o comportamento das funções do núcleo do pacote `biblioteca` em casos felizes e em cenários de erro, gerando evidência reproduzível de que o código atende aos requisitos da atividade. O relatório também documenta os testes manuais conduzidos durante o desenvolvimento da interface de linha de comando, que não estão automatizados.

## 2. Ambiente

| Item | Versão ou caminho |
| --- | --- |
| Sistema operacional | macOS (Darwin 25.5.0) |
| Python | 3.14.3, instalação Python.org framework |
| Pytest | 9.0.3 |
| Plugins ativos | pluggy 1.6.0, anyio 4.13.0 |
| Comando padrão | `python3 -m pytest` |
| Diretório raiz | raiz do repositório |

## 3. Metodologia

A suíte adota pytest como framework e segue o padrão Arrange-Act-Assert em cada caso de teste. Os arquivos de teste ficam em `tests/` e usam nomes no formato `test_<funcao>_<comportamento_esperado>`, o que permite a um leitor identificar o que está sendo verificado apenas pelo identificador do teste.

O isolamento entre testes é feito pela fixture `tmp_path` do pytest, que cria um diretório temporário único por execução. Cada teste opera sobre seu próprio diretório, sem dependência de estado deixado por execuções anteriores e sem efeitos sobre o disco do usuário.

A cobertura segue duas regras por função pública. Há um teste para o caminho feliz e um teste para cada exceção customizada que a função pode levantar. Funções que aceitam parâmetros equivalentes (como `validar_extensao` percorrendo a lista de formatos aceitos) usam `pytest.mark.parametrize` para reduzir repetição. Funções privadas são exercitadas indiretamente pelas funções públicas que as consomem.

A configuração de `PYTHONPATH` é centralizada em `tests/conftest.py`, arquivo descoberto automaticamente pelo pytest antes da coleta dos arquivos de teste. Ele insere `src/` em `sys.path`, replicando em ambiente de testes a mesma manipulação feita por `run.py` em ambiente de execução.

## 4. Inventário dos testes

A suíte é composta por 78 testes distribuídos em cinco arquivos.

| Arquivo | Quantidade | Aspectos verificados |
| --- | --- | --- |
| `tests/test_arquivos.py` | 24 | Validação de extensão (parametrizada por formato aceito e por caixa alta), criação de arquivo vazio e com conteúdo, preservação de caracteres acentuados em UTF-8, rejeição de extensão fora da lista, rejeição de duplicata, leitura textual e tratamento de caminho inexistente ou diretório, renomeação preservando o diretório de origem, recusa de extensão inválida no destino, remoção e suas falhas. |
| `tests/test_diretorios.py` | 14 | Criação de diretório com e sem criação de pais, falha quando o caminho já existe, listagem em modo simples e recursivo, ordenação alfabética dos itens, remoção de pasta vazia, recusa de remoção em pasta com conteúdo, remoção em cascata com `recursivo=True`, e falhas correspondentes. |
| `tests/test_catalogo.py` | 27 | Ciclo de I/O do JSON (leitura, escrita, arquivo inexistente, JSON corrompido), preservação de acentos, validação de metadados (título e autor não vazios, ano inteiro, rejeição de booleano, rejeição de ano anterior a 1450), duplicata, derivação automática do campo `tipo` a partir da extensão, CRUD completo (`adicionar`, `remover`, `buscar`, `listar`), e renomeação preservando metadados e recalculando o tipo quando a extensão muda. |
| `tests/test_listagens.py` | 6 | Agrupamento por tipo e por ano, ordenação determinística das chaves (alfabética para tipo e crescente para ano), retorno de dicionário vazio para catálogo vazio. |
| `tests/test_auditoria.py` | 7 | Classificação correta de documentos íntegros, registros sem arquivo no disco e arquivos no disco sem registro, combinação simultânea das três categorias, filtragem de arquivos com extensão fora da lista (`catalogo.json`, `.DS_Store`, `.zip`) e falha quando o diretório do acervo não existe. |

Os 24 testes de `test_arquivos.py` incluem seis variações parametrizadas da validação de extensão, uma para cada formato listado em `EXTENSOES_SUPORTADAS`. Sem o parâmetro, seriam 19 testes diretos.

## 5. Resultado da execução

A execução em 28 de maio de 2026 com o comando `python3 -m pytest -v` reportou:

```
collected 78 items
...
============================== 78 passed in 0.05s ==============================
```

Todos os 78 testes resultaram em `PASSED`. Não houve falhas, erros nem testes ignorados (`skipped`).

O tempo total de execução foi de 0,05 segundo, o que torna a suíte adequada para uso em ciclos de desenvolvimento iterativos e para inclusão em pipelines de integração contínua.

## 6. Reprodução

A partir da raiz do repositório:

```bash
pip3 install -r requirements.txt
python3 -m pytest -v
```

Para o resumo compacto, sem listagem dos testes individuais:

```bash
python3 -m pytest --tb=no -q
```

Para executar apenas um arquivo de teste específico:

```bash
python3 -m pytest tests/test_catalogo.py -v
```

Para executar apenas um teste pelo nome:

```bash
python3 -m pytest -v -k test_adicionar_documento_recusa_duplicata
```

A flag `-k` aceita expressões com `and`, `or`, `not` para filtragem mais fina.

## 7. Limitações reconhecidas

A suíte automatizada não cobre os módulos `cli.py`, `__main__.py` e `run.py`. O motivo é que esses módulos consomem entrada interativa via `input()` e produzem saída via `print()`, o que demanda um padrão de teste com captura de `stdin` e `stdout` (uso de `capsys` e `monkeypatch.setattr`) que está fora do escopo desta entrega. As funções consumidas pela CLI (de `arquivos`, `diretorios`, `catalogo`, `listagens` e `auditoria`) são as mesmas testadas pela suíte automatizada, o que oferece garantia indireta sobre o comportamento da CLI quanto à lógica de negócio.

Os testes não exercitam cenários de concorrência (escrita simultânea no catálogo por dois processos) nem volumes grandes (acervo com dezenas de milhares de documentos). Esses cenários não fazem parte do caso de uso definido pela atividade, que prevê operação por um bibliotecário por vez sobre acervos de tamanho moderado.

Os testes não verificam codificações de texto além de UTF-8. O sistema assume UTF-8 em toda a leitura e escrita de texto, o que é consistente com macOS e Linux modernos e com o ambiente da atividade.

## 8. Testes manuais complementares

Durante o desenvolvimento da Fase 4, a interface de linha de comando foi exercitada manualmente nos nove subcomandos disponíveis. Os procedimentos abaixo foram registrados como validação ad hoc; a execução automática equivalente fica como trabalho futuro.

| Subcomando | Procedimento | Resultado observado |
| --- | --- | --- |
| `adicionar` | Cadastro interativo de um arquivo `.txt` previamente criado em `/tmp`, com respostas válidas. | Arquivo copiado para `acervo/`, registro criado no catálogo, resumo exibido. |
| `importar` | Importação em lote de três documentos via arquivo CSV com cabeçalho. | Três registros criados, mensagem `Importação concluída: 3 sucesso(s), 0 falha(s)`. |
| `listar` | Execução sem argumentos. | Listagem linear dos registros existentes. |
| `listar-tipo` | Execução sem argumentos com três documentos `.txt` no catálogo. | Seção única `TXT (3 documentos)` com os três registros. |
| `listar-ano` | Execução sem argumentos com registros de 2024 e 2025. | Duas seções, `2024 (2 documentos)` e `2025 (1 documento)`, em ordem crescente. |
| `buscar` | Consulta por `nome_arquivo` existente. | Registro completo exibido. |
| `renomear` | Renomeação de `documento_teste.txt` para `documento_teste_renomeado.txt`. | Arquivo físico e registro renomeados em conjunto. |
| `remover` | Remoção com resposta `s` no prompt de confirmação. | Arquivo físico e registro removidos. |
| `auditar` | Execução após remoção manual de um arquivo físico do acervo, sem usar o subcomando `remover`. | Saída identificou corretamente um registro sem arquivo na categoria "Cadastros sem arquivo no disco". |

Os testes manuais validaram também o tratamento de caminho inválido no prompt do `importar`, em que o usuário digitou `/temp/cadastros.csv` (typo de `/tmp/`). O programa exibiu a mensagem "Arquivo '/temp/cadastros.csv' não encontrado." e repetiu o prompt sem encerrar a execução, comportamento alinhado ao desenho da função `_perguntar_caminho_existente`.

## 9. Conclusão

A suíte automatizada cobre 100% das funções públicas do núcleo do pacote `biblioteca`, com 78 testes verdes em ambiente isolado e tempo total de execução abaixo de um décimo de segundo. As funções de manipulação de arquivos, gerenciamento de diretórios, persistência de catálogo, listagens analíticas e auditoria de consistência foram verificadas em casos felizes e em cada caminho de exceção esperado. Os testes manuais cobrem a interface de linha de comando nos nove subcomandos disponíveis, complementando a cobertura automatizada.
