"""Ponto de entrada conveniente para execução direta do sistema.

Permite executar a CLI sem instalar o pacote, ajustando dinamicamente
o `sys.path` para incluir o diretório `src/`. Uso esperado:

    python3 run.py listar
    python3 run.py adicionar
    python3 run.py --help

A alternativa profissional é instalar o pacote em modo editável com
`pip install -e .` por meio de um `pyproject.toml`. Optou-se por este
wrapper para evitar o passo de instalação durante a avaliação
acadêmica.
"""

import sys
from pathlib import Path


_RAIZ_SRC = Path(__file__).resolve().parent / "src"
sys.path.insert(0, str(_RAIZ_SRC))

from biblioteca.cli import main  # noqa: E402  (import após sys.path)


if __name__ == "__main__":
    sys.exit(main())
