from __future__ import annotations

from collections import defaultdict
from decimal import Decimal
from typing import Any, Iterable, Mapping

from .util import decimal_ou_none, parse_timestamp


CATEGORIAS_QUALIDADE = (
    "ACERTO",
    "FALSO_POSITIVO",
    "FALSO_NEGATIVO",
    "ACERTO_NEGATIVO",
    "OPORTUNIDADE_PERDIDA",
    "NAO_AVALIAVEL",
)


def _resultado_positivo(experiencia: Mapping[str, Any]) -> bool | None:
    resultado = experiencia.get("resultado", {})
    if not isinstance(resultado, Mapping):
        return None
    mfe = decimal_ou_none(resultado.get("mfe_pontos"))
    mae = decimal_ou_none(resultado.get("mae_pontos"))
    if mfe is None or mae is None:
        return None
    return mfe > mae


def classificar_qualidade_hipotese(
    experiencia: Mapping[str, Any],
) -> str:
    hipotese = experiencia.get("hipotese", {})
    if not isinstance(hipotese, Mapping):
        return "NAO_AVALIAVEL"
    direcao = hipotese.get("direcao")
    origem_direcao = hipotese.get("origem_direcao")
    positivo = _resultado_positivo(experiencia)
    if positivo is None:
        return "NAO_AVALIAVEL"
    if direcao in ("COMPRA", "VENDA"):
        return "ACERTO" if positivo else "FALSO_POSITIVO"
    if origem_direcao == "HIPOTESE_NEGATIVA_EXPLICITA":
        return "FALSO_NEGATIVO" if positivo else "ACERTO_NEGATIVO"
    if origem_direcao == "ABSTENCAO_DELIBERADA":
        return "OPORTUNIDADE_PERDIDA" if positivo else "ACERTO_NEGATIVO"
    return "NAO_AVALIAVEL"


def metricas_qualidade(
    evidencias: Iterable[dict[str, Any]],
) -> dict[str, Any]:
    grupos: dict[str, list[str]] = {categoria: [] for categoria in CATEGORIAS_QUALIDADE}
    for evidencia in evidencias:
        categoria = str(evidencia["qualidade_hipotese"])
        grupos[categoria].append(str(evidencia["experiencia_id"]))
    return {
        "regra": "MATRIZ_QUALIDADE_HIPOTESE_REPLAY_V1",
        **{
            categoria: {
                "quantidade": len(grupos[categoria]),
                "ids": grupos[categoria],
            }
            for categoria in CATEGORIAS_QUALIDADE
        },
    }


def _resumo_estrato(
    chave: str,
    evidencias: list[dict[str, Any]],
) -> dict[str, Any]:
    categorias = defaultdict(int)
    for evidencia in evidencias:
        categorias[evidencia["qualidade_hipotese"]] += 1
    return {
        "chave": chave,
        "quantidade": len(evidencias),
        "ids_experiencias": [e["experiencia_id"] for e in evidencias],
        "acertos": categorias["ACERTO"],
        "falsos_positivos": categorias["FALSO_POSITIVO"],
        "falsos_negativos": categorias["FALSO_NEGATIVO"],
        "oportunidades_perdidas": categorias["OPORTUNIDADE_PERDIDA"],
        "nao_avaliaveis": categorias["NAO_AVALIAVEL"],
    }


def resultados_por_horario(
    evidencias: Iterable[dict[str, Any]],
) -> list[dict[str, Any]]:
    grupos: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for evidencia in evidencias:
        hora = parse_timestamp(
            evidencia["timestamp_referencia"],
            "timestamp_referencia",
        ).hour
        chave = f"{hora:02d}:00-{hora:02d}:59"
        grupos[chave].append(evidencia)
    return [_resumo_estrato(chave, grupos[chave]) for chave in sorted(grupos)]


def _amplitude(experiencia: Mapping[str, Any]) -> Decimal | None:
    fato = experiencia.get("fato", {})
    evento = fato.get("evento", {}) if isinstance(fato, Mapping) else {}
    if not isinstance(evento, Mapping):
        return None
    maximo = decimal_ou_none(evento.get("maximo"))
    minimo = decimal_ou_none(evento.get("minimo"))
    if maximo is None or minimo is None:
        return None
    return maximo - minimo


def _quantil_nearest_rank(valores: list[Decimal], p: Decimal) -> Decimal:
    ordenados = sorted(valores)
    if not ordenados:
        raise ValueError("sem valores")
    posto = int((p * Decimal(len(ordenados))).to_integral_value(rounding="ROUND_CEILING"))
    posto = max(1, min(posto, len(ordenados)))
    return ordenados[posto - 1]


def resultados_por_volatilidade(
    evidencias: Iterable[dict[str, Any]],
) -> list[dict[str, Any]]:
    lista = list(evidencias)
    calibracao = [
        _amplitude(e["experiencia_fonte"])
        for e in lista
        if e["particao"] == "CALIBRACAO"
    ]
    calibracao_validos = [valor for valor in calibracao if valor is not None]
    grupos: dict[str, list[dict[str, Any]]] = defaultdict(list)
    if len(calibracao_validos) < 3:
        for evidencia in lista:
            grupos["NAO_AVALIAVEL"].append(evidencia)
    else:
        q33 = _quantil_nearest_rank(calibracao_validos, Decimal("0.33"))
        q66 = _quantil_nearest_rank(calibracao_validos, Decimal("0.66"))
        for evidencia in lista:
            valor = _amplitude(evidencia["experiencia_fonte"])
            if valor is None:
                chave = "NAO_AVALIAVEL"
            elif valor <= q33:
                chave = "BAIXA"
            elif valor <= q66:
                chave = "MEDIA"
            else:
                chave = "ALTA"
            grupos[chave].append(evidencia)
    ordem = {"BAIXA": 0, "MEDIA": 1, "ALTA": 2, "NAO_AVALIAVEL": 3}
    return [
        _resumo_estrato(chave, grupos[chave])
        for chave in sorted(grupos, key=lambda item: ordem[item])
    ]


def resultados_por_contexto(
    evidencias: Iterable[dict[str, Any]],
) -> list[dict[str, Any]]:
    grupos: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for evidencia in evidencias:
        experiencia = evidencia["experiencia_fonte"]
        contexto = experiencia.get("contexto", {})
        regime = contexto.get("regime") if isinstance(contexto, Mapping) else None
        sessao = contexto.get("sessao", {}) if isinstance(contexto, Mapping) else {}
        sessao_id = sessao.get("sessao_id") if isinstance(sessao, Mapping) else None
        chave = f"regime={regime if regime is not None else 'AUSENTE'}|sessao={sessao_id if sessao_id is not None else 'AUSENTE'}"
        grupos[chave].append(evidencia)
    return [_resumo_estrato(chave, grupos[chave]) for chave in sorted(grupos)]
