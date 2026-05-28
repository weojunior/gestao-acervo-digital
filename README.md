# Gestão de acervo digital

Sistema em Python para administração de documentos digitais em bibliotecas universitárias. Os bibliotecários adicionam, renomeiam, removem e listam documentos (PDF, ePUB, OpenDocument e outros formatos textuais) por uma interface de linha de comando, com listagem agrupada por tipo de arquivo e por ano de publicação, e auditoria de consistência entre o acervo físico e o catálogo de metadados.

Projeto desenvolvido como atividade avaliativa da disciplina Programação para Ciência de Dados, 1º período do Curso Superior de Tecnologia em Inteligência Artificial, PUC-PR.

## 1. Visão geral

O sistema substitui um fluxo manual de gestão de documentos digitais por uma ferramenta versionável e auditável. O catálogo de metadados fica em `acervo/catalogo.json`, com um registro por documento contendo nome do arquivo, título, autor, ano de publicação e tipo derivado da extensão. Os arquivos físicos vivem em `acervo/`, separados dos metadados mas sob auditoria de consistência.

A operação ocorre por uma CLI com nove subcomandos. O cadastro tem dois modos: interativo (prompts no terminal para inserção pontual) e importação em lote a partir de arquivo CSV (para carga inicial do acervo ou migração de planilha). Listagens agrupadas por tipo e por ano cobrem o requisito analítico da atividade. A auditoria cruza o conteúdo de `acervo/` com o catálogo e classifica cada item em uma de três categorias: íntegro, registrado sem arquivo, ou no disco sem registro.

## 2. Pré-requisitos

| Item | Versão mínima |
| --- | --- |
| Python | 3.10 |
| pytest | 8.0 (apenas para rodar a suíte de testes) |

A versão mínima do Python deve-se ao uso da sintaxe de tipo `str | Path` (PEP 604, Python 3.10) e dos coletores genéricos `list[Path]` e `tuple[str, ...]` (PEP 585, Python 3.9).

## 3. Instalação

```bash
git clone https://github.com/weojunior/gestao-acervo-digital.git
cd gestao-acervo-digital
pip3 install -r requirements.txt
```

A última linha instala apenas o `pytest` e suas dependências de execução. O sistema em si não tem dependências externas além da biblioteca padrão do Python.

## 4. Execução

A CLI é acessada via o wrapper `run.py` na raiz do projeto:

```bash
python3 run.py --help
```

A flag `--help` lista os nove subcomandos disponíveis. A execução não exige instalação do pacote via pip porque o wrapper insere `src/` em `sys.path` automaticamente.

## 5. Subcomandos

| Subcomando | Modo | Descrição |
| --- | --- | --- |
| `adicionar` | Interativo | Cadastra novo documento. Pede caminho do arquivo de origem, título, autor, ano e nome final. Copia o arquivo para `acervo/` e registra os metadados no catálogo. |
| `importar` | Interativo | Importa documentos em lote a partir de arquivo CSV. Pede o caminho do CSV e processa linha a linha. Falhas em uma linha não interrompem o processamento das demais. |
| `renomear` | Interativo | Renomeia documento existente. Pede nome atual e novo nome. Atualiza o arquivo físico e o registro do catálogo em conjunto, com rollback automático em caso de erro. |
| `remover` | Interativo | Remove documento. Pede o nome do arquivo, exibe os metadados para conferência, solicita confirmação explícita (`s` para confirmar) e remove do catálogo e do disco. |
| `buscar` | Interativo | Exibe os metadados de um documento pelo nome do arquivo. |
| `listar` | Direto | Lista todos os registros do catálogo em ordem de inserção. |
| `listar-tipo` | Direto | Agrupa registros por tipo de arquivo, em ordem alfabética das chaves. |
| `listar-ano` | Direto | Agrupa registros por ano de publicação, em ordem cronológica crescente. |
| `auditar` | Direto | Cruza acervo físico e catálogo. Reporta documentos íntegros, registros sem arquivo no disco e arquivos no disco sem cadastro. |

## 6. Exemplo de uso

Cadastro de um documento via fluxo interativo:

```
$ python3 run.py adicionar
Cadastro de novo documento.
Pressione Ctrl+C para cancelar a qualquer momento.

Caminho do arquivo a importar: /Users/biblio/Downloads/estatistica.pdf
Título do documento: Estatística Bayesiana
Autor: Andrew Gelman
Ano de publicação: 2013
Nome do arquivo no acervo (Enter para manter 'estatistica.pdf'):

Documento cadastrado:
- estatistica.pdf
    título: Estatística Bayesiana
    autor:  Andrew Gelman
    ano:    2013
    tipo:   PDF
```

Listagem por ano:

```
$ python3 run.py listar-ano
2013 (1 documento)
- estatistica.pdf
    título: Estatística Bayesiana
    autor:  Andrew Gelman
    ano:    2013
    tipo:   PDF
```

## 7. Formato do CSV de importação

O arquivo CSV usado pelo subcomando `importar` deve ter cabeçalho com cinco colunas, sendo quatro obrigatórias e uma opcional.

| Coluna | Obrigatória | Descrição |
| --- | --- | --- |
| `caminho_origem` | Sim | Caminho do arquivo a copiar para o acervo. Aceita `~` no início. |
| `titulo` | Sim | Título do documento. |
| `autor` | Sim | Autor do documento. |
| `ano` | Sim | Ano de publicação. Inteiro entre 1450 e o ano corrente mais um. |
| `nome_destino` | Não | Nome final no acervo. Quando vazio, usa o nome do arquivo de origem. |

Exemplo:

```csv
caminho_origem,titulo,autor,ano,nome_destino
/Users/biblio/Downloads/livro_a.pdf,Livro A,Autor X,2024,
/Users/biblio/Downloads/livro_b.epub,Livro B,Autor Y,2024,calculo_stewart.epub
```

A primeira linha mantém o nome original (`livro_a.pdf`). A segunda renomeia para `calculo_stewart.epub` no momento do cadastro.

## 8. Estrutura do código

```
gestao-acervo-digital/
├── README.md                  Este documento.
├── CONTRIBUTING.md            Guia de contribuição (commits, PRs, código).
├── RELATORIO_TESTES.md        Relatório da suíte de testes automatizados.
├── RELATORIO_FEEDBACK.md      Relatório de feedback dos bibliotecários.
├── requirements.txt           Dependências do projeto.
├── run.py                     Wrapper de execução da CLI.
├── .gitignore                 Padrões versionados de exclusão do Git.
├── .github/
│   └── pull_request_template.md   Template de pull request.
├── acervo/                    Pasta de trabalho (conteúdo ignorado pelo Git).
│   └── .gitkeep
├── docs/                      Documentação técnica por módulo.
├── src/biblioteca/
│   ├── __init__.py            Metadados do pacote.
│   ├── __main__.py            Entrypoint para python3 -m biblioteca.
│   ├── arquivos.py            Operações em arquivos individuais.
│   ├── diretorios.py          Gerenciamento de diretórios.
│   ├── catalogo.py            CRUD e persistência do catálogo JSON.
│   ├── listagens.py           Agrupamento por tipo e por ano.
│   ├── auditoria.py           Cruzamento disco e catálogo.
│   ├── excecoes.py            Hierarquia de exceções customizadas.
│   └── cli.py                 Lógica da interface de linha de comando.
└── tests/
    ├── conftest.py            Configuração compartilhada do pytest.
    ├── test_arquivos.py
    ├── test_diretorios.py
    ├── test_catalogo.py
    ├── test_listagens.py
    └── test_auditoria.py
```

## 9. Testes

Execução da suíte completa:

```bash
python3 -m pytest
```

A suíte tem 80 testes e roda em menos de um décimo de segundo. Detalhamento da metodologia, inventário por módulo e limitações reconhecidas estão em [`RELATORIO_TESTES.md`](RELATORIO_TESTES.md).

## 10. Formatos aceitos

A constante `EXTENSOES_SUPORTADAS` em `src/biblioteca/arquivos.py` lista os formatos aceitos no acervo. Atualmente: `.pdf`, `.epub`, `.txt`, `.md`, `.docx`, `.doc`, `.odt`, `.ods`. A inclusão de novos formatos exige adicionar a extensão nessa tupla e o rótulo correspondente em `TIPO_POR_EXTENSAO` no módulo `catalogo.py`.

## 11. Documentação adicional

- [`CONTRIBUTING.md`](CONTRIBUTING.md): guia de contribuição, padrão de commits, convenções de código, fluxo de PR.
- [`RELATORIO_TESTES.md`](RELATORIO_TESTES.md): relatório da suíte de testes automatizados.
- [`RELATORIO_FEEDBACK.md`](RELATORIO_FEEDBACK.md): consulta a bibliotecários e ajustes incorporados.
- [`docs/`](docs/): documentação técnica por módulo do pacote `biblioteca`.

## 12. Licença

Projeto acadêmico sem licença pública atribuída. Uso restrito ao contexto da disciplina e à avaliação correspondente.
