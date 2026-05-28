# Referência de API

Catálogo das funções públicas dos módulos do pacote `biblioteca`, com assinatura, parâmetros, retornos, exceções e exemplos. Organizado por módulo, na mesma ordem das camadas descritas em [`arquitetura.md`](arquitetura.md).

## 1. Módulo `biblioteca.arquivos`

Operações de manipulação de arquivos individuais.

### 1.1. Constantes

- `EXTENSOES_SUPORTADAS: tuple[str, ...]` lista de extensões aceitas pelo acervo. Valor atual: `(".pdf", ".epub", ".txt", ".md", ".docx", ".doc", ".odt", ".ods")`.
- `CODIFICACAO_PADRAO: str` codificação usada na leitura e escrita de texto. Valor: `"utf-8"`.

### 1.2. `validar_extensao`

```python
def validar_extensao(caminho: str | Path) -> None
```

Verifica que a extensão do arquivo está em `EXTENSOES_SUPORTADAS`. Comparação insensível à caixa.

- Args: `caminho` qualquer string ou Path com extensão a verificar.
- Raises: `FormatoNaoSuportado` quando a extensão não consta na lista.

### 1.3. `criar_arquivo`

```python
def criar_arquivo(caminho: str | Path, conteudo: str = "") -> Path
```

Cria arquivo de texto no caminho indicado. Não cria diretórios intermediários.

- Args: `caminho` destino do arquivo; `conteudo` texto inicial (vazio por padrão).
- Returns: `Path` do arquivo criado.
- Raises: `FormatoNaoSuportado` extensão inválida; `DocumentoJaExiste` caminho ocupado.

### 1.4. `ler_arquivo`

```python
def ler_arquivo(caminho: str | Path) -> str
```

Lê e retorna o conteúdo textual em UTF-8. Cobre simultaneamente "abrir" e "ler".

- Args: `caminho` arquivo a ler.
- Returns: conteúdo decodificado como `str`.
- Raises: `DocumentoNaoEncontrado` arquivo inexistente ou caminho aponta para diretório.

### 1.5. `renomear_arquivo`

```python
def renomear_arquivo(caminho_atual: str | Path, novo_nome: str) -> Path
```

Renomeia preservando o diretório de origem. O `novo_nome` é apenas o nome do arquivo, sem caminho.

- Args: `caminho_atual` arquivo a renomear; `novo_nome` novo nome com extensão.
- Returns: `Path` do arquivo após renomeação.
- Raises: `DocumentoNaoEncontrado` origem inexistente; `DocumentoJaExiste` destino ocupado; `FormatoNaoSuportado` extensão do novo nome inválida.

### 1.6. `remover_arquivo`

```python
def remover_arquivo(caminho: str | Path) -> None
```

Remove permanentemente o arquivo.

- Args: `caminho` arquivo a remover.
- Raises: `DocumentoNaoEncontrado` arquivo inexistente ou caminho aponta para diretório.

## 2. Módulo `biblioteca.diretorios`

Operações de gerenciamento de diretórios.

### 2.1. `criar_diretorio`

```python
def criar_diretorio(caminho: str | Path, criar_pais: bool = False) -> Path
```

Cria diretório no caminho indicado.

- Args: `caminho` destino; `criar_pais` se `True`, cria toda a hierarquia ascendente.
- Returns: `Path` do diretório criado.
- Raises: `DiretorioJaExiste` caminho já ocupado; `DiretorioNaoEncontrado` quando `criar_pais=False` e o pai não existe.

### 2.2. `listar_diretorio`

```python
def listar_diretorio(caminho: str | Path, recursivo: bool = False) -> list[Path]
```

Lista o conteúdo do diretório em ordem alfabética.

- Args: `caminho` diretório a listar; `recursivo` inclui conteúdo de subpastas se `True`.
- Returns: `list[Path]` ordenada alfabeticamente.
- Raises: `DiretorioNaoEncontrado` caminho inexistente ou aponta para arquivo.

### 2.3. `remover_diretorio`

```python
def remover_diretorio(caminho: str | Path, recursivo: bool = False) -> None
```

Remove diretório. Por padrão exige que esteja vazio.

- Args: `caminho` diretório a remover; `recursivo` permite remoção em cascata.
- Raises: `DiretorioNaoEncontrado` caminho inexistente; `DiretorioNaoVazio` diretório contém itens e `recursivo=False`.

## 3. Módulo `biblioteca.catalogo`

Persistência e gestão dos metadados em JSON.

### 3.1. Constantes

- `VERSAO_SCHEMA: str` versão do esquema persistido. Valor atual: `"1.0"`.
- `ANO_MINIMO_ACEITO: int` ano mínimo aceito como ano de publicação. Valor: `1450`.
- `TIPO_POR_EXTENSAO: dict[str, str]` mapeamento extensão para rótulo. Atualmente cobre `.pdf` para `PDF`, `.epub` para `EPUB`, `.txt` para `TXT`, `.md` para `MD`, `.docx` para `DOCX`, `.doc` para `DOC`, `.odt` para `ODT`, `.ods` para `ODS`.

### 3.2. Esquema do registro

Cada documento no catálogo é um dicionário com cinco chaves.

| Campo | Tipo | Restrições |
| --- | --- | --- |
| `nome_arquivo` | str | Único no catálogo. Chave primária. |
| `titulo` | str | Não vazio após `strip`. |
| `autor` | str | Não vazio após `strip`. |
| `ano` | int | Entre `ANO_MINIMO_ACEITO` e o ano corrente mais um. `bool` é rejeitado. |
| `tipo` | str | Derivado da extensão pelo mapeamento `TIPO_POR_EXTENSAO`. |

### 3.3. Esquema do catálogo persistido

```json
{
  "versao": "1.0",
  "documentos": [
    { ... registro 1 ... },
    { ... registro 2 ... }
  ]
}
```

### 3.4. `carregar_catalogo`

```python
def carregar_catalogo(caminho: str | Path) -> dict
```

Lê o JSON do disco. Devolve estrutura vazia inicializada quando o arquivo não existe.

- Returns: `dict` com chaves `versao` e `documentos`.
- Raises: `CatalogoCorrompido` JSON malformado.

### 3.5. `salvar_catalogo`

```python
def salvar_catalogo(caminho: str | Path, catalogo: dict) -> None
```

Persiste o catálogo. Indentação de dois espaços, `ensure_ascii=False`.

### 3.6. `adicionar_documento`

```python
def adicionar_documento(
    caminho_catalogo: str | Path,
    nome_arquivo: str,
    titulo: str,
    autor: str,
    ano: int,
) -> dict
```

Valida, insere e persiste. Retorna o registro criado.

- Raises: `FormatoNaoSuportado`, `MetadadoInvalido`, `DocumentoJaExiste`, `CatalogoCorrompido` (propagada).

### 3.7. `remover_documento`

```python
def remover_documento(caminho_catalogo: str | Path, nome_arquivo: str) -> dict
```

Remove o registro pelo `nome_arquivo`. Retorna o registro removido.

- Raises: `DocumentoNaoEncontrado`, `CatalogoCorrompido` (propagada).

### 3.8. `buscar_documento`

```python
def buscar_documento(caminho_catalogo: str | Path, nome_arquivo: str) -> dict
```

Lookup pelo `nome_arquivo`. Retorna o registro encontrado.

- Raises: `DocumentoNaoEncontrado`, `CatalogoCorrompido` (propagada).

### 3.9. `listar_documentos`

```python
def listar_documentos(caminho_catalogo: str | Path) -> list[dict]
```

Retorna todos os registros em ordem de inserção.

- Raises: `CatalogoCorrompido` (propagada).

### 3.10. `renomear_documento`

```python
def renomear_documento(
    caminho_catalogo: str | Path,
    nome_atual: str,
    novo_nome: str,
) -> dict
```

Atualiza `nome_arquivo` e recalcula `tipo` quando a extensão muda. Demais metadados preservados.

- Raises: `FormatoNaoSuportado`, `DocumentoNaoEncontrado`, `DocumentoJaExiste`, `CatalogoCorrompido` (propagada).

## 4. Módulo `biblioteca.listagens`

Visões agrupadas sobre o catálogo.

### 4.1. `listar_por_tipo`

```python
def listar_por_tipo(caminho_catalogo: str | Path) -> dict[str, list[dict]]
```

Agrupa registros pelo rótulo `tipo`. Chaves em ordem alfabética.

- Raises: `CatalogoCorrompido` (propagada).

### 4.2. `listar_por_ano`

```python
def listar_por_ano(caminho_catalogo: str | Path) -> dict[int, list[dict]]
```

Agrupa registros pelo campo `ano`. Chaves em ordem crescente.

- Raises: `CatalogoCorrompido` (propagada).

## 5. Módulo `biblioteca.auditoria`

Cruzamento entre acervo físico e catálogo.

### 5.1. `auditar_acervo`

```python
def auditar_acervo(
    caminho_acervo: str | Path,
    caminho_catalogo: str | Path,
) -> dict[str, list]
```

Compara arquivos físicos no acervo com os registros do catálogo. Filtragem por `EXTENSOES_SUPORTADAS`.

Retorno: dicionário com três chaves.

| Chave | Conteúdo |
| --- | --- |
| `integros` | `list[dict]` registros com arquivo presente no disco. |
| `nao_encontrados` | `list[dict]` registros sem arquivo correspondente. |
| `nao_catalogados` | `list[Path]` arquivos no disco sem registro. Ordenada alfabeticamente. |

- Raises: `DiretorioNaoEncontrado`, `CatalogoCorrompido` (propagada).

## 6. Módulo `biblioteca.excecoes`

Hierarquia de exceções customizadas. Todas descendem de `BibliotecaError`.

| Classe | Quando é levantada |
| --- | --- |
| `BibliotecaError` | Classe-base. Capturável para tratamento uniforme. |
| `DocumentoNaoEncontrado` | Arquivo ou registro ausente. |
| `DocumentoJaExiste` | Tentativa de cadastrar duplicata. |
| `DiretorioNaoEncontrado` | Pasta inexistente. |
| `DiretorioJaExiste` | Tentativa de criar pasta sobre outra já presente. |
| `DiretorioNaoVazio` | Bloqueio de remoção em pasta com conteúdo. |
| `CatalogoCorrompido` | JSON malformado ou esquema incompatível. |
| `MetadadoInvalido` | Campo fora das regras de domínio. |
| `FormatoNaoSuportado` | Extensão fora da lista aceita. |

## 7. Módulo `biblioteca.cli`

Interface de linha de comando. Documentação detalhada dos subcomandos está em [`../README.md`](../README.md) seção 5, com exemplos de uso na seção 6.

### 7.1. Constantes

- `RAIZ_PROJETO: Path` raiz do projeto, calculada relativa ao módulo.
- `ACERVO_PADRAO: Path` aponta para `acervo/`.
- `CATALOGO_PADRAO: Path` aponta para `acervo/catalogo.json`.
- `COLUNAS_CSV_OBRIGATORIAS: tuple[str, ...]` colunas exigidas no CSV de importação.
- `COLUNA_CSV_OPCIONAL: str` coluna opcional do CSV (`"nome_destino"`).

### 7.2. `main`

```python
def main(argv: list[str] | None = None) -> int
```

Ponto de entrada da CLI. Constrói o parser, despacha para o handler do subcomando escolhido e captura erros uniformemente.

- Args: `argv` opcional, usa `sys.argv[1:]` quando `None`.
- Returns: código de saída. `0` em sucesso, `1` em `BibliotecaError`, `130` em `KeyboardInterrupt`.

### 7.3. Subcomandos

Cada subcomando é tratado por um handler `_comando_<nome>` interno ao módulo. A CLI sempre exibe metadados de retorno via `_imprimir_registro` para padronização visual.

| Subcomando | Handler |
| --- | --- |
| `listar` | `_comando_listar` |
| `adicionar` | `_comando_adicionar` |
| `importar` | `_comando_importar` |
| `renomear` | `_comando_renomear` |
| `remover` | `_comando_remover` |
| `buscar` | `_comando_buscar` |
| `listar-tipo` | `_comando_listar_tipo` |
| `listar-ano` | `_comando_listar_ano` |
| `auditar` | `_comando_auditar` |
