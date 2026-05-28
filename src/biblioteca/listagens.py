"""Listagens analíticas do acervo digital.

Fornece visões agrupadas dos registros do catálogo por tipo de arquivo
e por ano de publicação, conforme exige o Critério 1 da atividade.

As funções consomem o catálogo via `catalogo.listar_documentos` e não
tocam diretamente no sistema de arquivos. A separação deste módulo em
relação a `catalogo` reflete a distinção entre operações CRUD (lá) e
consultas analíticas sobre os mesmos dados (aqui).
"""

from collections import defaultdict
from pathlib import Path

from .catalogo import listar_documentos


def listar_por_tipo(caminho_catalogo: str | Path) -> dict[str, list[dict]]:
    """Agrupa os registros do catálogo pelo rótulo de tipo.

    Args:
        caminho_catalogo: Caminho do arquivo do catálogo.

    Returns:
        Dicionário com chaves ordenadas alfabeticamente. Cada chave é
        um rótulo de tipo (por exemplo, "PDF", "EPUB") e cada valor é
        a lista de registros daquele tipo, preservando a ordem de
        inserção no catálogo.

    Raises:
        CatalogoCorrompido: Propagada de `listar_documentos` quando o
            JSON não pode ser interpretado.
    """
    agrupado: dict[str, list[dict]] = defaultdict(list)

    for registro in listar_documentos(caminho_catalogo):
        agrupado[registro["tipo"]].append(registro)

    return dict(sorted(agrupado.items()))


def listar_por_ano(caminho_catalogo: str | Path) -> dict[int, list[dict]]:
    """Agrupa os registros do catálogo pelo ano de publicação.

    Args:
        caminho_catalogo: Caminho do arquivo do catálogo.

    Returns:
        Dicionário com chaves em ordem crescente. Cada chave é um ano
        e cada valor é a lista de registros publicados naquele ano,
        preservando a ordem de inserção no catálogo.

    Raises:
        CatalogoCorrompido: Propagada de `listar_documentos` quando o
            JSON não pode ser interpretado.
    """
    agrupado: dict[int, list[dict]] = defaultdict(list)

    for registro in listar_documentos(caminho_catalogo):
        agrupado[registro["ano"]].append(registro)

    return dict(sorted(agrupado.items()))
