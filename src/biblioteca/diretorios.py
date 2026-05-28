"""Operações de gerenciamento de diretórios do acervo digital.

O módulo cobre as três operações exigidas pelo Critério 1 da atividade
no que diz respeito a diretórios: criar, listar e remover. As funções
operam sobre `pathlib.Path` e reportam erros por meio das exceções
customizadas definidas em `excecoes`.

A função `listar_diretorio` aceita o parâmetro `recursivo` para
acomodar tanto a inspeção pontual de uma pasta quanto a varredura
completa do acervo, necessária ao agrupamento por tipo e por ano
implementado na Fase 3.

A função `remover_diretorio` exige escolha explícita entre remoção
simples (apenas pastas vazias) e remoção em cascata. Esse desenho
protege o bibliotecário de apagar o acervo por engano em uma chamada
acidental.
"""

import shutil
from pathlib import Path

from .excecoes import (
    DiretorioJaExiste,
    DiretorioNaoEncontrado,
    DiretorioNaoVazio,
)


def criar_diretorio(caminho: str | Path, criar_pais: bool = False) -> Path:
    """Cria um diretório no caminho indicado.

    Args:
        caminho: Local onde o diretório será criado.
        criar_pais: Quando True, cria também os diretórios intermediários
            que ainda não existirem. Quando False, exige que o diretório
            pai já exista.

    Returns:
        Objeto Path do diretório recém-criado.

    Raises:
        DiretorioJaExiste: Quando o caminho indicado já está ocupado.
        DiretorioNaoEncontrado: Quando criar_pais=False e o diretório
            pai do caminho não existe.
    """
    diretorio = Path(caminho)

    if diretorio.exists():
        raise DiretorioJaExiste(
            f"Já existe diretório em {str(diretorio)!r}."
        )

    if not criar_pais:
        pai = diretorio.parent
        if pai.parts and not pai.exists():
            raise DiretorioNaoEncontrado(
                f"Diretório pai {str(pai)!r} não existe. "
                f"Passe criar_pais=True para criar a hierarquia."
            )

    diretorio.mkdir(parents=criar_pais)
    return diretorio


def listar_diretorio(
    caminho: str | Path,
    recursivo: bool = False,
) -> list[Path]:
    """Lista o conteúdo de um diretório.

    Args:
        caminho: Caminho do diretório a listar.
        recursivo: Quando True, inclui o conteúdo de subdiretórios em
            qualquer profundidade. Quando False, lista apenas os itens
            do nível imediato.

    Returns:
        Lista de Path ordenada alfabeticamente, contendo arquivos e
        subdiretórios encontrados.

    Raises:
        DiretorioNaoEncontrado: Quando o diretório não existe ou o
            caminho aponta para um arquivo.
    """
    diretorio = Path(caminho)

    if not diretorio.is_dir():
        raise DiretorioNaoEncontrado(
            f"Diretório {str(diretorio)!r} não encontrado."
        )

    if recursivo:
        itens = list(diretorio.rglob("*"))
    else:
        itens = list(diretorio.iterdir())

    return sorted(itens)


def remover_diretorio(
    caminho: str | Path,
    recursivo: bool = False,
) -> None:
    """Remove um diretório do sistema de arquivos.

    Args:
        caminho: Caminho do diretório a ser removido.
        recursivo: Quando True, remove o diretório e todo o seu
            conteúdo. Quando False, exige que o diretório esteja
            vazio.

    Raises:
        DiretorioNaoEncontrado: Quando o diretório não existe.
        DiretorioNaoVazio: Quando recursivo=False e o diretório contém
            arquivos ou subpastas.
    """
    diretorio = Path(caminho)

    if not diretorio.is_dir():
        raise DiretorioNaoEncontrado(
            f"Diretório {str(diretorio)!r} não encontrado."
        )

    if recursivo:
        shutil.rmtree(diretorio)
        return

    try:
        diretorio.rmdir()
    except OSError as erro:
        raise DiretorioNaoVazio(
            f"Diretório {str(diretorio)!r} contém itens. "
            f"Passe recursivo=True para remoção em cascata."
        ) from erro
