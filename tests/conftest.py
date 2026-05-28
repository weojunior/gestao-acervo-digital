"""Configurações compartilhadas dos testes do pytest.

O arquivo é descoberto automaticamente pelo pytest antes da coleta
dos testes. Insere `src/` no `sys.path` para tornar o pacote
`biblioteca` importável sem necessidade de instalar o projeto via
pip. Replica em ambiente de teste a mesma manipulação de path feita
por `run.py` em ambiente de produção.
"""

import sys
from pathlib import Path


_RAIZ_SRC = Path(__file__).resolve().parent.parent / "src"
sys.path.insert(0, str(_RAIZ_SRC))
