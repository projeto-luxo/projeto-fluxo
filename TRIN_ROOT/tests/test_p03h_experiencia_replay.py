from __future__ import annotations

import copy
import hashlib
import json
import os
from pathlib import Path

import pytest

from intelligence.historiador_replay import (
    RepositorioExperiencias,
    construir_experiencia_replay,
    consultar_experiencia,
    consultar_experiencias,
    registrar_experiencia,
)


def _contextos() -> list[dict]:
    eventos = [
        (1, "09:00", "100010.00", "100030.00", "99980.00"),
        (2, "09:01", "100020.00", "100040.00", "99990.00"),
        (3, "09:02", "100000.00", "100050.00", "100000.00"),
        (4, "09:03", "100060.00", "100080.00", "99980.00"),
        (5, "09:04", "100100.00", "100120.00", "99950.00"),
        (6, "09:05", "100020.00", "100070.00", "99970.00"),
        (7, "09:06", "100030.00", "100060.00", "99960.00"),
        (8, "09:07", "100080.00", "100090.00", "100010.00"),
    ]
    saida = []
    anteriores: list[dict] = []
    for ordinal, hora, ultimo, maximo, minimo in eventos:
        evento = {
            "ativo": "WINFUT",
            "data": "21/01/2026",
            "hora": f"{hora}:00",
            "timestamp": f"2026-01-21T{hora}:00-03:00",
            "abertura": ultimo,
            "maximo": maximo,
            "minimo": minimo,
            "ultimo": ultimo,
            "volume": "1.00",
            "volume_quantidade": "1",
        }
        saida.append(
            {
                "solicitacao_id": "SOL-P03H-001",
                "origem_id": "ORIGEM-CONTROLADA",
                "origem_hash": "a" * 64,
                "periodo_solicitado": {
                    "inicio": "2026-01-21T09:00:00-03:00",
                    "fim": "2026-01-21T09:07:00-03:00",
                },
                "timestamp_evento": evento["timestamp"],
                "ordinal_evento": ordinal,
                "evento_atual": evento,
                "sessao": {"sessao_id": "2026-01-21", "mudou_sessao": ordinal == 1},
                "janela_anterior": copy.deepcopy(anteriores[-2:]),
            }
        )
        anteriores.append(evento)
    return saida


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_origem_e_compartimentos_separados():
    exp = construir_experiencia_replay(
        _contextos(),
        ordinal_referencia=3,
        hipotese={"direcao": "COMPRA", "origem_direcao": "FIXTURE_P03H"},
        tamanho_janela_posterior=3,
    )
    dados = exp.como_dict()
    assert dados["origem_tipo"] == "ORIGEM_REPLAY"
    assert all(isinstance(dados[k], dict) for k in ("fato", "contexto", "hipotese", "resultado"))


def test_direcao_ausente_permanece_ausente():
    exp = construir_experiencia_replay(
        _contextos(), ordinal_referencia=3, hipotese={}, tamanho_janela_posterior=3
    )
    assert exp.hipotese["direcao"] is None
    assert exp.hipotese["direcao_inventada"] is False
    assert exp.resultado["mfe_pontos"] is None
    assert exp.resultado["mae_pontos"] is None
    assert exp.resultado["status_metricas"] == "SEM_DIRECAO"


def test_mfe_mae_e_janela_deterministicos():
    args = dict(
        contextos=_contextos(),
        ordinal_referencia=3,
        hipotese={"direcao_fornecida": "COMPRA", "origem_direcao": "FIXTURE_P03H"},
        tamanho_janela_posterior=3,
    )
    primeira = construir_experiencia_replay(**args)
    segunda = construir_experiencia_replay(**args)
    assert primeira.resultado["janela_posterior_ordinais"] == [4, 5, 6]
    assert primeira.resultado["mfe_pontos"] == "120.00"
    assert primeira.resultado["mae_pontos"] == "50.00"
    assert primeira.como_dict() == segunda.como_dict()


def test_entrada_nao_e_mutada():
    contextos = _contextos()
    antes = copy.deepcopy(contextos)
    construir_experiencia_replay(
        contextos,
        ordinal_referencia=3,
        hipotese={"direcao": "COMPRA"},
        tamanho_janela_posterior=3,
    )
    assert contextos == antes


def test_repositorio_registro_consulta_e_idempotencia(tmp_path: Path):
    exp = construir_experiencia_replay(
        _contextos(),
        ordinal_referencia=3,
        hipotese={"direcao": "COMPRA", "origem_direcao": "TESTE"},
        tamanho_janela_posterior=3,
    )
    destino = tmp_path / "experiencias.jsonl"
    repo = RepositorioExperiencias(destino)
    primeiro = registrar_experiencia(repo, exp)
    segundo = registrar_experiencia(repo, exp)
    assert primeiro == segundo
    assert len(destino.read_text(encoding="utf-8").splitlines()) == 1
    assert consultar_experiencia(repo, exp.experiencia_id) == exp.como_dict()
    assert consultar_experiencias(repo, origem_id=exp.origem_id, direcao="COMPRA") == [exp.como_dict()]


def test_repositorio_persistente_reabre_sem_perder_rastreabilidade(tmp_path: Path):
    exp = construir_experiencia_replay(
        _contextos(),
        ordinal_referencia=3,
        hipotese={"direcao": "COMPRA"},
        tamanho_janela_posterior=3,
    )
    destino = tmp_path / "experiencias.jsonl"
    RepositorioExperiencias(destino).registrar_experiencia(exp)
    reaberto = RepositorioExperiencias(destino)
    assert reaberto.consultar_experiencia(exp.experiencia_id) == exp.como_dict()


def test_sem_import_ou_chamada_automatica_de_confluencia():
    import intelligence.historiador_replay.experiencia_replay as modulo
    fonte = Path(modulo.__file__).read_text(encoding="utf-8")
    assert "confluence" not in fonte.casefold()
    assert "confluencia" not in fonte.casefold()
