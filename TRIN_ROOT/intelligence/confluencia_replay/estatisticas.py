from __future__ import annotations

from decimal import Decimal
from typing import Any, Iterable

from .util import decimal_ou_none, duas_casas


def _percentil_nearest_rank(valores: list[Decimal], percentual: Decimal) -> Decimal:
    if not valores:
        raise ValueError("lista vazia")
    ordenados = sorted(valores)
    # nearest-rank: ceil(p*n), com índice mínimo 1.
    produto = percentual * Decimal(len(ordenados))
    posto = int(produto.to_integral_value(rounding="ROUND_CEILING"))
    posto = max(1, min(posto, len(ordenados)))
    return ordenados[posto - 1]


def estatisticas_metricas(
    evidencias: Iterable[dict[str, Any]],
    campo: str,
) -> dict[str, Any]:
    pares: list[tuple[str, Decimal]] = []
    excluidos: list[dict[str, str]] = []
    for evidencia in evidencias:
        experiencia_id = str(evidencia["experiencia_id"])
        valor = decimal_ou_none(evidencia.get(campo))
        if valor is None:
            excluidos.append(
                {
                    "experiencia_id": experiencia_id,
                    "motivo": f"{campo.upper()}_AUSENTE_OU_INVALIDO",
                }
            )
        else:
            pares.append((experiencia_id, valor))

    valores = [valor for _, valor in pares]
    ids = [experiencia_id for experiencia_id, _ in pares]
    if not valores:
        return {
            "quantidade": 0,
            "minimo": None,
            "maximo": None,
            "media": None,
            "mediana": None,
            "percentil_25": None,
            "percentil_75": None,
            "ids_incluidos": [],
            "excluidos": excluidos,
            "outliers_removidos": 0,
        }

    ordenados = sorted(valores)
    quantidade = len(ordenados)
    media = sum(ordenados, Decimal("0")) / Decimal(quantidade)
    if quantidade % 2:
        mediana = ordenados[quantidade // 2]
    else:
        mediana = (
            ordenados[quantidade // 2 - 1] + ordenados[quantidade // 2]
        ) / Decimal("2")

    return {
        "quantidade": quantidade,
        "minimo": duas_casas(ordenados[0]),
        "maximo": duas_casas(ordenados[-1]),
        "media": duas_casas(media),
        "mediana": duas_casas(mediana),
        "percentil_25": duas_casas(
            _percentil_nearest_rank(ordenados, Decimal("0.25"))
        ),
        "percentil_75": duas_casas(
            _percentil_nearest_rank(ordenados, Decimal("0.75"))
        ),
        "ids_incluidos": ids,
        "excluidos": excluidos,
        "outliers_removidos": 0,
    }
