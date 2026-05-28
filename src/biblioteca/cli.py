"""Interface de linha de comando do sistema de gestão de acervo digital.

Permite ao bibliotecário operar as funcionalidades do pacote
`biblioteca` sem necessidade de programar em Python. Os comandos
disponíveis são:

    adicionar     Cadastra novo documento interativamente.
    importar      Importa documentos em lote a partir de arquivo CSV.
    renomear      Renomeia documento e atualiza catálogo.
    remover       Remove documento do acervo e do catálogo.
    buscar        Exibe os metadados de um documento.
    listar        Lista todos os registros do catálogo.
    listar-tipo   Agrupa registros por tipo de arquivo.
    listar-ano    Agrupa registros por ano de publicação.
    auditar       Cruza disco e catálogo para detectar divergências.

A execução ocorre via `python3 run.py <comando>` a partir da raiz do
projeto, ou via `python3 -m biblioteca <comando>` quando o diretório
`src/` está no PYTHONPATH.

Erros do domínio (descendentes de BibliotecaError) são capturados na
função `main` e reportados ao usuário com mensagem clara e código de
saída 1. Os handlers individuais permanecem livres de tratamento de
exceções.
"""

import argparse
import csv
import shutil
from pathlib import Path
from typing import Any, Callable

from .arquivos import validar_extensao
from .catalogo import (
    adicionar_documento,
    buscar_documento,
    listar_documentos,
    remover_documento,
    renomear_documento,
)
from .excecoes import (
    BibliotecaError,
    DocumentoJaExiste,
    DocumentoNaoEncontrado,
)


COLUNAS_CSV_OBRIGATORIAS = ("caminho_origem", "titulo", "autor", "ano")
COLUNA_CSV_OPCIONAL = "nome_destino"


RAIZ_PROJETO = Path(__file__).resolve().parents[2]
ACERVO_PADRAO = RAIZ_PROJETO / "acervo"
CATALOGO_PADRAO = ACERVO_PADRAO / "catalogo.json"


def main(argv: list[str] | None = None) -> int:
    """Entrada principal da CLI.

    Args:
        argv: Lista de argumentos a processar. Quando None, utiliza
            `sys.argv[1:]`.

    Returns:
        Código de saída. Zero em sucesso, 1 quando um erro de domínio
        é capturado e reportado ao usuário.
    """
    parser = _construir_parser()
    args = parser.parse_args(argv)

    try:
        args.handler(args)
    except BibliotecaError as erro:
        print(f"erro: {erro}")
        return 1
    except KeyboardInterrupt:
        print("\nOperação cancelada pelo usuário.")
        return 130

    return 0


def _construir_parser() -> argparse.ArgumentParser:
    """Constrói o ArgumentParser com todos os subcomandos do sistema."""
    parser = argparse.ArgumentParser(
        prog="biblioteca",
        description="Sistema de gestão de acervo digital.",
    )
    sub = parser.add_subparsers(dest="comando", required=True)

    _registrar(
        sub, "listar",
        "Lista todos os registros do catálogo.",
        _comando_listar,
    )
    _registrar(
        sub, "adicionar",
        "Cadastra novo documento interativamente.",
        _comando_adicionar,
    )
    _registrar(
        sub, "importar",
        "Importa documentos em lote a partir de arquivo CSV.",
        _comando_importar,
    )
    _registrar(
        sub, "renomear",
        "Renomeia documento e atualiza catálogo.",
        _comando_renomear,
    )
    _registrar(
        sub, "remover",
        "Remove documento do acervo e do catálogo.",
        _comando_remover,
    )
    _registrar(
        sub, "buscar",
        "Exibe os metadados de um documento.",
        _comando_buscar,
    )
    _registrar(
        sub, "listar-tipo",
        "Agrupa registros por tipo de arquivo.",
        _nao_implementado,
    )
    _registrar(
        sub, "listar-ano",
        "Agrupa registros por ano de publicação.",
        _nao_implementado,
    )
    _registrar(
        sub, "auditar",
        "Cruza disco e catálogo para detectar divergências.",
        _nao_implementado,
    )

    return parser


def _registrar(
    sub: Any,
    nome: str,
    descricao: str,
    handler: Callable[[argparse.Namespace], None],
) -> None:
    """Registra um subcomando no parser e associa seu handler.

    Args:
        sub: Action de subparsers do ArgumentParser raiz.
        nome: Nome do subcomando exposto ao usuário no terminal.
        descricao: Texto curto exibido pelo `--help`.
        handler: Função que executa o comando.
    """
    subparser = sub.add_parser(nome, help=descricao)
    subparser.set_defaults(handler=handler)


def _comando_listar(args: argparse.Namespace) -> None:
    """Imprime todos os registros do catálogo em ordem de inserção."""
    registros = listar_documentos(CATALOGO_PADRAO)

    if not registros:
        print("O catálogo está vazio.")
        return

    for registro in registros:
        _imprimir_registro(registro)


def _imprimir_registro(registro: dict) -> None:
    """Imprime um registro em layout legível.

    Args:
        registro: Dicionário no esquema definido por `catalogo`.
    """
    print(f"- {registro['nome_arquivo']}")
    print(f"    título: {registro['titulo']}")
    print(f"    autor:  {registro['autor']}")
    print(f"    ano:    {registro['ano']}")
    print(f"    tipo:   {registro['tipo']}")
    print()


def _nao_implementado(args: argparse.Namespace) -> None:
    """Stub para comandos a serem implementados em iterações seguintes."""
    print(f"Comando {args.comando!r} ainda não implementado.")


def _comando_adicionar(args: argparse.Namespace) -> None:
    """Cadastro interativo de um novo documento.

    Pergunta o caminho do arquivo de origem, os metadados e o nome
    final do arquivo no acervo. Copia o arquivo para a pasta
    `acervo/` e registra os metadados no catálogo. Se a inserção
    no catálogo falhar após a cópia, a cópia é desfeita para
    preservar a consistência entre disco e catálogo.
    """
    print("Cadastro de novo documento.")
    print("Pressione Ctrl+C para cancelar a qualquer momento.")
    print()

    caminho_origem = _perguntar_caminho_existente(
        "Caminho do arquivo a importar: "
    )
    titulo = _perguntar_texto("Título do documento: ", obrigatorio=True)
    autor = _perguntar_texto("Autor: ", obrigatorio=True)
    ano = _perguntar_inteiro("Ano de publicação: ")
    nome_destino = _perguntar_nome_destino(caminho_origem.name)

    validar_extensao(nome_destino)

    caminho_destino = ACERVO_PADRAO / nome_destino
    if caminho_destino.exists():
        raise DocumentoJaExiste(
            f"Já existe arquivo em {str(caminho_destino)!r}."
        )

    ACERVO_PADRAO.mkdir(parents=True, exist_ok=True)
    shutil.copy2(caminho_origem, caminho_destino)

    try:
        registro = adicionar_documento(
            CATALOGO_PADRAO,
            nome_arquivo=nome_destino,
            titulo=titulo,
            autor=autor,
            ano=ano,
        )
    except BibliotecaError:
        caminho_destino.unlink()
        raise

    print()
    print("Documento cadastrado:")
    _imprimir_registro(registro)


def _comando_importar(args: argparse.Namespace) -> None:
    """Importa documentos em lote a partir de um arquivo CSV.

    O CSV deve ter cabeçalho com as colunas obrigatórias
    `caminho_origem`, `titulo`, `autor`, `ano` e a coluna opcional
    `nome_destino`. Cada linha é processada de forma independente.
    Falhas em uma linha não interrompem o processamento das demais e
    são reportadas individualmente ao usuário.
    """
    print("Importação em lote a partir de CSV.")
    print()

    caminho_csv = _perguntar_caminho_existente("Caminho do arquivo CSV: ")
    sucessos = 0
    falhas = 0

    with open(caminho_csv, newline="", encoding="utf-8") as arquivo:
        leitor = csv.DictReader(arquivo)
        _validar_colunas_csv(leitor.fieldnames or [])

        ACERVO_PADRAO.mkdir(parents=True, exist_ok=True)

        # A enumeração começa em 2 porque a linha 1 do arquivo é o
        # cabeçalho consumido pelo DictReader.
        for numero_linha, linha in enumerate(leitor, start=2):
            try:
                nome = _importar_linha(linha)
                sucessos += 1
                print(f"  linha {numero_linha}: {nome} importado.")
            except (BibliotecaError, FileNotFoundError, ValueError) as erro:
                falhas += 1
                print(f"  linha {numero_linha}: erro - {erro}")

    print()
    print(f"Importação concluída: {sucessos} sucesso(s), {falhas} falha(s).")


def _importar_linha(linha: dict) -> str:
    """Processa uma linha do CSV: copia o arquivo e registra no catálogo.

    Args:
        linha: Dicionário com as colunas obrigatórias e, opcionalmente,
            `nome_destino`.

    Returns:
        Nome final do arquivo no acervo.

    Raises:
        FileNotFoundError: Quando o caminho de origem não existe.
        ValueError: Quando o ano não pode ser convertido para int.
        BibliotecaError: Propagada das funções de catálogo.
    """
    caminho_origem = Path(linha["caminho_origem"].strip()).expanduser()
    if not caminho_origem.is_file():
        raise FileNotFoundError(
            f"Arquivo {str(caminho_origem)!r} não encontrado."
        )

    valor_nome_destino = (linha.get(COLUNA_CSV_OPCIONAL) or "").strip()
    nome_destino = valor_nome_destino or caminho_origem.name

    titulo = linha["titulo"].strip()
    autor = linha["autor"].strip()
    ano = int(linha["ano"].strip())

    validar_extensao(nome_destino)

    caminho_destino = ACERVO_PADRAO / nome_destino
    if caminho_destino.exists():
        raise DocumentoJaExiste(
            f"Já existe arquivo em {str(caminho_destino)!r}."
        )

    shutil.copy2(caminho_origem, caminho_destino)

    try:
        adicionar_documento(
            CATALOGO_PADRAO,
            nome_arquivo=nome_destino,
            titulo=titulo,
            autor=autor,
            ano=ano,
        )
    except BibliotecaError:
        caminho_destino.unlink()
        raise

    return nome_destino


def _validar_colunas_csv(colunas: list[str]) -> None:
    """Verifica que o CSV traz todas as colunas obrigatórias.

    Raises:
        ValueError: Quando alguma coluna obrigatória está ausente.
    """
    faltantes = [c for c in COLUNAS_CSV_OBRIGATORIAS if c not in colunas]
    if faltantes:
        raise ValueError(
            f"CSV não tem as colunas obrigatórias: {faltantes}. "
            f"Colunas esperadas: "
            f"{COLUNAS_CSV_OBRIGATORIAS + (COLUNA_CSV_OPCIONAL,)}."
        )


def _perguntar_caminho_existente(prompt: str) -> Path:
    """Pede um caminho de arquivo existente, repetindo em caso de erro.

    Aceita `~` no início do caminho, expandindo para o diretório do
    usuário. Retorna apenas quando o caminho aponta para um arquivo
    válido.
    """
    while True:
        resposta = input(prompt).strip()
        if not resposta:
            print("Caminho não pode estar em branco.")
            continue

        caminho = Path(resposta).expanduser()
        if not caminho.is_file():
            print(f"Arquivo {str(caminho)!r} não encontrado.")
            continue

        return caminho


def _perguntar_texto(prompt: str, obrigatorio: bool = False) -> str:
    """Pede uma resposta textual.

    Args:
        prompt: Texto exibido ao usuário.
        obrigatorio: Quando True, repete a pergunta até obter resposta
            não vazia.
    """
    while True:
        resposta = input(prompt).strip()
        if resposta or not obrigatorio:
            return resposta
        print("Resposta não pode estar em branco.")


def _perguntar_inteiro(prompt: str) -> int:
    """Pede um inteiro, repetindo em caso de entrada inválida."""
    while True:
        resposta = input(prompt).strip()
        try:
            return int(resposta)
        except ValueError:
            print(f"Valor {resposta!r} não é um inteiro válido.")


def _perguntar_nome_destino(nome_padrao: str) -> str:
    """Pede o nome final do arquivo no acervo.

    Em resposta vazia, devolve o `nome_padrao` (geralmente o nome
    original do arquivo).
    """
    resposta = input(
        f"Nome do arquivo no acervo (Enter para manter {nome_padrao!r}): "
    ).strip()
    return resposta or nome_padrao


def _comando_renomear(args: argparse.Namespace) -> None:
    """Renomeia documento no acervo e atualiza o catálogo.

    Pergunta o nome atual e o novo nome. Renomeia primeiro o arquivo
    físico em `acervo/` e depois o registro no catálogo. Se a
    atualização do catálogo falhar, o nome físico é revertido para
    preservar a consistência entre disco e catálogo.
    """
    print("Renomeação de documento.")
    print()

    nome_atual = _perguntar_texto(
        "Nome atual do arquivo: ", obrigatorio=True
    )
    caminho_atual = ACERVO_PADRAO / nome_atual
    if not caminho_atual.is_file():
        raise DocumentoNaoEncontrado(
            f"Arquivo {str(caminho_atual)!r} não encontrado no acervo."
        )

    novo_nome = _perguntar_texto(
        "Novo nome do arquivo: ", obrigatorio=True
    )
    validar_extensao(novo_nome)

    caminho_novo = ACERVO_PADRAO / novo_nome
    if caminho_novo.exists():
        raise DocumentoJaExiste(
            f"Já existe arquivo em {str(caminho_novo)!r}."
        )

    caminho_atual.rename(caminho_novo)
    try:
        registro = renomear_documento(
            CATALOGO_PADRAO, nome_atual, novo_nome
        )
    except BibliotecaError:
        caminho_novo.rename(caminho_atual)
        raise

    print()
    print("Documento renomeado:")
    _imprimir_registro(registro)


def _comando_remover(args: argparse.Namespace) -> None:
    """Remove documento do acervo e do catálogo.

    Pergunta o nome do arquivo, exibe os metadados atuais e solicita
    confirmação explícita. A remoção ocorre primeiro no catálogo e
    depois no sistema de arquivos. Caso o arquivo físico não esteja
    presente, o registro é removido mesmo assim e o usuário recebe
    um aviso.
    """
    print("Remoção de documento.")
    print()

    nome = _perguntar_texto("Nome do arquivo: ", obrigatorio=True)
    registro = buscar_documento(CATALOGO_PADRAO, nome)

    print()
    print("Registro encontrado:")
    _imprimir_registro(registro)

    if not _confirmar("Confirma a remoção?"):
        print("Operação cancelada.")
        return

    remover_documento(CATALOGO_PADRAO, nome)

    caminho = ACERVO_PADRAO / nome
    if caminho.is_file():
        caminho.unlink()
        print(f"Documento {nome!r} removido com sucesso.")
    else:
        print(
            f"Registro removido. Aviso: arquivo {str(caminho)!r} "
            f"já não estava presente no acervo."
        )


def _comando_buscar(args: argparse.Namespace) -> None:
    """Exibe os metadados de um documento do catálogo."""
    nome = _perguntar_texto("Nome do arquivo: ", obrigatorio=True)
    registro = buscar_documento(CATALOGO_PADRAO, nome)
    print()
    _imprimir_registro(registro)


def _confirmar(prompt: str) -> bool:
    """Pergunta sim/não com default não.

    Retorna True apenas para respostas 's', 'sim' (em qualquer caixa).
    Qualquer outra resposta, inclusive vazia, retorna False. Essa
    assimetria torna a confirmação consciente, exigindo entrada
    afirmativa explícita.
    """
    resposta = input(f"{prompt} (s/N): ").strip().lower()
    return resposta in ("s", "sim")
