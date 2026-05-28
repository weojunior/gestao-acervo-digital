"""Hierarquia de exceções customizadas do pacote biblioteca.

Todas as exceções levantadas por funções deste pacote descendem de
BibliotecaError. Essa convenção permite ao código cliente, em particular
à CLI, capturar a raiz da hierarquia e tratar uniformemente os erros de
domínio sem ocultar exceções de outras origens (KeyboardInterrupt,
MemoryError, etc.).
"""


class BibliotecaError(Exception):
    """Classe-base de todas as exceções do pacote biblioteca."""


class DocumentoNaoEncontrado(BibliotecaError):
    """Documento referenciado não consta no acervo nem no catálogo.

    Aplica-se à ausência do arquivo físico em `acervo/`, à ausência do
    registro correspondente em `acervo/catalogo.json`, ou às duas
    situações simultaneamente.
    """


class DocumentoJaExiste(BibliotecaError):
    """Há tentativa de cadastrar documento com identificador já presente.

    Garante a unicidade dos registros no catálogo e evita sobrescrita
    silenciosa de arquivos existentes no acervo.
    """


class DiretorioNaoEncontrado(BibliotecaError):
    """Diretório indicado como alvo da operação não existe no sistema de arquivos."""


class DiretorioJaExiste(BibliotecaError):
    """Há tentativa de criar diretório em caminho já ocupado por outro diretório."""


class DiretorioNaoVazio(BibliotecaError):
    """Remoção bloqueada porque o diretório ainda contém arquivos.

    A remoção em cascata exige o parâmetro `recursivo=True` na função
    `remover_diretorio`.
    """


class CatalogoCorrompido(BibliotecaError):
    """Arquivo `catalogo.json` não pôde ser interpretado.

    Causas comuns: JSON sintaticamente inválido, ausência de campos
    obrigatórios na raiz do documento, ou tipo de dado incompatível com
    o esquema esperado pelo módulo `catalogo`.
    """


class MetadadoInvalido(BibliotecaError):
    """Campo de metadado não satisfaz as regras de domínio.

    Exemplos: ano fora do intervalo aceito, título em branco, tipo de
    documento fora da lista de formatos suportados pelo acervo.
    """


class FormatoNaoSuportado(BibliotecaError):
    """Extensão do arquivo está fora da lista de formatos aceitos pelo acervo."""
