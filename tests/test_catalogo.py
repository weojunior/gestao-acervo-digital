"""Testes do módulo `biblioteca.catalogo`.

Cobre o CRUD do catálogo, a validação de metadados e a persistência
em JSON, com cenários felizes e de erro. Cada teste usa um arquivo
de catálogo isolado em diretório temporário criado pela fixture
`tmp_path` do pytest.
"""

import json

import pytest

from biblioteca.catalogo import (
    adicionar_documento,
    buscar_documento,
    carregar_catalogo,
    listar_documentos,
    remover_documento,
    renomear_documento,
    salvar_catalogo,
)
from biblioteca.excecoes import (
    CatalogoCorrompido,
    DocumentoJaExiste,
    DocumentoNaoEncontrado,
    FormatoNaoSuportado,
    MetadadoInvalido,
)


def test_carregar_catalogo_retorna_estrutura_vazia_quando_arquivo_inexistente(
    tmp_path,
):
    caminho = tmp_path / "catalogo.json"

    catalogo = carregar_catalogo(caminho)

    assert catalogo == {"versao": "1.0", "documentos": []}
    assert not caminho.exists()


def test_carregar_catalogo_le_arquivo_existente(tmp_path):
    caminho = tmp_path / "catalogo.json"
    salvar_catalogo(
        caminho,
        {"versao": "1.0", "documentos": [{"campo": "valor"}]},
    )

    catalogo = carregar_catalogo(caminho)

    assert catalogo == {"versao": "1.0", "documentos": [{"campo": "valor"}]}


def test_carregar_catalogo_falha_quando_json_corrompido(tmp_path):
    caminho = tmp_path / "catalogo.json"
    caminho.write_text("{ json invalido", encoding="utf-8")

    with pytest.raises(CatalogoCorrompido):
        carregar_catalogo(caminho)


def test_salvar_catalogo_preserva_acentos(tmp_path):
    caminho = tmp_path / "catalogo.json"
    catalogo = {
        "versao": "1.0",
        "documentos": [
            {"nome_arquivo": "ação.pdf", "titulo": "Decisão"}
        ],
    }

    salvar_catalogo(caminho, catalogo)
    conteudo = caminho.read_text(encoding="utf-8")

    assert "ação.pdf" in conteudo
    assert "Decisão" in conteudo


def test_salvar_catalogo_grava_json_legivel_com_quebras_de_linha(tmp_path):
    caminho = tmp_path / "catalogo.json"

    salvar_catalogo(caminho, {"versao": "1.0", "documentos": []})

    conteudo = caminho.read_text(encoding="utf-8")
    assert "\n" in conteudo


def test_adicionar_documento_cria_registro_completo(tmp_path):
    caminho = tmp_path / "catalogo.json"

    registro = adicionar_documento(
        caminho,
        nome_arquivo="livro.pdf",
        titulo="Estatística Bayesiana",
        autor="Andrew Gelman",
        ano=2013,
    )

    assert registro["nome_arquivo"] == "livro.pdf"
    assert registro["titulo"] == "Estatística Bayesiana"
    assert registro["autor"] == "Andrew Gelman"
    assert registro["ano"] == 2013
    assert registro["tipo"] == "PDF"


def test_adicionar_documento_persiste_no_disco(tmp_path):
    caminho = tmp_path / "catalogo.json"

    adicionar_documento(
        caminho,
        nome_arquivo="livro.pdf",
        titulo="Título",
        autor="Autor",
        ano=2020,
    )

    catalogo = json.loads(caminho.read_text(encoding="utf-8"))
    assert len(catalogo["documentos"]) == 1


def test_adicionar_documento_aplica_strip_em_titulo_e_autor(tmp_path):
    caminho = tmp_path / "catalogo.json"

    registro = adicionar_documento(
        caminho,
        nome_arquivo="livro.pdf",
        titulo="  Título com espaços  ",
        autor="  Autor  ",
        ano=2020,
    )

    assert registro["titulo"] == "Título com espaços"
    assert registro["autor"] == "Autor"


def test_adicionar_documento_recusa_extensao_invalida(tmp_path):
    caminho = tmp_path / "catalogo.json"

    with pytest.raises(FormatoNaoSuportado):
        adicionar_documento(
            caminho,
            nome_arquivo="livro.zip",
            titulo="x",
            autor="y",
            ano=2020,
        )


def test_adicionar_documento_recusa_titulo_em_branco(tmp_path):
    caminho = tmp_path / "catalogo.json"

    with pytest.raises(MetadadoInvalido):
        adicionar_documento(
            caminho,
            nome_arquivo="livro.pdf",
            titulo="   ",
            autor="autor",
            ano=2020,
        )


def test_adicionar_documento_recusa_autor_em_branco(tmp_path):
    caminho = tmp_path / "catalogo.json"

    with pytest.raises(MetadadoInvalido):
        adicionar_documento(
            caminho,
            nome_arquivo="livro.pdf",
            titulo="titulo",
            autor="",
            ano=2020,
        )


def test_adicionar_documento_recusa_ano_nao_inteiro(tmp_path):
    caminho = tmp_path / "catalogo.json"

    with pytest.raises(MetadadoInvalido):
        adicionar_documento(
            caminho,
            nome_arquivo="livro.pdf",
            titulo="x",
            autor="y",
            ano="2020",
        )


def test_adicionar_documento_recusa_ano_booleano(tmp_path):
    caminho = tmp_path / "catalogo.json"

    with pytest.raises(MetadadoInvalido):
        adicionar_documento(
            caminho,
            nome_arquivo="livro.pdf",
            titulo="x",
            autor="y",
            ano=True,
        )


def test_adicionar_documento_recusa_ano_anterior_a_1450(tmp_path):
    caminho = tmp_path / "catalogo.json"

    with pytest.raises(MetadadoInvalido):
        adicionar_documento(
            caminho,
            nome_arquivo="livro.pdf",
            titulo="x",
            autor="y",
            ano=1400,
        )


def test_adicionar_documento_recusa_duplicata(tmp_path):
    caminho = tmp_path / "catalogo.json"
    adicionar_documento(
        caminho, nome_arquivo="livro.pdf",
        titulo="t1", autor="a1", ano=2020,
    )

    with pytest.raises(DocumentoJaExiste):
        adicionar_documento(
            caminho, nome_arquivo="livro.pdf",
            titulo="t2", autor="a2", ano=2021,
        )


def test_adicionar_documento_deriva_tipo_da_extensao(tmp_path):
    caminho = tmp_path / "catalogo.json"

    registro_pdf = adicionar_documento(
        caminho, nome_arquivo="a.pdf",
        titulo="t", autor="a", ano=2020,
    )
    registro_epub = adicionar_documento(
        caminho, nome_arquivo="b.epub",
        titulo="t", autor="a", ano=2020,
    )

    assert registro_pdf["tipo"] == "PDF"
    assert registro_epub["tipo"] == "EPUB"


def test_remover_documento_retira_do_catalogo_e_retorna_o_registro(tmp_path):
    caminho = tmp_path / "catalogo.json"
    adicionar_documento(
        caminho, nome_arquivo="livro.pdf",
        titulo="t", autor="a", ano=2020,
    )

    removido = remover_documento(caminho, "livro.pdf")

    assert removido["nome_arquivo"] == "livro.pdf"
    assert listar_documentos(caminho) == []


def test_remover_documento_falha_quando_nao_encontrado(tmp_path):
    caminho = tmp_path / "catalogo.json"

    with pytest.raises(DocumentoNaoEncontrado):
        remover_documento(caminho, "ausente.pdf")


def test_buscar_documento_encontra_registro_existente(tmp_path):
    caminho = tmp_path / "catalogo.json"
    adicionar_documento(
        caminho, nome_arquivo="livro.pdf",
        titulo="Título", autor="Autor", ano=2020,
    )

    registro = buscar_documento(caminho, "livro.pdf")

    assert registro["titulo"] == "Título"
    assert registro["ano"] == 2020


def test_buscar_documento_falha_quando_nao_encontrado(tmp_path):
    caminho = tmp_path / "catalogo.json"

    with pytest.raises(DocumentoNaoEncontrado):
        buscar_documento(caminho, "ausente.pdf")


def test_listar_documentos_devolve_vazio_para_catalogo_vazio(tmp_path):
    caminho = tmp_path / "catalogo.json"
    assert listar_documentos(caminho) == []


def test_listar_documentos_preserva_ordem_de_insercao(tmp_path):
    caminho = tmp_path / "catalogo.json"
    adicionar_documento(
        caminho, nome_arquivo="b.pdf",
        titulo="B", autor="a", ano=2020,
    )
    adicionar_documento(
        caminho, nome_arquivo="a.pdf",
        titulo="A", autor="a", ano=2020,
    )

    registros = listar_documentos(caminho)

    assert [r["nome_arquivo"] for r in registros] == ["b.pdf", "a.pdf"]


def test_renomear_documento_atualiza_nome_e_preserva_metadados(tmp_path):
    caminho = tmp_path / "catalogo.json"
    adicionar_documento(
        caminho, nome_arquivo="velho.pdf",
        titulo="Título", autor="Autor", ano=2020,
    )

    registro = renomear_documento(caminho, "velho.pdf", "novo.pdf")

    assert registro["nome_arquivo"] == "novo.pdf"
    assert registro["titulo"] == "Título"
    assert registro["autor"] == "Autor"
    assert registro["ano"] == 2020


def test_renomear_documento_recalcula_tipo_quando_extensao_muda(tmp_path):
    caminho = tmp_path / "catalogo.json"
    adicionar_documento(
        caminho, nome_arquivo="velho.pdf",
        titulo="t", autor="a", ano=2020,
    )

    registro = renomear_documento(caminho, "velho.pdf", "novo.epub")

    assert registro["tipo"] == "EPUB"


def test_renomear_documento_falha_quando_nome_atual_inexistente(tmp_path):
    caminho = tmp_path / "catalogo.json"

    with pytest.raises(DocumentoNaoEncontrado):
        renomear_documento(caminho, "ausente.pdf", "novo.pdf")


def test_renomear_documento_falha_quando_novo_nome_ocupado(tmp_path):
    caminho = tmp_path / "catalogo.json"
    adicionar_documento(
        caminho, nome_arquivo="a.pdf",
        titulo="t", autor="a", ano=2020,
    )
    adicionar_documento(
        caminho, nome_arquivo="b.pdf",
        titulo="t", autor="a", ano=2020,
    )

    with pytest.raises(DocumentoJaExiste):
        renomear_documento(caminho, "a.pdf", "b.pdf")


def test_renomear_documento_rejeita_extensao_invalida(tmp_path):
    caminho = tmp_path / "catalogo.json"
    adicionar_documento(
        caminho, nome_arquivo="livro.pdf",
        titulo="t", autor="a", ano=2020,
    )

    with pytest.raises(FormatoNaoSuportado):
        renomear_documento(caminho, "livro.pdf", "livro.zip")
