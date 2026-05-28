"""Testes do módulo `biblioteca.arquivos`.

Cobre as funções de manipulação de arquivos individuais com casos
felizes e cenários de erro, cada um isolado em um diretório temporário
criado pela fixture `tmp_path` do pytest.
"""

import pytest

from biblioteca.arquivos import (
    EXTENSOES_SUPORTADAS,
    criar_arquivo,
    ler_arquivo,
    remover_arquivo,
    renomear_arquivo,
    validar_extensao,
)
from biblioteca.excecoes import (
    DocumentoJaExiste,
    DocumentoNaoEncontrado,
    FormatoNaoSuportado,
)


@pytest.mark.parametrize("extensao", EXTENSOES_SUPORTADAS)
def test_validar_extensao_aceita_formatos_da_lista(extensao):
    validar_extensao(f"arquivo{extensao}")


def test_validar_extensao_rejeita_extensao_fora_da_lista():
    with pytest.raises(FormatoNaoSuportado):
        validar_extensao("arquivo.zip")


def test_validar_extensao_aceita_extensao_em_caixa_alta():
    validar_extensao("ARQUIVO.PDF")


def test_criar_arquivo_cria_arquivo_vazio_no_caminho_indicado(tmp_path):
    arquivo = tmp_path / "novo.txt"

    resultado = criar_arquivo(arquivo)

    assert resultado == arquivo
    assert arquivo.is_file()
    assert arquivo.read_text() == ""


def test_criar_arquivo_grava_conteudo_textual(tmp_path):
    arquivo = tmp_path / "novo.txt"

    criar_arquivo(arquivo, conteudo="conteúdo de teste")

    assert arquivo.read_text() == "conteúdo de teste"


def test_criar_arquivo_preserva_caracteres_acentuados(tmp_path):
    arquivo = tmp_path / "novo.txt"

    criar_arquivo(arquivo, conteudo="ação, decisão, gestão")

    assert arquivo.read_text() == "ação, decisão, gestão"


def test_criar_arquivo_rejeita_extensao_nao_suportada(tmp_path):
    with pytest.raises(FormatoNaoSuportado):
        criar_arquivo(tmp_path / "novo.zip")


def test_criar_arquivo_rejeita_caminho_ja_ocupado(tmp_path):
    arquivo = tmp_path / "existente.txt"
    arquivo.write_text("já existe")

    with pytest.raises(DocumentoJaExiste):
        criar_arquivo(arquivo)


def test_ler_arquivo_devolve_conteudo_textual(tmp_path):
    arquivo = tmp_path / "doc.txt"
    arquivo.write_text("texto de teste")

    assert ler_arquivo(arquivo) == "texto de teste"


def test_ler_arquivo_preserva_acentos(tmp_path):
    arquivo = tmp_path / "doc.txt"
    arquivo.write_text("texto com acentuação")

    assert ler_arquivo(arquivo) == "texto com acentuação"


def test_ler_arquivo_falha_quando_arquivo_inexistente(tmp_path):
    with pytest.raises(DocumentoNaoEncontrado):
        ler_arquivo(tmp_path / "ausente.txt")


def test_ler_arquivo_falha_quando_caminho_eh_diretorio(tmp_path):
    with pytest.raises(DocumentoNaoEncontrado):
        ler_arquivo(tmp_path)


def test_renomear_arquivo_preserva_diretorio_original(tmp_path):
    origem = tmp_path / "original.txt"
    origem.write_text("conteúdo")

    destino = renomear_arquivo(origem, "novo.txt")

    assert destino == tmp_path / "novo.txt"
    assert destino.is_file()
    assert not origem.exists()


def test_renomear_arquivo_falha_quando_origem_inexistente(tmp_path):
    with pytest.raises(DocumentoNaoEncontrado):
        renomear_arquivo(tmp_path / "ausente.txt", "novo.txt")


def test_renomear_arquivo_falha_quando_destino_ocupado(tmp_path):
    origem = tmp_path / "original.txt"
    origem.write_text("a")
    (tmp_path / "destino.txt").write_text("b")

    with pytest.raises(DocumentoJaExiste):
        renomear_arquivo(origem, "destino.txt")


def test_renomear_arquivo_rejeita_extensao_invalida(tmp_path):
    origem = tmp_path / "original.txt"
    origem.write_text("a")

    with pytest.raises(FormatoNaoSuportado):
        renomear_arquivo(origem, "destino.zip")


def test_remover_arquivo_apaga_o_arquivo(tmp_path):
    arquivo = tmp_path / "doc.txt"
    arquivo.write_text("conteúdo")

    remover_arquivo(arquivo)

    assert not arquivo.exists()


def test_remover_arquivo_falha_quando_ausente(tmp_path):
    with pytest.raises(DocumentoNaoEncontrado):
        remover_arquivo(tmp_path / "ausente.txt")


def test_remover_arquivo_falha_quando_caminho_eh_diretorio(tmp_path):
    with pytest.raises(DocumentoNaoEncontrado):
        remover_arquivo(tmp_path)
