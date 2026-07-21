from __future__ import annotations

import copy
from pathlib import Path
from typing import Any

from intelligence.confluencia_replay import avaliar_confluencia_replay
from intelligence.historiador_replay.util.hash_sha256 import sha256_bytes
from intelligence.historiador_replay.util.json_canonico import json_canonico_bytes

REGIME_OFICIAL_TESTE = "REGIME_REPLAY_OFICIAL_TESTE"
ORIGEM_ID_TESTE = "ORIGEM-P04B"


class RepositorioFake:
    """Somente para testes unitários do adapter; o ponta a ponta usa a classe real."""

    def __init__(self, experiencias: list[dict[str, Any]]) -> None:
        self.experiencias = copy.deepcopy(experiencias)
        self.chamadas: list[tuple[str | None, str | None]] = []

    def consultar_experiencias(self, origem_id=None, direcao=None):
        self.chamadas.append((origem_id, direcao))
        return copy.deepcopy(self.experiencias)


def consulta(origem_id: str = ORIGEM_ID_TESTE):
    return {
        "contrato_consulta": "ConsultaConfluenciaReplayV1",
        "versao": "1.0.0",
        "modo_analise": "RETROSPECTIVO_SELADO",
        "origem_id": origem_id,
        "perfil_criterio": "CRITERIO_CONFLUENCIA_REPLAY_V1",
        "campos_comparacao": [
            "fato.evento.ativo",
            "contexto.regime",
            "contexto.sessao.sessao_id",
        ],
        "contexto_alvo": {
            "ativo": "WINFUT",
            "regime": REGIME_OFICIAL_TESTE,
            "sessao_id": "2026-01-21",
        },
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


def experiencia(n: int, origem_id: str = ORIGEM_ID_TESTE):
    corpo = {
        "contrato": "ExperienciaReplayV1",
        "versao": "1.0.0",
        "origem_tipo": "ORIGEM_REPLAY",
        "solicitacao_id": "SOL-P04B",
        "origem_id": origem_id,
        "origem_hash": "a" * 64,
        "timestamp_referencia": f"2026-01-21T09:{n:02d}:00-03:00",
        "ordinal_referencia": n,
        "fato": {"evento": {"ativo": "WINFUT", "maximo": "100120.00", "minimo": "99950.00"}},
        "contexto": {"regime": REGIME_OFICIAL_TESTE, "sessao": {"sessao_id": "2026-01-21"}},
        "hipotese": {"direcao": "COMPRA", "origem_direcao": "TESTE", "direcao_inventada": False, "status_metricas": "CALCULADAS"},
        "resultado": {"mfe_pontos": "120.00", "mae_pontos": "50.00", "desfecho": "MFE_MAE_DETERMINISTICO", "direcao_avaliada": "COMPRA"},
    }
    return {
        "experiencia_id": sha256_bytes(json_canonico_bytes(corpo)),
        **corpo,
    }


def saida_p04a_valida():
    repo = RepositorioFake([experiencia(1), experiencia(2)])
    return avaliar_confluencia_replay(consulta=consulta(), repositorio=repo, validar_schema_saida=True)


def env_config(tmp_path: Path):
    path = tmp_path / "experiencias.jsonl"
    path.write_text("", encoding="utf-8")
    return {
        "TRIN_CONFLUENCIA_REPLAY_ORIGEM_ID": ORIGEM_ID_TESTE,
        "TRIN_CONFLUENCIA_REPLAY_REPOSITORIO_JSONL": str(path),
        "TRIN_CONFLUENCIA_REPLAY_ATIVO": "WINFUT",
        "TRIN_CONFLUENCIA_REPLAY_SESSAO_ID": "2026-01-21",
        "TRIN_CONFLUENCIA_REPLAY_REGIME": REGIME_OFICIAL_TESTE,
        "TRIN_CONFLUENCIA_REPLAY_REGIME_FONTE": "HISTORIADOR_REPLAY_CONTEXTO_OFICIAL",
    }


def payload_fiscal_aprovado(extra: dict[str, Any] | None = None):
    payload = {
        "contrato_ativo": {"ativo_base": "WINFUT"},
        "fiscal": {
            "fonte": "FISCAL_TEMPORAL_LAUDO_OFICIAL",
            "status": "CERTIFICADO",
            "aprovado_operacional": True,
            "bloqueio_operacional": False,
            "motivo": None,
        },
    }
    if extra:
        payload.update(copy.deepcopy(extra))
    return payload
