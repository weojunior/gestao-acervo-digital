"""Testes do módulo `biblioteca.diretorios`.

Cobre as funções de gerenciamento de diretórios em casos felizes e
em cenários de erro, com diretórios temporários isolados pela fixture
`tmp_path` do pytest.
"""

import pytest

from biblioteca.diretorios import (
    criar_diretorio,
    listar_diretorio,
    remover_diretorio,
)
from biblioteca.excecoes import (
    DiretorioJaExiste,
    DiretorioNaoEncontrado,
    DiretorioNaoVazio,
)


def test_criar_diretorio_cria_no_caminho_indicado(tmp_path):
    novo = tmp_path / "subpasta"

    resultado = criar_diretorio(novo)

    assert resultado == novo
    assert novo.is_dir()


def test_criar_diretorio_falha_quando_caminho_ja_existe(tmp_path):
    novo = tmp_path / "subpasta"
    novo.mkdir()

    with pytest.raises(DiretorioJaExiste):
        criar_diretorio(novo)


def test_criar_diretorio_falha_quando_pai_ausente_e_sem_criar_pais(tmp_path):
    profundo = tmp_path / "ainda_nao_existe" / "filho"

    with pytest.raises(DiretorioNaoEncontrado):
        criar_diretorio(profundo, criar_pais=False)


def test_criar_diretorio_cria_hierarquia_com_criar_pais(tmp_path):
    profundo = tmp_path / "a" / "b" / "c"

    criar_diretorio(profundo, criar_pais=True)

    assert profundo.is_dir()


def test_listar_diretorio_retorna_lista_vazia_para_pasta_vazia(tmp_path):
    assert listar_diretorio(tmp_path) == []


def test_listar_diretorio_retorna_arquivos_em_ordem_alfabetica(tmp_path):
    (tmp_path / "b.txt").write_text("")
    (tmp_path / "a.txt").write_text("")
    (tmp_path / "c.txt").write_text("")

    resultado = listar_diretorio(tmp_path)

    assert [p.name for p in resultado] == ["a.txt", "b.txt", "c.txt"]


def test_listar_diretorio_inclui_subpastas_no_modo_recursivo(tmp_path):
    sub = tmp_path / "subpasta"
    sub.mkdir()
    (sub / "interno.txt").write_text("")

    resultado = listar_diretorio(tmp_path, recursivo=True)
    nomes = sorted(p.name for p in resultado)

    assert "subpasta" in nomes
    assert "interno.txt" in nomes


def test_listar_diretorio_nao_recursivo_ignora_conteudo_de_subpasta(tmp_path):
    sub = tmp_path / "subpasta"
    sub.mkdir()
    (sub / "interno.txt").write_text("")

    resultado = listar_diretorio(tmp_path, recursivo=False)

    assert [p.name for p in resultado] == ["subpasta"]


def test_listar_diretorio_falha_quando_pasta_inexistente(tmp_path):
    with pytest.raises(DiretorioNaoEncontrado):
        listar_diretorio(tmp_path / "ausente")


def test_listar_diretorio_falha_quando_caminho_eh_arquivo(tmp_path):
    arquivo = tmp_path / "doc.txt"
    arquivo.write_text("")

    with pytest.raises(DiretorioNaoEncontrado):
        listar_diretorio(arquivo)


def test_remover_diretorio_apaga_pasta_vazia(tmp_path):
    pasta = tmp_path / "vazia"
    pasta.mkdir()

    remover_diretorio(pasta)

    assert not pasta.exists()


def test_remover_diretorio_falha_em_pasta_com_conteudo(tmp_path):
    pasta = tmp_path / "ocupada"
    pasta.mkdir()
    (pasta / "doc.txt").write_text("")

    with pytest.raises(DiretorioNaoVazio):
        remover_diretorio(pasta)


def test_remover_diretorio_recursivo_remove_em_cascata(tmp_path):
    pasta = tmp_path / "ocupada"
    pasta.mkdir()
    (pasta / "doc.txt").write_text("")
    (pasta / "subpasta").mkdir()
    (pasta / "subpasta" / "outro.txt").write_text("")

    remover_diretorio(pasta, recursivo=True)

    assert not pasta.exists()


def test_remover_diretorio_falha_quando_pasta_inexistente(tmp_path):
    with pytest.raises(DiretorioNaoEncontrado):
        remover_diretorio(tmp_path / "ausente")
