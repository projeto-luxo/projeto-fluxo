"""Caminhos oficiais compartilhados do projeto TRIN.

Responsabilidade única:
- resolver a raiz do repositório;
- resolver a Biblioteca Histórica oficial, irmã do TRIN_ROOT e fora do Git.

Este módulo não cria pastas e não altera arquivos.
"""

from __future__ import annotations

from pathlib import Path

TRIN_ROOT = Path(__file__).resolve().parents[1]
PROJETO_FLUXO = TRIN_ROOT.parent
BIBLIOTECA_HISTORICA = PROJETO_FLUXO / "TRIN_HISTORICO"


def caminho_historico(*partes: str) -> Path:
    """Retorna um caminho interno da Biblioteca Histórica oficial."""

    return BIBLIOTECA_HISTORICA.joinpath(*partes)
