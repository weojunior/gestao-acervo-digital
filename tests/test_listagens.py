"""Testes do módulo `biblioteca.listagens`.

Cobre as funções de agrupamento por tipo de arquivo e por ano de
publicação em catálogos com diferentes composições, sempre com
arquivos isolados em diretório temporário.
"""

from biblioteca.catalogo import adicionar_documento
from biblioteca.listagens import listar_por_ano, listar_por_tipo


def test_listar_por_tipo_devolve_dict_vazio_para_catalogo_vazio(tmp_path):
    caminho = tmp_path / "catalogo.json"
    assert listar_por_tipo(caminho) == {}


def test_listar_por_tipo_agrupa_registros_pelo_tipo(tmp_path):
    caminho = tmp_path / "catalogo.json"
    adicionar_documento(
        caminho, nome_arquivo="a.pdf",
        titulo="A", autor="x", ano=2020,
    )
    adicionar_documento(
        caminho, nome_arquivo="b.epub",
        titulo="B", autor="x", ano=2020,
    )
    adicionar_documento(
        caminho, nome_arquivo="c.pdf",
        titulo="C", autor="y", ano=2021,
    )

    grupos = listar_por_tipo(caminho)

    assert set(grupos.keys()) == {"PDF", "EPUB"}
    assert len(grupos["PDF"]) == 2
    assert len(grupos["EPUB"]) == 1


def test_listar_por_tipo_retorna_chaves_em_ordem_alfabetica(tmp_path):
    caminho = tmp_path / "catalogo.json"
    adicionar_documento(
        caminho, nome_arquivo="z.txt",
        titulo="z", autor="x", ano=2020,
    )
    adicionar_documento(
        caminho, nome_arquivo="a.pdf",
        titulo="a", autor="x", ano=2020,
    )
    adicionar_documento(
        caminho, nome_arquivo="m.epub",
        titulo="m", autor="x", ano=2020,
    )

    grupos = listar_por_tipo(caminho)

    assert list(grupos.keys()) == ["EPUB", "PDF", "TXT"]


def test_listar_por_ano_devolve_dict_vazio_para_catalogo_vazio(tmp_path):
    caminho = tmp_path / "catalogo.json"
    assert listar_por_ano(caminho) == {}


def test_listar_por_ano_agrupa_registros_pelo_ano(tmp_path):
    caminho = tmp_path / "catalogo.json"
    adicionar_documento(
        caminho, nome_arquivo="a.pdf",
        titulo="a", autor="x", ano=2020,
    )
    adicionar_documento(
        caminho, nome_arquivo="b.pdf",
        titulo="b", autor="x", ano=2020,
    )
    adicionar_documento(
        caminho, nome_arquivo="c.pdf",
        titulo="c", autor="x", ano=2021,
    )

    grupos = listar_por_ano(caminho)

    assert set(grupos.keys()) == {2020, 2021}
    assert len(grupos[2020]) == 2
    assert len(grupos[2021]) == 1


def test_listar_por_ano_retorna_chaves_em_ordem_crescente(tmp_path):
    caminho = tmp_path / "catalogo.json"
    adicionar_documento(
        caminho, nome_arquivo="a.pdf",
        titulo="a", autor="x", ano=2022,
    )
    adicionar_documento(
        caminho, nome_arquivo="b.pdf",
        titulo="b", autor="x", ano=2018,
    )
    adicionar_documento(
        caminho, nome_arquivo="c.pdf",
        titulo="c", autor="x", ano=2020,
    )

    grupos = listar_por_ano(caminho)

    assert list(grupos.keys()) == [2018, 2020, 2022]
