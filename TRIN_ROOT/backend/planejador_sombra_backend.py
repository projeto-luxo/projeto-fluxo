from __future__ import annotations

from collections.abc import Mapping
from copy import deepcopy
from datetime import datetime
import hashlib
import json
import math
from typing import Any, Protocol
from zoneinfo import ZoneInfo


SCHEMA_ENTRADA = "PlanejamentoOperacionalSombraEntradaV1"
SCHEMA_SAIDA = "PlanejamentoOperacionalSombraV1"
SCHEMA_CONFLUENCIA = "ConfluenciaOperacionalV1"
FONTE_FISCAL_OFICIAL = "FISCAL_TEMPORAL_LAUDO_OFICIAL"
STATUS_FISCAIS_ESTRITAMENTE_APROVADOS = frozenset(
    {"CERTIFICADO", "APROVADO", "OK"}
)
CAMPOS_REGIAO = (
    "chave_regiao",
    "status",
    "uso_operacional",
    "limite_inferior",
    "limite_superior",
    "classificacao",
    "quantidade_origens",
)
CAMPO_SAIDA = "planejamento_operacional_sombra"
CAMPO_STATUS = "planejamento_operacional_sombra_status"
CAMPO_ERRO = "planejamento_operacional_sombra_erro"
TIMEZONE_OFICIAL = ZoneInfo("America/Sao_Paulo")


class PlanejadorSombra(Protocol):
    def planejar_sombra(
        self,
        entrada: Mapping[str, Any] | None,
    ) -> dict[str, Any]: ...


def _mapping(valor: Any) -> dict[str, Any]:
    if not isinstance(valor, Mapping):
        return {}
    return dict(valor)


def _texto(valor: Any) -> str:
    return valor.strip() if isinstance(valor, str) else ""


def _texto_upper(valor: Any) -> str:
    return _texto(valor).upper()


def _inteiro_nao_negativo(valor: Any) -> int | None:
    if isinstance(valor, bool) or not isinstance(valor, int) or valor < 0:
        return None
    return valor


def _numero_finito(valor: Any) -> float | None:
    try:
        numero = float(valor)
    except (TypeError, ValueError):
        return None
    if not math.isfinite(numero):
        return None
    return numero


def _ultimo_candle(payload: Mapping[str, Any]) -> dict[str, Any]:
    historico = payload.get("historico")
    if not isinstance(historico, list) or not historico:
        return {}
    ultimo = historico[-1]
    return _mapping(ultimo)


def _timestamp_iso_oficial(candle: Mapping[str, Any]) -> str | None:
    epoch = _numero_finito(candle.get("time"))
    if epoch is None:
        return None
    try:
        return datetime.fromtimestamp(
            epoch,
            tz=TIMEZONE_OFICIAL,
        ).isoformat(timespec="seconds")
    except (OverflowError, OSError, ValueError):
        return None


def _hash_deterministico(dados: Mapping[str, Any]) -> str:
    serializado = json.dumps(
        dados,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )
    return hashlib.sha256(serializado.encode("utf-8")).hexdigest()


def _gate_fiscal(payload: Mapping[str, Any]) -> dict[str, Any]:
    fiscal = _mapping(payload.get("fiscal"))
    fonte = _texto(fiscal.get("fonte"))
    status = _texto_upper(fiscal.get("status"))
    aprovado = (
        fonte == FONTE_FISCAL_OFICIAL
        and status in STATUS_FISCAIS_ESTRITAMENTE_APROVADOS
        and fiscal.get("aprovado_operacional") is True
        and fiscal.get("bloqueio_operacional") is False
    )
    return {
        "decisao": "APROVADA" if aprovado else "BLOQUEADA",
        "status_tecnico_bruto": status or None,
        "motivo": fiscal.get("motivo"),
        "fonte": fonte or None,
    }


def _contrato_ativo_confirmado(payload: Mapping[str, Any]) -> str | None:
    contrato = _mapping(payload.get("contrato_ativo"))
    esperado = _texto_upper(contrato.get("contrato_esperado_rtd"))
    excel = _texto_upper(contrato.get("contrato_excel_rtd"))
    backend = _texto_upper(contrato.get("contrato_backend_rtd"))
    aprovado = (
        _texto_upper(contrato.get("resolver_status")) == "RESOLVIDO"
        and _texto_upper(contrato.get("status_validacao")) == "APROVADO"
        and contrato.get("bloqueio_operacional") is False
        and bool(esperado)
        and esperado == excel
        and excel == backend
    )
    return excel if aprovado else None


def _fontes_saudaveis(payload: Mapping[str, Any]) -> bool:
    painel = _mapping(payload.get("painel_temporal"))
    candle = _ultimo_candle(payload)

    fonte_dados = _texto_upper(
        payload.get("fonte_dados") or candle.get("fonte_dados")
    )
    status_candle = _texto_upper(candle.get("status_candle"))
    status_fonte = _texto_upper(
        painel.get("status_fonte") or candle.get("status_fonte")
    )

    return (
        "referencias_mercado_erro" in payload
        and payload.get("referencias_mercado_erro") is None
        and "regioes_compostas_erro" in payload
        and payload.get("regioes_compostas_erro") is None
        and painel.get("fonte_estagnada") is False
        and bool(fonte_dados)
        and "FALLBACK" not in fonte_dados
        and "INDISPONIVEL" not in fonte_dados
        and bool(status_candle)
        and "FALLBACK" not in status_candle
        and bool(status_fonte)
        and status_fonte != "RTD_ESTAGNADO"
    )


def _regioes_elegiveis(payload: Mapping[str, Any]) -> list[dict[str, Any]]:
    regioes = payload.get("regioes_compostas")
    if not isinstance(regioes, list):
        return []

    saida: list[dict[str, Any]] = []
    for regiao in regioes:
        if not isinstance(regiao, Mapping):
            continue
        saida.append(
            {
                campo: deepcopy(regiao.get(campo))
                for campo in CAMPOS_REGIAO
            }
        )
    return saida


def _confluencia_versionada(payload: Mapping[str, Any]) -> dict[str, Any]:
    confluencia = _mapping(payload.get("confluencia"))
    evidencias = confluencia.get("evidencias")
    if not isinstance(evidencias, list):
        evidencias = []
    return {
        "schema_version": SCHEMA_CONFLUENCIA,
        "score_confluencia": deepcopy(
            confluencia.get("score_confluencia")
        ),
        "direcao": _texto_upper(confluencia.get("direcao")) or None,
        "qualidade": _texto_upper(confluencia.get("qualidade")) or None,
        "evidencias": deepcopy(evidencias),
    }


def _origem_contexto(payload: Mapping[str, Any]) -> str:
    replay = _mapping(payload.get("replay"))
    processamento = _mapping(payload.get("processamento_operacional"))
    modos = {
        _texto_upper(payload.get("modo_dados")),
        _texto_upper(payload.get("modo")),
        _texto_upper(replay.get("modo_dados")),
        _texto_upper(processamento.get("modo_dados")),
    }
    if replay.get("ativo") is True or "REPLAY" in modos:
        return "REPLAY"
    if replay.get("ativo") is False or "AO_VIVO" in modos:
        return "AO_VIVO"
    return "DESCONHECIDA"


def _periodo_parcial_replay(candle: Mapping[str, Any]) -> bool:
    quantidade = _inteiro_nao_negativo(candle.get("qtd_candles_origem"))
    esperados = _inteiro_nao_negativo(
        candle.get("qtd_candles_esperados")
    )
    completo = (
        candle.get("candle_em_formacao") is False
        and quantidade is not None
        and esperados is not None
        and esperados > 0
        and quantidade >= esperados
    )
    return not completo


def _identidade_snapshot(
    payload: Mapping[str, Any],
    origem: str,
) -> dict[str, Any]:
    candle = _ultimo_candle(payload)
    processamento = _mapping(payload.get("processamento_operacional"))
    replay = _mapping(payload.get("replay"))
    timestamp = _timestamp_iso_oficial(candle)
    assinatura = deepcopy(processamento.get("assinatura_evento"))

    if origem == "REPLAY":
        sequencia = _inteiro_nao_negativo(replay.get("indice"))
        material_id = {
            "origem_contexto": origem,
            "timestamp_epoch": candle.get("time"),
            "indice": sequencia,
            "assinatura_evento": assinatura,
        }
        return {
            "evento_id": _hash_deterministico(material_id),
            "timestamp": timestamp,
            "sequencia": sequencia,
            "ordem_evento": sequencia,
            "janela_fim_ordem": sequencia,
            "periodo_parcial": _periodo_parcial_replay(candle),
        }

    sequencia = _inteiro_nao_negativo(processamento.get("sequencia"))
    material_id = {
        "origem_contexto": origem,
        "assinatura_evento": assinatura,
        "sequencia": sequencia,
    }
    return {
        "evento_id": _hash_deterministico(material_id),
        "timestamp": timestamp,
        "sequencia": sequencia,
        "periodo_parcial": True,
    }


def montar_entrada_planejador_sombra_v1(
    payload: Mapping[str, Any] | None,
) -> dict[str, Any]:
    dados = _mapping(payload)
    origem = _origem_contexto(dados)
    return {
        "schema_version": SCHEMA_ENTRADA,
        "gate_fiscal": _gate_fiscal(dados),
        "contrato_ativo": _contrato_ativo_confirmado(dados),
        "fontes_saudaveis": _fontes_saudaveis(dados),
        "regioes_elegiveis": _regioes_elegiveis(dados),
        "confluencia_versionada": _confluencia_versionada(dados),
        "origem_contexto": origem,
        "identidade_snapshot": _identidade_snapshot(dados, origem),
    }


def campo_planejamento_sombra_bloqueado(
    motivo: str,
    *,
    erro_tipo: str | None = None,
) -> dict[str, Any]:
    evidencias: dict[str, Any] = {}
    if erro_tipo:
        evidencias["erro_tipo"] = erro_tipo
    return {
        "schema_version": SCHEMA_SAIDA,
        "id_plano": "PO-BACKEND-ERRO-BLOQUEADO",
        "modo": "SOMBRA",
        "origem_contexto": "DESCONHECIDA",
        "estado": "ERRO_BLOQUEADO",
        "autorizacao": "BLOQUEADA",
        "uso_operacional": "BLOQUEADO",
        "motivo_bloqueio": motivo,
        "direcao": None,
        "entrada_inferior": None,
        "entrada_superior": None,
        "invalidacao": None,
        "stop": None,
        "parcial": None,
        "alvo": None,
        "ordem_corretora": None,
        "entradas_recebidas": None,
        "gates": [],
        "evidencias": evidencias,
        "hipotese_plano": None,
        "rastreabilidade": {
            "identidade_snapshot": {},
            "hash_entrada": None,
            "versao_regra": None,
            "look_ahead": False,
        },
    }


def _normalizar_saida_fail_closed(
    saida: Mapping[str, Any],
) -> dict[str, Any]:
    if not isinstance(saida, Mapping):
        raise TypeError("SAIDA_PLANEJADOR_SOMBRA_NAO_MAPPING")
    normalizada = deepcopy(dict(saida))
    normalizada["schema_version"] = SCHEMA_SAIDA
    normalizada["modo"] = "SOMBRA"
    normalizada["autorizacao"] = "BLOQUEADA"
    normalizada["uso_operacional"] = "BLOQUEADO"
    normalizada["ordem_corretora"] = None
    for campo in (
        "entrada_inferior",
        "entrada_superior",
        "invalidacao",
        "stop",
        "parcial",
        "alvo",
    ):
        normalizada[campo] = None
    return normalizada


def anexar_planejamento_sombra_v1(
    payload: Mapping[str, Any] | None,
    *,
    planejador: PlanejadorSombra,
) -> dict[str, Any]:
    copia = _mapping(payload)
    try:
        entrada = montar_entrada_planejador_sombra_v1(copia)
        saida = _normalizar_saida_fail_closed(
            planejador.planejar_sombra(entrada)
        )
        copia[CAMPO_SAIDA] = saida
        copia[CAMPO_STATUS] = (
            "ERRO_BLOQUEADO"
            if saida.get("estado") == "ERRO_BLOQUEADO"
            else "SOMBRA_VERSIONADA_BLOQUEADA"
        )
        copia[CAMPO_ERRO] = None
    except Exception as erro:
        copia[CAMPO_SAIDA] = campo_planejamento_sombra_bloqueado(
            "ERRO_ADAPTER_PLANEJADOR_SOMBRA",
            erro_tipo=type(erro).__name__,
        )
        copia[CAMPO_STATUS] = "ERRO_BLOQUEADO"
        copia[CAMPO_ERRO] = f"{type(erro).__name__}: {erro}"
    return copia
