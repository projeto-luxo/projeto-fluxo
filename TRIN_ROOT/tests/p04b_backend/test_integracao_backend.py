from __future__ import annotations

import importlib
import json
from pathlib import Path

from fastapi.testclient import TestClient

from backend.confluencia_replay_backend import anexar_confluencia_replay_backend
from tests.p04b_backend.helpers import (
    consulta,
    env_config,
    experiencia,
    payload_fiscal_aprovado,
)


def test_backend_oficial_identificado_por_launcher():
    root = Path(__file__).resolve().parents[2]
    texto = (root / "INICIAR_TRIN_PAINEL.bat").read_text(encoding="utf-8")
    assert "backend.server_institucional_v6:app" in texto
    assert "--port 8001" in texto


def test_backend_retorno_antecipado_tambem_contem_campo(monkeypatch):
    monkeypatch.delenv("TRIN_CONFLUENCIA_REPLAY_REPOSITORIO_JSONL", raising=False)
    modulo = importlib.import_module("backend.server_institucional_v6")
    monkeypatch.setattr(modulo, "historico", [])
    monkeypatch.setattr(modulo, "atualizar_historico", lambda: None)
    monkeypatch.setattr(modulo.replay_reader, "ativo", False)
    payload = modulo.gerar_payload()
    assert payload["status_backend"] == "SEM_HISTORICO_SUFICIENTE"
    assert "confluencia_replay" in payload
    assert payload["confluencia_replay"]["operacional"] is False


def test_backend_caminho_principal_contem_campo(monkeypatch):
    monkeypatch.delenv("TRIN_CONFLUENCIA_REPLAY_REPOSITORIO_JSONL", raising=False)
    modulo = importlib.import_module("backend.server_institucional_v6")
    modulo.gerar_payload()
    payload = modulo.gerar_payload()
    assert "confluencia_replay" in payload
    assert payload["confluencia_replay"]["peso"] == 0


def test_endpoint_http_data_real_expoe_contrato(monkeypatch):
    modulo = importlib.import_module("backend.server_institucional_v6")
    monkeypatch.setattr(modulo, "historico", [])
    monkeypatch.setattr(modulo, "atualizar_historico", lambda: None)
    monkeypatch.setattr(modulo.replay_reader, "ativo", False)
    with TestClient(modulo.app) as cliente:
        resposta = cliente.get("/data")
    assert resposta.status_code == 200
    payload = resposta.json()
    assert payload["status_backend"] == "SEM_HISTORICO_SUFICIENTE"
    assert payload["confluencia_replay"]["operacional"] is False


def test_endpoint_websocket_ws_real_expoe_mesmo_contrato(monkeypatch):
    modulo = importlib.import_module("backend.server_institucional_v6")
    monkeypatch.setattr(modulo, "historico", [])
    monkeypatch.setattr(modulo, "atualizar_historico", lambda: None)
    monkeypatch.setattr(modulo.replay_reader, "ativo", False)
    with TestClient(modulo.app) as cliente:
        with cliente.websocket_connect("/ws") as websocket:
            payload = websocket.receive_json()
    assert payload["status_backend"] == "SEM_HISTORICO_SUFICIENTE"
    assert payload["confluencia_replay"]["peso"] == 0

def _registrar_experiencia_oficial(repositorio, item):
    registrar = getattr(repositorio, "registrar_experiencia", None)
    assert callable(registrar)
    registrar(item)


def test_fluxo_oficial_historiador_p04a_backend(tmp_path):
    from intelligence.confluencia_replay import avaliar_confluencia_replay
    from intelligence.historiador_replay import RepositorioExperiencias

    env = env_config(tmp_path)
    caminho = Path(env["TRIN_CONFLUENCIA_REPLAY_REPOSITORIO_JSONL"])
    caminho.unlink()

    repositorio = RepositorioExperiencias(caminho)
    assert callable(getattr(repositorio, "consultar_experiencias", None))
    _registrar_experiencia_oficial(repositorio, experiencia(1))

    saida_p04a = avaliar_confluencia_replay(
        consulta=consulta(),
        repositorio=repositorio,
        validar_schema_saida=True,
    )

    payload = anexar_confluencia_replay_backend(
        payload_fiscal_aprovado(),
        replay_ativo=True,
        replay_status={"data_pregao": "2026-01-21"},
        environ=env,
        timeout_segundos=5.0,
    )
    campo = payload["confluencia_replay"]

    assert campo["status"] == saida_p04a["status"]
    assert campo["id_confluencia"] == saida_p04a["id_confluencia"]
    assert campo["hash_resultado"] == saida_p04a["hash_resultado"]
    assert (
        campo["quantidade_experiencias"]
        == saida_p04a["quantidade_experiencias"]
        == 1
    )
    assert campo["classificacoes"] == saida_p04a["classificacoes_evidencia"]
    assert campo["metricas"]["qualidade_hipotese"] == (
        saida_p04a["metricas_qualidade_hipotese"]
    )
    assert campo["bloqueios"] == saida_p04a["bloqueios"]
    assert campo["motivos"] == saida_p04a["motivos"]
    assert campo["gate_fiscal"]["aprovado_operacional"] is True
    assert campo["peso"] == 0
    assert campo["impacto_operacional"] == 0
    assert campo["operacional"] is False


def test_dois_caminhos_de_retorno_usam_finalizador_unico():
    root = Path(__file__).resolve().parents[2]
    texto = (root / "backend/server_institucional_v6.py").read_text(encoding="utf-8")
    assert texto.count("return _finalizar_payload_p04b(payload_fallback)") == 1
    assert texto.count("return _finalizar_payload_p04b(payload)") == 1
    assert texto.count("def _finalizar_payload_p04b(payload):") == 1
