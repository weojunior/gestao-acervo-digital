"""Operações de manipulação de arquivos individuais do acervo.

O módulo cobre as quatro operações exigidas pelo Critério 1 da atividade
no que diz respeito a arquivos: criar, ler, renomear e remover. A operação
de abertura está embutida em `ler_arquivo`, que abre, lê e fecha em uma
chamada atômica, padrão idiomático do Python para arquivos de texto.

As funções operam apenas sobre arquivos de texto. Documentos binários
como PDF e ePUB são tratados como entidades opacas pelo sistema: existem
no sistema de arquivos, são movidos, renomeados ou removidos, mas seus
conteúdos não são lidos por este módulo. Os metadados desses documentos
ficam registrados em `acervo/catalogo.json` pelo módulo `catalogo`.
"""

from pathlib import Path

from .excecoes import (
    DocumentoJaExiste,
    DocumentoNaoEncontrado,
    FormatoNaoSuportado,
)


EXTENSOES_SUPORTADAS = (".pdf", ".epub", ".txt", ".md", ".docx", ".doc")
CODIFICACAO_PADRAO = "utf-8"


def validar_extensao(caminho: str | Path) -> None:
    """Valida que a extensão do arquivo está entre os formatos suportados.

    Args:
        caminho: Caminho ou nome do arquivo a verificar.

    Raises:
        FormatoNaoSuportado: Quando a extensão não consta em
            EXTENSOES_SUPORTADAS.
    """
    arquivo = Path(caminho)
    extensao = arquivo.suffix.lower()

    if extensao not in EXTENSOES_SUPORTADAS:
        raise FormatoNaoSuportado(
            f"Extensão {extensao!r} não é aceita pelo acervo. "
            f"Formatos válidos: {EXTENSOES_SUPORTADAS}."
        )


def criar_arquivo(caminho: str | Path, conteudo: str = "") -> Path:
    """Cria um arquivo de texto no caminho indicado.

    A função não cria diretórios intermediários. O diretório que recebe o
    arquivo precisa existir antes da chamada. Para criar diretórios use
    `biblioteca.diretorios.criar_diretorio`.

    Args:
        caminho: Local onde o arquivo será criado.
        conteudo: Texto inicial. Em branco por padrão.

    Returns:
        Objeto Path do arquivo recém-criado.

    Raises:
        FormatoNaoSuportado: Quando a extensão do arquivo não é aceita.
        DocumentoJaExiste: Quando já existe um arquivo no caminho.
        DiretorioNaoEncontrado: Propagada do sistema operacional quando o
            diretório pai não existe.
    """
    arquivo = Path(caminho)

    validar_extensao(arquivo)

    if arquivo.exists():
        raise DocumentoJaExiste(
            f"Já existe arquivo em {str(arquivo)!r}."
        )

    arquivo.write_text(conteudo, encoding=CODIFICACAO_PADRAO)
    return arquivo


def ler_arquivo(caminho: str | Path) -> str:
    """Lê e retorna o conteúdo textual de um arquivo.

    A chamada combina abertura, leitura e fechamento em uma operação
    atômica. Cobre simultaneamente as operações de abrir e ler exigidas
    pelo Critério 1.

    Args:
        caminho: Caminho do arquivo a ser lido.

    Returns:
        Conteúdo do arquivo decodificado como string UTF-8.

    Raises:
        DocumentoNaoEncontrado: Quando o arquivo não existe ou o caminho
            aponta para um diretório.
    """
    arquivo = Path(caminho)

    if not arquivo.is_file():
        raise DocumentoNaoEncontrado(
            f"Arquivo {str(arquivo)!r} não encontrado."
        )

    return arquivo.read_text(encoding=CODIFICACAO_PADRAO)


def renomear_arquivo(caminho_atual: str | Path, novo_nome: str) -> Path:
    """Renomeia um arquivo preservando o diretório original.

    O parâmetro `novo_nome` deve conter apenas o nome do arquivo, sem
    componentes de caminho. A função preserva o diretório de origem e
    move o arquivo apenas dentro dele.

    Args:
        caminho_atual: Caminho do arquivo a ser renomeado.
        novo_nome: Novo nome do arquivo, incluindo a extensão.

    Returns:
        Objeto Path do arquivo após a renomeação.

    Raises:
        DocumentoNaoEncontrado: Quando o arquivo original não existe.
        DocumentoJaExiste: Quando já existe arquivo com o novo nome no
            mesmo diretório.
        FormatoNaoSuportado: Quando o novo nome usa extensão fora da
            lista de formatos suportados.
    """
    origem = Path(caminho_atual)

    if not origem.is_file():
        raise DocumentoNaoEncontrado(
            f"Arquivo {str(origem)!r} não encontrado."
        )

    validar_extensao(novo_nome)
    destino = origem.with_name(novo_nome)

    if destino.exists():
        raise DocumentoJaExiste(
            f"Já existe arquivo em {str(destino)!r}."
        )

    return origem.rename(destino)


def remover_arquivo(caminho: str | Path) -> None:
    """Remove permanentemente um arquivo do sistema de arquivos.

    Args:
        caminho: Caminho do arquivo a ser removido.

    Raises:
        DocumentoNaoEncontrado: Quando o arquivo não existe ou o caminho
            aponta para um diretório.
    """
    arquivo = Path(caminho)

    if not arquivo.is_file():
        raise DocumentoNaoEncontrado(
            f"Arquivo {str(arquivo)!r} não encontrado."
        )

    arquivo.unlink()
