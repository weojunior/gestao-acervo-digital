"""Auditoria de consistência entre o acervo físico e o catálogo.

Cruza os arquivos presentes no diretório do acervo com os registros do
catálogo JSON e classifica cada item em uma de três categorias:

    - íntegro: arquivo no disco e registro no catálogo.
    - não catalogado: arquivo no disco sem registro correspondente.
    - não encontrado: registro no catálogo sem arquivo no disco.

A função apoia a manutenção da qualidade do acervo ao expor cadastros
incompletos e arquivos órfãos, situações comuns em bibliotecas que
gerenciam documentos em fluxo manual.

Apenas arquivos com extensão listada em EXTENSOES_SUPORTADAS são
considerados. Arquivos auxiliares como `catalogo.json` ou metadados
do sistema operacional (`.DS_Store`, `.gitkeep`) ficam de fora por
terem extensões não previstas para documentos.
"""

from pathlib import Path

from .arquivos import EXTENSOES_SUPORTADAS
from .catalogo import listar_documentos
from .diretorios import listar_diretorio


def auditar_acervo(
    caminho_acervo: str | Path,
    caminho_catalogo: str | Path,
) -> dict[str, list]:
    """Compara o estado físico do acervo com o conteúdo do catálogo.

    Args:
        caminho_acervo: Diretório onde estão os arquivos de documentos.
        caminho_catalogo: Caminho do arquivo JSON do catálogo.

    Returns:
        Dicionário com três chaves:

            - `nao_catalogados`: lista de Path ordenada, com os
              arquivos presentes no acervo mas sem registro no
              catálogo.
            - `nao_encontrados`: lista de dict, com os registros do
              catálogo cujo `nome_arquivo` não foi encontrado no
              disco.
            - `integros`: lista de dict, com os registros do catálogo
              cujo arquivo está presente no disco.

    Raises:
        DiretorioNaoEncontrado: Quando `caminho_acervo` não aponta
            para um diretório existente.
        CatalogoCorrompido: Propagada de `listar_documentos` quando o
            JSON do catálogo não pode ser interpretado.
    """
    pasta_acervo = Path(caminho_acervo)

    nomes_no_disco = {
        item.name
        for item in listar_diretorio(pasta_acervo)
        if item.is_file() and item.suffix.lower() in EXTENSOES_SUPORTADAS
    }

    registros = listar_documentos(caminho_catalogo)
    nomes_catalogados = {registro["nome_arquivo"] for registro in registros}

    nao_catalogados = sorted(
        pasta_acervo / nome
        for nome in (nomes_no_disco - nomes_catalogados)
    )

    nao_encontrados = [
        registro
        for registro in registros
        if registro["nome_arquivo"] not in nomes_no_disco
    ]

    integros = [
        registro
        for registro in registros
        if registro["nome_arquivo"] in nomes_no_disco
    ]

    return {
        "nao_catalogados": nao_catalogados,
        "nao_encontrados": nao_encontrados,
        "integros": integros,
    }
