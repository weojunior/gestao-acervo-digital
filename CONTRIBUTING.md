# Guia de contribuição

Documento orientador para colaboradores que vão alterar o código ou a documentação do sistema de gestão de acervo digital. Cobre o setup do ambiente local, o ciclo de trabalho com Git e GitHub, o padrão de mensagens de commit, as convenções de código Python e a execução da suíte de testes.

## 1. Pré-requisitos

| Item | Versão mínima | Observação |
| --- | --- | --- |
| Python | 3.10 | Sintaxe `str | Path` (PEP 604) e `tuple[str, ...]` (PEP 585) usados no código. |
| Git | 2.28 | A flag `git init -b main` exige essa versão. |
| GitHub CLI (`gh`) | 2.0 | Apenas para criar PRs e clonar pelo terminal. Operações via web também funcionam. |
| pytest | 8.0 | Listado em `requirements.txt`. |

## 2. Configurando o ambiente local

A sequência abaixo prepara um ambiente novo a partir do zero.

```bash
git clone https://github.com/weojunior/gestao-acervo-digital.git
cd gestao-acervo-digital
pip3 install -r requirements.txt
python3 -m pytest
```

O comando final confirma que o ambiente está funcional: a suíte deve passar com 78 testes verdes em menos de um segundo.

A execução da CLI ocorre via wrapper na raiz do projeto:

```bash
python3 run.py --help
```

O wrapper insere `src/` em `sys.path` automaticamente, dispensando instalação do pacote via pip.

## 3. Ciclo de desenvolvimento

Toda mudança segue o fluxo abaixo. As etapas estão numeradas para indicar a ordem, mas algumas (especialmente 3.2 e 3.3) podem se repetir várias vezes dentro do mesmo PR.

### 3.1. Crie uma branch a partir de `main`

A branch `main` é protegida por convenção. Nenhum commit deve ser feito diretamente nela. Sempre crie uma branch derivada:

```bash
git checkout main
git pull origin main
git checkout -b tipo/descricao-curta
```

O nome da branch segue o padrão `tipo/descricao-curta`, em que `tipo` espelha os tipos do Conventional Commits (ver seção 4) e `descricao-curta` é uma frase com hifens, sem espaços. Exemplos: `feat/exportar-catalogo-csv`, `fix/permitir-ano-1450`, `docs/atualizar-readme-instalacao`.

### 3.2. Realize commits granulares

Cada commit deve representar uma unidade lógica de mudança. Commits muito grandes ou que misturam conteúdos distintos (código novo e refatoração no mesmo commit) dificultam a revisão e o `git bisect` futuro.

```bash
git add caminho/do/arquivo.py
git status
git commit -m "tipo: descrição curta no imperativo"
```

Evite `git add .` quando houver arquivos não relacionados modificados. Selecione explicitamente o que entra no commit.

### 3.3. Sincronize com o remote

Depois de um ou mais commits locais:

```bash
git push origin tipo/descricao-curta
```

Na primeira execução por branch, use `git push -u origin tipo/descricao-curta` para configurar o tracking. Nas seguintes, `git push` basta.

### 3.4. Abra um pull request

Após o último push, abra o PR. Pelo terminal:

```bash
gh pr create --base main
```

O `gh` lê o template em `.github/pull_request_template.md` e abre um editor para você preencher resumo, detalhes, tipo, roteiro de testes e checklist. Alternativamente, acesse o repositório no navegador e clique em "Compare & pull request" no banner que aparece após o push.

O PR deve ter:

- Título no padrão do Conventional Commits, igual ou similar à mensagem do commit principal.
- Descrição que explique o porquê da mudança, não apenas o quê (esse último o `git diff` já mostra).
- Roteiro de testes que o revisor possa seguir para validar.
- Checklist do template marcado conforme aplicável.

### 3.5. Responda à revisão

Comentários do revisor podem ser respondidos com novos commits na mesma branch. Não force push para reescrever o histórico durante a revisão, mesmo em revisões longas. Force push só após aprovação, se for necessário um squash explícito.

### 3.6. Merge

A estratégia padrão é "Create a merge commit" (preserva o histórico granular dos commits da branch). Não use "Squash and merge" como padrão, porque perde a granularidade que justificou a divisão em vários commits.

Depois do merge, apague a branch remota (botão "Delete branch" no GitHub) e a local:

```bash
git checkout main
git pull origin main
git branch -d tipo/descricao-curta
```

## 4. Padrão de mensagens de commit

O projeto adota Conventional Commits. Cada mensagem segue a forma `tipo: descrição no infinitivo`, sem ponto final.

Tipos aceitos:

| Tipo | Quando usar |
| --- | --- |
| `feat` | Nova funcionalidade do sistema visível ao usuário final. |
| `fix` | Correção de defeito em comportamento existente. |
| `docs` | Alterações em documentação (`README`, `CONTRIBUTING`, comentários extensos, docstrings substanciais). |
| `refactor` | Reorganização de código sem mudança de comportamento externo. |
| `test` | Adição, ajuste ou remoção de testes automatizados. |
| `chore` | Configuração, infraestrutura, ajustes em `.gitignore` ou `requirements.txt`. |
| `style` | Formatação que não altera semântica (raro neste projeto). |
| `perf` | Melhoria de desempenho. |
| `build` | Mudanças no sistema de build (raro neste projeto). |
| `ci` | Configuração de integração contínua. |

Exemplos válidos extraídos do histórico do projeto:

- `feat: adicionar funções de criar, ler, renomear e remover arquivos`
- `refactor: reorganizar src em pacote biblioteca e introduzir exceções customizadas`
- `test: cobrir módulo catalogo com testes unitários`
- `chore: excluir conteúdo de acervo do versionamento`

Mensagens devem estar em português e usar verbo no infinitivo. Evite mensagens vagas como `correções` ou `update`.

## 5. Padrão de código Python

O projeto segue as PEPs 8, 257 e 484.

| Aspecto | Convenção |
| --- | --- |
| Indentação | 4 espaços, sem tabs. |
| Largura de linha | até 88 caracteres. |
| Nomes de função e variável | `snake_case`. |
| Nomes de classe | `PascalCase`. |
| Nomes de constante | `UPPER_SNAKE_CASE`. |
| Imports | três blocos separados por linha em branco: stdlib, terceiros, locais. |
| Docstrings | obrigatórias em toda função, classe e módulo público. Estilo Google com seções `Args`, `Returns`, `Raises`. |
| Type hints | obrigatórios em assinaturas de função pública. Sintaxe `str | Path` (PEP 604) e `list[Path]` (PEP 585). |
| Tratamento de erro | exceções customizadas descendentes de `BibliotecaError`. Nunca `except: pass`. |
| Constantes | strings repetidas e números mágicos viram constantes no topo do módulo. |
| Comentários | apenas onde o porquê não for óbvio. Em português. |

Funções privadas (uso interno do módulo) recebem prefixo de underscore: `_validar_metadados`, `_tipo_de`.

## 6. Testes

A suíte usa pytest e fica em `tests/`. Cada módulo do pacote tem seu arquivo de teste correspondente: `test_arquivos.py` testa `arquivos.py`, e assim por diante.

Convenções:

- Nome do teste no formato `test_<funcao>_<comportamento_esperado>`.
- Padrão Arrange-Act-Assert dentro de cada teste.
- Uso da fixture `tmp_path` do pytest para isolamento. Não escreva testes que dependam de arquivos fora dessa pasta temporária.
- Cobertura por função: um teste para o caminho feliz e um teste para cada exceção esperada.

Execução:

```bash
python3 -m pytest               # suíte completa
python3 -m pytest -v            # verbose
python3 -m pytest --tb=no -q    # resumo compacto
python3 -m pytest tests/test_catalogo.py    # arquivo específico
```

PRs que adicionam ou alteram código de produção devem incluir testes correspondentes. PRs que quebram testes existentes precisam justificar a quebra na descrição.

## 7. Documentação

Mudanças de comportamento externo, novos comandos da CLI ou novos formatos de dados devem atualizar:

- `README.md`, quando alteram o uso visível ao usuário.
- `RELATORIO_TESTES.md`, quando adicionam ou removem testes (atualizar a seção 4 e o número total na 5).
- Docstring do módulo afetado, quando alteram a responsabilidade do módulo.

## 8. Dúvidas

Abra uma issue no repositório com a tag `question` antes de iniciar trabalho extenso baseado em interpretação própria de requisito. Vale o princípio de evitar retrabalho.
