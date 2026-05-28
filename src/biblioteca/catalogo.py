"""Persistência e gestão do catálogo de metadados do acervo digital.

Armazena os metadados dos documentos em um arquivo JSON único, por
convenção `acervo/catalogo.json`. Expõe operações para carregar, salvar,
adicionar, remover, buscar e listar registros. As operações de escrita
validam metadados antes de persistir e rejeitam duplicatas pelo nome
do arquivo.

Esquema do registro (cinco campos):
    - nome_arquivo: chave primária, única no catálogo.
    - titulo: título do documento, texto não vazio.
    - autor: autor do documento, texto não vazio.
    - ano: ano de publicação, inteiro entre 1450 e o ano corrente + 1.
    - tipo: rótulo legível do formato, derivado da extensão.

Esquema do arquivo persistido:
    {
        "versao": "1.0",
        "documentos": [ {...registro...}, ... ]
    }

A persistência usa UTF-8 com `ensure_ascii=False` para preservar
caracteres acentuados, e indentação de dois espaços para legibilidade
em inspeção manual.
"""

import json
from datetime import date
from pathlib import Path

from .arquivos import validar_extensao
from .excecoes import (
    CatalogoCorrompido,
    DocumentoJaExiste,
    DocumentoNaoEncontrado,
    MetadadoInvalido,
)


VERSAO_SCHEMA = "1.0"
ANO_MINIMO_ACEITO = 1450

# Mapeamento extensão para rótulo legível usado no campo `tipo` do
# registro. Mantenha alinhado com EXTENSOES_SUPORTADAS do módulo
# `arquivos`. Inconsistências são detectadas pela suíte de testes.
TIPO_POR_EXTENSAO = {
    ".pdf": "PDF",
    ".epub": "EPUB",
    ".txt": "TXT",
    ".md": "MD",
    ".docx": "DOCX",
    ".doc": "DOC",
}


def carregar_catalogo(caminho: str | Path) -> dict:
    """Lê o catálogo JSON do disco e retorna o conteúdo como dicionário.

    Se o arquivo não existir, retorna um catálogo vazio inicializado.
    A função não cria o arquivo no disco; a persistência é
    responsabilidade de `salvar_catalogo`.

    Args:
        caminho: Caminho do arquivo JSON do catálogo.

    Returns:
        Dicionário com as chaves `versao` (str) e `documentos`
        (list[dict]).

    Raises:
        CatalogoCorrompido: Quando o arquivo existe mas o JSON não
            pode ser interpretado.
    """
    arquivo = Path(caminho)

    if not arquivo.exists():
        return {"versao": VERSAO_SCHEMA, "documentos": []}

    conteudo = arquivo.read_text(encoding="utf-8")
    try:
        return json.loads(conteudo)
    except json.JSONDecodeError as erro:
        raise CatalogoCorrompido(
            f"JSON em {str(arquivo)!r} mal formado: {erro.msg} "
            f"(linha {erro.lineno}, coluna {erro.colno})."
        ) from erro


def salvar_catalogo(caminho: str | Path, catalogo: dict) -> None:
    """Persiste o catálogo no disco em formato JSON.

    Args:
        caminho: Caminho do arquivo JSON do catálogo.
        catalogo: Dicionário no formato esperado, com as chaves `versao`
            e `documentos`.
    """
    arquivo = Path(caminho)
    arquivo.write_text(
        json.dumps(catalogo, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def adicionar_documento(
    caminho_catalogo: str | Path,
    nome_arquivo: str,
    titulo: str,
    autor: str,
    ano: int,
) -> dict:
    """Registra um documento no catálogo e persiste a alteração.

    Valida metadados, infere o campo `tipo` a partir da extensão e
    rejeita duplicatas pelo nome do arquivo.

    Args:
        caminho_catalogo: Caminho do arquivo do catálogo.
        nome_arquivo: Nome do arquivo do documento, com extensão.
        titulo: Título do documento.
        autor: Autor do documento.
        ano: Ano de publicação.

    Returns:
        Dicionário do registro recém-adicionado.

    Raises:
        FormatoNaoSuportado: Quando a extensão do arquivo não é aceita.
        MetadadoInvalido: Quando algum campo falha na validação.
        DocumentoJaExiste: Quando já há registro com o mesmo
            `nome_arquivo` no catálogo.
        CatalogoCorrompido: Propagada por `carregar_catalogo`.
    """
    validar_extensao(nome_arquivo)
    _validar_metadados(titulo=titulo, autor=autor, ano=ano)

    catalogo = carregar_catalogo(caminho_catalogo)

    for registro in catalogo["documentos"]:
        if registro["nome_arquivo"] == nome_arquivo:
            raise DocumentoJaExiste(
                f"Já existe documento {nome_arquivo!r} no catálogo."
            )

    novo_registro = {
        "nome_arquivo": nome_arquivo,
        "titulo": titulo.strip(),
        "autor": autor.strip(),
        "ano": ano,
        "tipo": _tipo_de(nome_arquivo),
    }
    catalogo["documentos"].append(novo_registro)
    salvar_catalogo(caminho_catalogo, catalogo)
    return novo_registro


def remover_documento(
    caminho_catalogo: str | Path,
    nome_arquivo: str,
) -> dict:
    """Remove um documento do catálogo e persiste a alteração.

    Args:
        caminho_catalogo: Caminho do arquivo do catálogo.
        nome_arquivo: Nome do arquivo do documento a remover.

    Returns:
        Dicionário do registro removido.

    Raises:
        DocumentoNaoEncontrado: Quando o `nome_arquivo` não consta no
            catálogo.
        CatalogoCorrompido: Propagada por `carregar_catalogo`.
    """
    catalogo = carregar_catalogo(caminho_catalogo)

    for posicao, registro in enumerate(catalogo["documentos"]):
        if registro["nome_arquivo"] == nome_arquivo:
            removido = catalogo["documentos"].pop(posicao)
            salvar_catalogo(caminho_catalogo, catalogo)
            return removido

    raise DocumentoNaoEncontrado(
        f"Documento {nome_arquivo!r} não consta no catálogo."
    )


def buscar_documento(
    caminho_catalogo: str | Path,
    nome_arquivo: str,
) -> dict:
    """Retorna o registro de um documento pelo nome do arquivo.

    Args:
        caminho_catalogo: Caminho do arquivo do catálogo.
        nome_arquivo: Nome do arquivo do documento procurado.

    Returns:
        Dicionário do registro encontrado.

    Raises:
        DocumentoNaoEncontrado: Quando o `nome_arquivo` não consta no
            catálogo.
        CatalogoCorrompido: Propagada por `carregar_catalogo`.
    """
    catalogo = carregar_catalogo(caminho_catalogo)

    for registro in catalogo["documentos"]:
        if registro["nome_arquivo"] == nome_arquivo:
            return registro

    raise DocumentoNaoEncontrado(
        f"Documento {nome_arquivo!r} não consta no catálogo."
    )


def listar_documentos(caminho_catalogo: str | Path) -> list[dict]:
    """Retorna a lista completa de registros do catálogo.

    Args:
        caminho_catalogo: Caminho do arquivo do catálogo.

    Returns:
        Lista de dicionários, um por documento registrado. Ordem
        preservada conforme inserção.

    Raises:
        CatalogoCorrompido: Propagada por `carregar_catalogo`.
    """
    catalogo = carregar_catalogo(caminho_catalogo)
    return list(catalogo["documentos"])


def renomear_documento(
    caminho_catalogo: str | Path,
    nome_atual: str,
    novo_nome: str,
) -> dict:
    """Renomeia um documento no catálogo, preservando os demais metadados.

    Atualiza simultaneamente os campos `nome_arquivo` e `tipo`, sendo
    o segundo recalculado a partir da extensão do novo nome.

    Args:
        caminho_catalogo: Caminho do arquivo do catálogo.
        nome_atual: Nome do arquivo atualmente registrado.
        novo_nome: Novo nome do arquivo, incluindo a extensão.

    Returns:
        Dicionário do registro com os campos atualizados.

    Raises:
        FormatoNaoSuportado: Quando a extensão do `novo_nome` não é
            aceita pelo acervo.
        DocumentoNaoEncontrado: Quando `nome_atual` não consta no
            catálogo.
        DocumentoJaExiste: Quando `novo_nome` já está em uso por outro
            registro.
        CatalogoCorrompido: Propagada por `carregar_catalogo`.
    """
    validar_extensao(novo_nome)
    catalogo = carregar_catalogo(caminho_catalogo)

    indice_atual = None
    for posicao, registro in enumerate(catalogo["documentos"]):
        if registro["nome_arquivo"] == nome_atual:
            indice_atual = posicao
        if (
            registro["nome_arquivo"] == novo_nome
            and registro["nome_arquivo"] != nome_atual
        ):
            raise DocumentoJaExiste(
                f"Já existe documento {novo_nome!r} no catálogo."
            )

    if indice_atual is None:
        raise DocumentoNaoEncontrado(
            f"Documento {nome_atual!r} não consta no catálogo."
        )

    catalogo["documentos"][indice_atual]["nome_arquivo"] = novo_nome
    catalogo["documentos"][indice_atual]["tipo"] = _tipo_de(novo_nome)
    salvar_catalogo(caminho_catalogo, catalogo)
    return catalogo["documentos"][indice_atual]


def _validar_metadados(titulo: str, autor: str, ano: int) -> None:
    """Valida os campos editáveis de um registro.

    Args:
        titulo: Título do documento.
        autor: Autor do documento.
        ano: Ano de publicação.

    Raises:
        MetadadoInvalido: Quando algum campo falha em uma das regras
            de domínio.
    """
    if not isinstance(titulo, str) or not titulo.strip():
        raise MetadadoInvalido("Título não pode estar em branco.")

    if not isinstance(autor, str) or not autor.strip():
        raise MetadadoInvalido("Autor não pode estar em branco.")

    # `bool` é subclasse de `int` em Python. A checagem explícita
    # impede que True ou False passem como ano válido.
    if not isinstance(ano, int) or isinstance(ano, bool):
        raise MetadadoInvalido(
            f"Ano deve ser inteiro, recebido {type(ano).__name__}."
        )

    ano_maximo = date.today().year + 1
    if ano < ANO_MINIMO_ACEITO or ano > ano_maximo:
        raise MetadadoInvalido(
            f"Ano {ano} fora do intervalo aceito "
            f"({ANO_MINIMO_ACEITO} a {ano_maximo})."
        )


def _tipo_de(nome_arquivo: str) -> str:
    """Retorna o rótulo de tipo a partir da extensão do nome do arquivo.

    Args:
        nome_arquivo: Nome do arquivo com extensão.

    Returns:
        Rótulo correspondente em maiúsculas (por exemplo, "PDF", "EPUB").
    """
    extensao = Path(nome_arquivo).suffix.lower()
    return TIPO_POR_EXTENSAO[extensao]
