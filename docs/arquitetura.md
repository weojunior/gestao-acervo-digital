# Arquitetura do sistema

Documento que descreve a organização do código, as decisões de design tomadas durante o desenvolvimento e os limites de responsabilidade entre os módulos do pacote `biblioteca`.

## 1. Camadas

O sistema é dividido em quatro camadas funcionais, cada uma materializada em um conjunto de módulos sem dependência reversa entre elas.

| Camada | Módulos | Responsabilidade |
| --- | --- | --- |
| I/O do sistema de arquivos | `arquivos`, `diretorios` | Operações primitivas sobre arquivos e pastas, em cima de `pathlib`. Nenhum conhecimento sobre catálogo, metadados ou formato de dados. |
| Dados | `catalogo` | Persistência, leitura e validação dos metadados em JSON. Conhece o esquema do registro mas não conhece a CLI. |
| Análise | `listagens`, `auditoria` | Consultas analíticas sobre o catálogo e cruzamentos com o estado do disco. Consomem `catalogo` e `arquivos`, não persistem nada. |
| Interface | `cli` | Coleta entrada do usuário, despacha para os módulos das camadas inferiores, formata a saída. Conhece todas as camadas abaixo. |

Em transversal a todas as camadas há o módulo `excecoes`, que define a hierarquia de erros do domínio. Todas as exceções levantadas pelo pacote descendem de `BibliotecaError`, o que permite à CLI capturar a raiz da hierarquia em um único `try/except`.

## 2. Mapa de dependências

A regra de acoplamento é simples: módulos só podem importar de camadas iguais ou inferiores. Inversões violariam a separação de responsabilidades.

```
cli                  (interface)
  ├─→ arquivos       (i/o)
  ├─→ diretorios     (i/o)
  ├─→ catalogo       (dados)
  ├─→ listagens      (análise)
  ├─→ auditoria      (análise)
  └─→ excecoes       (transversal)

listagens, auditoria (análise)
  └─→ catalogo, arquivos, diretorios

catalogo             (dados)
  └─→ arquivos       (para reuso de validar_extensao)

arquivos, diretorios (i/o)
  └─→ excecoes       (apenas)
```

A dependência de `catalogo` em `arquivos` para a função `validar_extensao` é intencional. Centraliza a definição de formatos aceitos em um único módulo (`arquivos.EXTENSOES_SUPORTADAS`) e evita duplicação de regras de domínio.

## 3. Decisões arquiteturais

### 3.1. Pacote `biblioteca` dentro de `src/`

A árvore de diretórios segue o padrão `src-layout`. O pacote nomeado fica em `src/biblioteca/`, não diretamente em `src/`. A pasta `src/` é apenas pasta-pai e não é, em si, um pacote Python. Esta convenção é difundida pela comunidade Python (PyPA) e evita problemas com imports implícitos da raiz do projeto.

### 3.2. Catálogo como fonte da verdade dos metadados

Os metadados ficam em `acervo/catalogo.json` em vez de embutidos no nome do arquivo ou nos próprios PDFs/ePUBs. Justificativas:

- Robustez: o catálogo continua válido mesmo que o usuário renomeie arquivos por engano fora do sistema. A auditoria detecta a divergência.
- Riqueza: permite armazenar título, autor, ano e tipo simultaneamente, ao contrário de convenções de nome que limitam a um ou dois campos.
- Independência de formato: não depende de bibliotecas para ler metadados embutidos em PDF (que nem sempre estão presentes) ou ePUB.

### 3.3. JSON em vez de SQLite

O catálogo é um arquivo JSON simples, não um banco de dados relacional. Motivos:

- Tamanho do problema. O caso de uso da atividade prevê acervos de dezenas a centenas de documentos, não milhares. JSON cabe em memória sem custo perceptível.
- Stdlib. O módulo `json` é parte da biblioteca padrão, sem dependência externa.
- Auditável. O arquivo pode ser inspecionado e editado manualmente em qualquer editor de texto. Útil em emergências.

A escolha tem custo. Operações concorrentes podem corromper o arquivo, motivo pelo qual o sistema é declaradamente single-user.

### 3.4. Exceções customizadas em hierarquia

Cada situação de erro do domínio tem sua própria classe de exceção, todas descendentes de `BibliotecaError`. A vantagem aparece em dois pontos:

- A CLI captura `BibliotecaError` uma única vez no `main` e mostra mensagem clara. Não precisa conhecer cada subclasse.
- Código que precisa tratar especificamente uma situação (por exemplo, sugerir nome alternativo em `DocumentoJaExiste`) pode capturar a subclasse antes do `except` genérico.

A alternativa seria retornar `False` ou `None` em caso de erro. Foi rejeitada por mascarar a causa do erro e por contrariar a convenção idiomática do Python.

### 3.5. Funções puras no núcleo

Os módulos das camadas de I/O, dados e análise não fazem `input()` nem `print()`. Recebem parâmetros, retornam valores, levantam exceções. Toda interação com o usuário é responsabilidade da CLI.

Essa separação tem duas consequências importantes:

- Testabilidade. As funções podem ser exercitadas pela suíte de testes sem precisar simular entrada de teclado.
- Reuso. A mesma lógica é consumida pela CLI interativa, pelo importador CSV e (potencialmente) por uma futura interface web.

### 3.6. Dois modos de cadastro

A CLI oferece cadastro interativo (`adicionar`) e em lote (`importar`). Cada modo serve a um perfil de uso. O interativo é melhor para o cadastro pontual de um documento que acaba de chegar à biblioteca. O em lote é melhor para a carga inicial do acervo ou para migração a partir de uma planilha exportada de outro sistema.

A decisão de não oferecer cadastro via argumentos diretos de linha de comando (`adicionar --titulo X --autor Y ...`) foi tomada considerando o perfil do usuário fim. Bibliotecários tendem a ser mais à vontade com prompts do que com sintaxe de flags.

### 3.7. CSV como formato de importação

O modo em lote consome arquivos CSV em vez de TXT estruturado ou JSON. Motivos:

- Excel, LibreOffice Calc e Google Sheets exportam CSV em um clique. O bibliotecário pode preparar a lista de documentos em planilha sem precisar aprender outro formato.
- A stdlib do Python tem o módulo `csv`, sem dependência externa.
- O CSV tem cabeçalho explícito, o que reduz erros de ordem de campos comparado a TXT delimitado sem cabeçalho.

## 4. Fluxo de dados

### 4.1. Cadastro interativo

```
usuário → CLI._comando_adicionar
              ↓
       _perguntar_caminho_existente   (i/o local com input())
       _perguntar_texto x N           (i/o local com input())
       _perguntar_inteiro             (i/o local com input())
              ↓
       arquivos.validar_extensao      (camada i/o)
              ↓
       shutil.copy2                   (cópia para acervo/)
              ↓
       catalogo.adicionar_documento   (camada dados)
              ↓
       CLI._imprimir_registro         (formatação)
              ↓
       saída no terminal
```

Em caso de falha após a cópia mas antes da inserção no catálogo, a CLI desfaz a cópia (`caminho_destino.unlink()`) e propaga a exceção. Mantém consistência entre disco e catálogo.

### 4.2. Auditoria

```
usuário → CLI._comando_auditar
              ↓
       auditoria.auditar_acervo
              ↓
       diretorios.listar_diretorio   (varredura do acervo)
              ↓
       catalogo.listar_documentos    (leitura do JSON)
              ↓
       comparação por conjuntos      (set difference)
              ↓
       CLI._imprimir_secao_auditoria (formatação por categoria)
              ↓
       saída no terminal em três seções
```

A varredura do disco filtra por `EXTENSOES_SUPORTADAS`, o que automaticamente exclui `catalogo.json`, `.DS_Store` e outros arquivos auxiliares.

## 5. Convenções de código

O código segue PEP 8, PEP 257 e PEP 484.

| Aspecto | Convenção |
| --- | --- |
| Nomes de função e variável | `snake_case` |
| Nomes de classe | `PascalCase` |
| Nomes de constante | `UPPER_SNAKE_CASE` |
| Largura de linha | até 88 caracteres |
| Imports | três blocos: stdlib, terceiros, locais |
| Docstrings | obrigatórias em toda função pública, estilo Google |
| Type hints | obrigatórios em assinaturas públicas, sintaxe `str | Path` (PEP 604) |
| Funções privadas | prefixo de underscore (`_validar_metadados`) |
| Constantes | extraídas para o topo do módulo, evitando strings e números mágicos |

## 6. Pontos de extensão

Adicionar formato de arquivo:

1. Acrescentar a extensão a `EXTENSOES_SUPORTADAS` em `src/biblioteca/arquivos.py`.
2. Acrescentar o rótulo correspondente a `TIPO_POR_EXTENSAO` em `src/biblioteca/catalogo.py`.
3. Os testes parametrizados absorvem a nova extensão automaticamente.

Adicionar comando à CLI:

1. Implementar `_comando_<nome>` em `src/biblioteca/cli.py`.
2. Registrar via `_registrar(sub, ...)` em `_construir_parser`.
3. Adicionar entrada correspondente à tabela de subcomandos no `README.md`.

Adicionar campo ao registro do catálogo:

1. Atualizar `adicionar_documento` em `catalogo.py` para aceitar e armazenar o campo.
2. Atualizar `_validar_metadados` se houver regra de domínio aplicável.
3. Considerar incrementar `VERSAO_SCHEMA` para sinalizar a mudança de formato.
4. Atualizar `_imprimir_registro` na CLI para incluir o campo na saída.

## 7. Limitações declaradas

- O sistema é single-user. Escrita concorrente no `catalogo.json` por dois processos simultâneos pode corromper o arquivo.
- Não há transações nem rollback global. O rollback é local a cada comando da CLI.
- Codificação assumida é UTF-8 em todas as operações de texto.
- Tamanho prático máximo do acervo: limitado pela memória disponível para carregar o JSON inteiro. Para acervos com dezenas de milhares de documentos, seria necessário migrar para SQLite.
