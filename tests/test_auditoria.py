"""Testes do módulo `biblioteca.auditoria`.

Cobre a função de cruzamento entre acervo físico e catálogo nos
cenários de acervo íntegro, registros sem arquivo, arquivos sem
registro e combinações dos três. Usa diretórios temporários
isolados pela fixture `tmp_path` do pytest.
"""

import pytest

from biblioteca.auditoria import auditar_acervo
from biblioteca.catalogo import adicionar_documento
from biblioteca.excecoes import DiretorioNaoEncontrado


def _adicionar_documento_completo(
    caminho_catalogo,
    caminho_acervo,
    nome,
    **metadados,
):
    """Cria arquivo físico no acervo e registro correspondente no catálogo.

    Helper de teste que simula o estado consistente esperado: arquivo
    presente no disco com cadastro correspondente no catálogo.
    """
    (caminho_acervo / nome).write_text("conteúdo de teste")
    defaults = {"titulo": "Título", "autor": "Autor", "ano": 2020}
    defaults.update(metadados)
    adicionar_documento(
        caminho_catalogo, nome_arquivo=nome, **defaults
    )


def test_auditar_acervo_devolve_categorias_vazias_quando_tudo_vazio(tmp_path):
    acervo = tmp_path / "acervo"
    acervo.mkdir()
    catalogo = tmp_path / "catalogo.json"

    resultado = auditar_acervo(acervo, catalogo)

    assert resultado["integros"] == []
    assert resultado["nao_encontrados"] == []
    assert resultado["nao_catalogados"] == []


def test_auditar_acervo_classifica_documentos_integros(tmp_path):
    acervo = tmp_path / "acervo"
    acervo.mkdir()
    catalogo = tmp_path / "catalogo.json"
    _adicionar_documento_completo(catalogo, acervo, "livro_a.txt")
    _adicionar_documento_completo(catalogo, acervo, "livro_b.pdf")

    resultado = auditar_acervo(acervo, catalogo)

    nomes = sorted(r["nome_arquivo"] for r in resultado["integros"])
    assert nomes == ["livro_a.txt", "livro_b.pdf"]
    assert resultado["nao_encontrados"] == []
    assert resultado["nao_catalogados"] == []


def test_auditar_acervo_identifica_registro_sem_arquivo(tmp_path):
    acervo = tmp_path / "acervo"
    acervo.mkdir()
    catalogo = tmp_path / "catalogo.json"
    adicionar_documento(
        catalogo, nome_arquivo="fantasma.pdf",
        titulo="t", autor="a", ano=2020,
    )

    resultado = auditar_acervo(acervo, catalogo)

    assert resultado["integros"] == []
    assert len(resultado["nao_encontrados"]) == 1
    assert resultado["nao_encontrados"][0]["nome_arquivo"] == "fantasma.pdf"
    assert resultado["nao_catalogados"] == []


def test_auditar_acervo_identifica_arquivo_sem_registro(tmp_path):
    acervo = tmp_path / "acervo"
    acervo.mkdir()
    catalogo = tmp_path / "catalogo.json"
    (acervo / "orfao.txt").write_text("")

    resultado = auditar_acervo(acervo, catalogo)

    assert resultado["integros"] == []
    assert resultado["nao_encontrados"] == []
    assert resultado["nao_catalogados"] == [acervo / "orfao.txt"]


def test_auditar_acervo_combina_as_tres_categorias(tmp_path):
    acervo = tmp_path / "acervo"
    acervo.mkdir()
    catalogo = tmp_path / "catalogo.json"
    _adicionar_documento_completo(catalogo, acervo, "integro.pdf")
    adicionar_documento(
        catalogo, nome_arquivo="ausente.pdf",
        titulo="t", autor="a", ano=2020,
    )
    (acervo / "orfao.epub").write_text("")

    resultado = auditar_acervo(acervo, catalogo)

    assert len(resultado["integros"]) == 1
    assert len(resultado["nao_encontrados"]) == 1
    assert len(resultado["nao_catalogados"]) == 1


def test_auditar_acervo_ignora_arquivos_com_extensao_fora_da_lista(tmp_path):
    acervo = tmp_path / "acervo"
    acervo.mkdir()
    catalogo = tmp_path / "catalogo.json"
    (acervo / "catalogo.json").write_text("{}")
    (acervo / ".DS_Store").write_text("")
    (acervo / "compactado.zip").write_text("")

    resultado = auditar_acervo(acervo, catalogo)

    assert resultado["nao_catalogados"] == []


def test_auditar_acervo_falha_quando_pasta_inexistente(tmp_path):
    acervo = tmp_path / "ausente"
    catalogo = tmp_path / "catalogo.json"

    with pytest.raises(DiretorioNaoEncontrado):
        auditar_acervo(acervo, catalogo)
