from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

from intelligence.confluencia_replay.canonico import sha256_canonico
from intelligence.confluencia_replay.nucleo import NucleoConfluenciaReplay
from intelligence.confluencia_replay.porta_historiador import PortaHistoriadorConfluenciaV1


SCHEMA_HISTORIADOR_SHA256 = "c579f15b9b6900e6904810f15f0a0ddf7b6965ad362f821e34757dde0cd019dc"


def consulta_padrao(**contexto_override: Any) -> dict[str, Any]:
    contexto = {
        "ativo": "WINFUT",
        "regime": "REPLAY_CERTIFICADO_SEM_INFERENCIA_OPERACIONAL",
        "sessao_id": "2026-01-21",
    }
    contexto.update(contexto_override)
    return {
        "contrato_consulta": "ConsultaConfluenciaReplayV1",
        "versao": "1.0.0",
        "modo_analise": "RETROSPECTIVO_SELADO",
        "origem_id": "WINFUT_REPLAY_SELADO_001",
        "perfil_criterio": "CRITERIO_CONFLUENCIA_REPLAY_V1",
        "campos_comparacao": [
            "fato.evento.ativo",
            "contexto.regime",
            "contexto.sessao.sessao_id",
        ],
        "contexto_alvo": contexto,
        "particao_dados": {
            "metodo": "CORTE_TEMPORAL_50_50_V1_PROVISORIO",
            "percentual_calibracao": 50,
            "percentual_prova": 50,
        },
        "politica_universo": {
            "usar_universo_completo": True,
            "top_n": None,
            "limite_seguranca": 1000,
            "ordem": "timestamp_referencia_ordinal_referencia_experiencia_id_ASC",
            "filtro_direcao": None,
        },
    }


def experiencia(
    i: int,
    *,
    ativo: str | None = "WINFUT",
    regime: str | None = "REPLAY_CERTIFICADO_SEM_INFERENCIA_OPERACIONAL",
    sessao_id: str | None = "2026-01-21",
    direcao: str | None = "COMPRA",
    origem_direcao: str | None = "CONTROLADA",
    mfe: str | None = "120.00",
    mae: str | None = "50.00",
    timestamp: str | None = None,
    ordinal: int | None = None,
    maximo: str | None = "10120",
    minimo: str | None = "9950",
    origem_tipo: str = "ORIGEM_REPLAY",
    origem_id: str = "WINFUT_REPLAY_SELADO_001",
    incluir_regime: bool = True,
) -> dict[str, Any]:
    timestamp = timestamp or f"2026-01-21T09:{i % 60:02d}:00-03:00"
    ordinal = ordinal if ordinal is not None else i
    origem_hash = f"{i % 16:x}" * 64
    evento = {
        "ativo": ativo,
        "maximo": maximo,
        "minimo": minimo,
        "ultimo": "10000",
    }
    contexto = {
        "origem_id": origem_id,
        "origem_hash": origem_hash,
        "periodo_solicitado": {
            "inicio": "2026-01-21T09:00:00-03:00",
            "fim": "2026-01-21T17:00:00-03:00",
        },
        "sessao": {
            "sessao_id": sessao_id,
            "mudou_sessao": False,
        },
        "janela_anterior": [],
        "tamanho_janela_posterior": 3,
    }
    if incluir_regime:
        contexto["regime"] = regime

    corpo = {
        "contrato": "ExperienciaReplayV1",
        "versao": "1.0.0",
        "origem_tipo": origem_tipo,
        "solicitacao_id": f"SOL-{i}",
        "origem_id": origem_id,
        "origem_hash": origem_hash,
        "timestamp_referencia": timestamp,
        "ordinal_referencia": ordinal,
        "fato": {
            "timestamp": timestamp,
            "ordinal": ordinal,
            "evento": evento,
        },
        "contexto": contexto,
        "hipotese": {
            "direcao": direcao,
            "origem_direcao": origem_direcao if direcao is not None or origem_direcao else None,
            "direcao_inventada": False,
        },
        "resultado": {
            "regra_janela_posterior": "3_EVENTOS_IMEDIATAMENTE_POSTERIORES",
            "janela_posterior_ordinais": [ordinal + 1, ordinal + 2, ordinal + 3],
            "janela_posterior_completa": True,
            "mfe_pontos": mfe,
            "mae_pontos": mae,
            "status_metricas": "CALCULADO" if direcao is not None else "SEM_DIRECAO",
        },
    }
    return {
        "experiencia_id": sha256_canonico(corpo),
        **corpo,
    }


class RepositorioFake:
    def __init__(self, experiencias: list[dict[str, Any]]) -> None:
        self.experiencias = experiencias
        self.chamadas: list[tuple[str | None, str | None]] = []
        self.escritas = 0

    def consultar_experiencias(
        self,
        origem_id: str | None = None,
        direcao: str | None = None,
    ) -> list[dict[str, Any]]:
        self.chamadas.append((origem_id, direcao))
        return self.experiencias

    def registrar(self, *_: Any, **__: Any) -> None:
        self.escritas += 1
        raise AssertionError("não deve ser chamado")


def avaliar(
    experiencias: list[dict[str, Any]],
    *,
    consulta: dict[str, Any] | None = None,
    schema_saida: bool = False,
) -> tuple[dict[str, Any], RepositorioFake]:
    repo = RepositorioFake(experiencias)
    nucleo = NucleoConfluenciaReplay(
        PortaHistoriadorConfluenciaV1(repo),
        validar_schema_saida=schema_saida,
    )
    return nucleo.avaliar(consulta or consulta_padrao()), repo


def hash_objeto(valor: Any) -> str:
    return sha256_canonico(valor)


def schema_historiador_fixture() -> Path:
    return Path(__file__).resolve().parent / "fixtures" / "EXPERIENCIA_REPLAY_V1.schema.json"
