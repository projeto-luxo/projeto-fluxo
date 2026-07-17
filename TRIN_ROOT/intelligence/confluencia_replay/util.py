from __future__ import annotations

import copy
from datetime import datetime
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from typing import Any, Iterable, Mapping, Sequence

from .erros import FalhaConfluenciaReplay

CAMPOS_FIXOS = (
    "fato.evento.ativo",
    "contexto.regime",
    "contexto.sessao.sessao_id",
)


def copia_profunda(valor: Any) -> Any:
    return copy.deepcopy(valor)


def obter_caminho(documento: Mapping[str, Any], caminho: str) -> tuple[bool, Any]:
    atual: Any = documento
    for parte in caminho.split("."):
        if not isinstance(atual, Mapping) or parte not in atual:
            return False, None
        atual = atual[parte]
    return True, atual


def parse_timestamp(valor: Any, campo: str) -> datetime:
    if not isinstance(valor, str) or not valor.strip():
        raise FalhaConfluenciaReplay("TIMESTAMP_INVALIDO", campo)
    texto = valor.strip()
    if texto.endswith("Z"):
        texto = texto[:-1] + "+00:00"
    try:
        resultado = datetime.fromisoformat(texto)
    except ValueError as exc:
        raise FalhaConfluenciaReplay("TIMESTAMP_INVALIDO", campo) from exc
    if resultado.tzinfo is None:
        raise FalhaConfluenciaReplay("TIMESTAMP_SEM_TIMEZONE", campo)
    return resultado


def decimal_ou_none(valor: Any) -> Decimal | None:
    if valor is None:
        return None
    try:
        resultado = Decimal(str(valor))
    except (InvalidOperation, ValueError, TypeError):
        return None
    if not resultado.is_finite():
        return None
    return resultado


def duas_casas(valor: Decimal | None) -> str | None:
    if valor is None:
        return None
    return f"{valor.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP):.2f}"


def unicos_preservando_ordem(valores: Iterable[str]) -> list[str]:
    vistos: set[str] = set()
    saida: list[str] = []
    for valor in valores:
        if valor not in vistos:
            vistos.add(valor)
            saida.append(valor)
    return saida


def garantir_lista_strings_unicas(
    valores: Any,
    campo: str,
) -> list[str]:
    if not isinstance(valores, list):
        raise FalhaConfluenciaReplay("LISTA_INVALIDA", campo)
    saida: list[str] = []
    for valor in valores:
        if not isinstance(valor, str) or not valor:
            raise FalhaConfluenciaReplay("ITEM_LISTA_INVALIDO", campo)
        saida.append(valor)
    if len(saida) != len(set(saida)):
        raise FalhaConfluenciaReplay("LISTA_COM_DUPLICIDADE", campo)
    return saida
