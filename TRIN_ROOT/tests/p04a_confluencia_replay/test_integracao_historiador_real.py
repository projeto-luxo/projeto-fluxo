from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator, FormatChecker

from intelligence.confluencia_replay.erros import FalhaConfluenciaReplay
from intelligence.confluencia_replay.modelos import validar_experiencia_minima
from intelligence.confluencia_replay.porta_historiador import PortaHistoriadorConfluenciaV1

from .helpers import (
    RepositorioFake,
    SCHEMA_HISTORIADOR_SHA256,
    avaliar,
    consulta_padrao,
    experiencia,
    schema_historiador_fixture,
)


def test_integracao_01_fixture_confere_schema_homologado() -> None:
    caminho = schema_historiador_fixture()
    assert hashlib.sha256(caminho.read_bytes()).hexdigest() == SCHEMA_HISTORIADOR_SHA256
    schema = json.loads(caminho.read_text(encoding="utf-8-sig"))
    Draft202012Validator.check_schema(schema)
    erros = list(
        Draft202012Validator(
            schema,
            format_checker=FormatChecker(),
        ).iter_errors(experiencia(1))
    )
    assert erros == []


def test_integracao_02_formato_real_sem_campos_sinteticos_e_aceito() -> None:
    item = experiencia(1, incluir_regime=False)
    for proibido in (
        "contrato_experiencia",
        "timestamp_evento",
        "ordinal_evento",
        "rastreabilidade",
        "certificado_id",
    ):
        assert proibido not in item
    projetada = validar_experiencia_minima(item)
    assert projetada.experiencia_id == item["experiencia_id"]
    assert projetada.timestamp_referencia == item["timestamp_referencia"]
    assert projetada.ordinal_referencia == item["ordinal_referencia"]


def test_integracao_03_formato_real_chega_ao_nucleo_sem_bloqueio_de_schema() -> None:
    saida, _ = avaliar([experiencia(1, incluir_regime=False)])
    assert saida["quantidade_experiencias"] == 1
    codigos = {item["codigo"] for item in saida["bloqueios"]}
    assert "EXPERIENCIA_SCHEMA_INCOMPLETO" not in codigos
    assert "DIRECAO_RESULTADO_DIVERGENTE" not in codigos


def test_integracao_04_origem_divergente_bloqueia_na_porta() -> None:
    repo = RepositorioFake([experiencia(1, origem_id="OUTRA_ORIGEM")])
    porta = PortaHistoriadorConfluenciaV1(repo)
    with pytest.raises(FalhaConfluenciaReplay) as exc:
        porta.consultar("WINFUT_REPLAY_SELADO_001")
    assert exc.value.codigo == "PORTA_HISTORIADOR_ORIGEM_DIVERGENTE"


def test_integracao_05_certificado_individual_nao_e_inventado() -> None:
    saida, _ = avaliar([experiencia(1)])
    texto = json.dumps(saida, ensure_ascii=False)
    assert "certificado_id" not in texto
    assert saida["garantia_fiscal"]["certificado_individual_exigido_na_confluencia"] is False


def test_integracao_06_id_experiencia_divergente_bloqueia() -> None:
    item = experiencia(1)
    item["experiencia_id"] = "0" * 64
    saida, _ = avaliar([item])
    assert saida["status"] == "BLOQUEADO"
    assert any(b["codigo"] == "EXPERIENCIA_ID_DIVERGENTE" for b in saida["bloqueios"])
