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
from pathlib import Path
from typing import Any, Callable

from .catalogo import listar_documentos
from .excecoes import BibliotecaError


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
        _nao_implementado,
    )
    _registrar(
        sub, "importar",
        "Importa documentos em lote a partir de arquivo CSV.",
        _nao_implementado,
    )
    _registrar(
        sub, "renomear",
        "Renomeia documento e atualiza catálogo.",
        _nao_implementado,
    )
    _registrar(
        sub, "remover",
        "Remove documento do acervo e do catálogo.",
        _nao_implementado,
    )
    _registrar(
        sub, "buscar",
        "Exibe os metadados de um documento.",
        _nao_implementado,
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
