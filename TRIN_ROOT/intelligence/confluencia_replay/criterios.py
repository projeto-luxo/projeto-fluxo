from __future__ import annotations

from typing import Any, Mapping

from .util import CAMPOS_FIXOS, obter_caminho


def _valor_alvo(consulta: Mapping[str, Any], caminho: str) -> Any:
    mapa = {
        "fato.evento.ativo": "ativo",
        "contexto.regime": "regime",
        "contexto.sessao.sessao_id": "sessao_id",
    }
    return consulta["contexto_alvo"][mapa[caminho]]


def avaliar_criterios(
    experiencia: Mapping[str, Any],
    consulta: Mapping[str, Any],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], str]:
    criterios: list[dict[str, Any]] = []
    concordancias: list[dict[str, Any]] = []
    divergencias: list[dict[str, Any]] = []
    algum_nao_avaliado = False

    for caminho in CAMPOS_FIXOS:
        alvo = _valor_alvo(consulta, caminho)
        existe, valor = obter_caminho(experiencia, caminho)
        if not existe or alvo is None or valor is None:
            resultado = "NAO_AVALIADO"
            motivo = "VALOR_AUSENTE"
            algum_nao_avaliado = True
        elif valor == alvo:
            resultado = "CONCORDA"
            motivo = None
        else:
            resultado = "DIVERGE"
            motivo = None

        criterio = {
            "campo": caminho,
            "resultado": resultado,
            "valor_alvo": alvo,
            "valor_experiencia": valor if existe else None,
            "motivo_nao_avaliado": motivo,
        }
        criterios.append(criterio)
        tipado = {
            "campo": caminho,
            "valor_alvo": alvo,
            "valor_experiencia": valor if existe else None,
        }
        if resultado == "CONCORDA":
            concordancias.append(tipado)
        elif resultado == "DIVERGE":
            divergencias.append(tipado)

    if divergencias:
        classificacao = "CONTRARIA"
    elif algum_nao_avaliado:
        classificacao = "NEUTRA"
    else:
        classificacao = "FAVORAVEL"
    return criterios, concordancias, divergencias, classificacao


def violacoes_bloqueadoras(experiencia: Mapping[str, Any]) -> list[str]:
    motivos: list[str] = []
    hipotese = experiencia.get("hipotese", {})
    resultado = experiencia.get("resultado", {})

    if not isinstance(hipotese, Mapping):
        return ["HIPOTESE_INVALIDA"]

    direcao = hipotese.get("direcao")
    if direcao not in (None, "COMPRA", "VENDA"):
        motivos.append("DIRECAO_INVALIDA")
    if hipotese.get("direcao_inventada") is not False:
        motivos.append("DIRECAO_INVENTADA")

    if isinstance(resultado, Mapping):
        status = resultado.get("status_metricas")
        if direcao is None and status != "SEM_DIRECAO":
            motivos.append("STATUS_METRICAS_DIRECAO_AUSENTE_DIVERGENTE")
        if direcao in ("COMPRA", "VENDA") and status not in (
            "CALCULADO",
            "JANELA_INCOMPLETA",
        ):
            motivos.append("STATUS_METRICAS_DIRECAO_PRESENTE_DIVERGENTE")
    else:
        motivos.append("RESULTADO_INVALIDO")

    return motivos
