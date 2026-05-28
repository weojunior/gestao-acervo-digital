"""Permite executar o pacote com `python3 -m biblioteca`.

Encaminha a execução para `biblioteca.cli.main` e propaga o código de
saída devolvido por ela ao processo.
"""

import sys

from .cli import main


if __name__ == "__main__":
    sys.exit(main())
