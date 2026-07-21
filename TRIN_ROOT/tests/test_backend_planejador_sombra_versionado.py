from __future__ import annotations

from copy import deepcopy
import importlib
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient

from backend.planejador_sombra_backend import (
    CAMPO_ERRO,
    CAMPO_SAIDA,
    CAMPO_STATUS,
    CAMPOS_REGIAO,
    SCHEMA_CONFLUENCIA,
    SCHEMA_ENTRADA,
    SCHEMA_SAIDA,
    anexar_planejamento_sombra_v1,
    montar_entrada_planejador_sombra_v1,
)
from core.planejador_operacional import PlanejadorOperacional


EPOCH = 1784563200


def payload_base() -> dict[str, Any]:
    return {
        "historico": [
            {
                "time": EPOCH,
                "fonte_dados": "RTD_EXCEL",
                "status_candle": "RTD_ATUALIZANDO",
                "status_fonte": "RTD_ATUALIZANDO",
            }
        ],
        "processamento_operacional": {
            "sequencia": 7,
            "assinatura_evento": [["time", EPOCH], ["close", 128000.0]],
            "modo_dados": "AO_VIVO",
        },
        "replay": {
            "ativo": False,
            "modo_dados": "AO_VIVO",
            "indice": 0,
        },
        "painel_temporal": {
            "fonte_estagnada": False,
            "status_fonte": "RTD_ATUALIZANDO",
        },
        "referencias_mercado_erro": None,
        "regioes_compostas_erro": None,
        "regioes_compostas": [
            {
                "chave_regiao": "REGIAO|WIN|128000",
                "status": "CANDIDATA",
                "uso_operacional": "BLOQUEADO",
                "limite_inferior": 127950.0,
                "limite_superior": 128050.0,
                "classificacao": "VWAP",
                "quantidade_origens": 2,
                "campo_externo": "NAO_PROPAGAR",
            }
        ],
        "fiscal": {
            "fonte": "FISCAL_TEMPORAL_LAUDO_OFICIAL",
            "status": "CERTIFICADO",
            "aprovado_operacional": True,
            "bloqueio_operacional": False,
            "motivo": "STATUS_FINAL_FISCAL:CERTIFICADO",
        },
        "contrato_ativo": {
            "resolver_status": "RESOLVIDO",
            "status_validacao": "APROVADO",
            "bloqueio_operacional": False,
            "contrato_esperado_rtd": "WINQ26",
            "contrato_excel_rtd": "WINQ26",
            "contrato_backend_rtd": "WINQ26",
        },
        "confluencia": {
            "score_confluencia": 6.5,
            "direcao": "NEUTRO",
            "qualidade": "NEUTRA",
            "evidencias": ["E1"],
        },
        "confluencia_replay": {
            "direcao": "COMPRA",
            "score_confluencia": 10,
        },
        "modo_dados": "AO_VIVO",
    }


def entrada(payload: dict[str, Any] | None = None) -> dict[str, Any]:
    return montar_entrada_planejador_sombra_v1(payload or payload_base())


def test_schema_entrada_exato():
    assert entrada()["schema_version"] == SCHEMA_ENTRADA


def test_campos_superiores_exatos():
    assert set(entrada()) == {
        "schema_version",
        "gate_fiscal",
        "contrato_ativo",
        "fontes_saudaveis",
        "regioes_elegiveis",
        "confluencia_versionada",
        "origem_contexto",
        "identidade_snapshot",
    }


@pytest.mark.parametrize("status", ["CERTIFICADO", "APROVADO", "OK"])
def test_fiscal_status_estrito_aprova(status):
    dados = payload_base()
    dados["fiscal"]["status"] = status
    assert entrada(dados)["gate_fiscal"]["decisao"] == "APROVADA"


@pytest.mark.parametrize(
    "status",
    ["APROVADO_COM_RESSALVAS", "RESSALVA", "DESCONHECIDO", "REPROVADO", ""],
)
def test_fiscal_status_nao_estrito_bloqueia(status):
    dados = payload_base()
    dados["fiscal"]["status"] = status
    assert entrada(dados)["gate_fiscal"]["decisao"] == "BLOQUEADA"


@pytest.mark.parametrize(
    "chave,valor",
    [
        ("aprovado_operacional", False),
        ("aprovado_operacional", None),
        ("bloqueio_operacional", True),
        ("bloqueio_operacional", None),
        ("fonte", "OUTRA_FONTE"),
    ],
)
def test_fiscal_demais_condicoes_bloqueiam(chave, valor):
    dados = payload_base()
    dados["fiscal"][chave] = valor
    assert entrada(dados)["gate_fiscal"]["decisao"] == "BLOQUEADA"


def test_gate_fiscal_preserva_fatos():
    gate = entrada()["gate_fiscal"]
    assert gate == {
        "decisao": "APROVADA",
        "status_tecnico_bruto": "CERTIFICADO",
        "motivo": "STATUS_FINAL_FISCAL:CERTIFICADO",
        "fonte": "FISCAL_TEMPORAL_LAUDO_OFICIAL",
    }


@pytest.mark.parametrize(
    "chave,valor",
    [
        ("resolver_status", "NAO_RESOLVIDO"),
        ("status_validacao", "NAO_APROVADO"),
        ("bloqueio_operacional", True),
        ("contrato_esperado_rtd", "WINV26"),
        ("contrato_excel_rtd", "WINV26"),
        ("contrato_backend_rtd", "WINV26"),
        ("contrato_esperado_rtd", None),
    ],
)
def test_contrato_nao_confirmado_vira_null(chave, valor):
    dados = payload_base()
    dados["contrato_ativo"][chave] = valor
    assert entrada(dados)["contrato_ativo"] is None


def test_contrato_estritamente_aprovado_preservado():
    assert entrada()["contrato_ativo"] == "WINQ26"


@pytest.mark.parametrize(
    "alteracao",
    [
        {"referencias_mercado_erro": "ERRO"},
        {"regioes_compostas_erro": "ERRO"},
        {"painel_temporal": {"fonte_estagnada": True, "status_fonte": "RTD_ATUALIZANDO"}},
        {"historico": [{"time": EPOCH, "fonte_dados": "RTD_FALLBACK", "status_candle": "OK"}]},
        {"historico": [{"time": EPOCH, "fonte_dados": "RTD_INDISPONIVEL", "status_candle": "OK"}]},
        {"historico": [{"time": EPOCH, "fonte_dados": "RTD_EXCEL", "status_candle": "FALLBACK_X"}]},
        {"painel_temporal": {"fonte_estagnada": False, "status_fonte": "RTD_ESTAGNADO"}},
    ],
)
def test_fontes_nao_saudaveis(alteracao):
    dados = payload_base()
    dados.update(deepcopy(alteracao))
    assert entrada(dados)["fontes_saudaveis"] is False


def test_fontes_saudaveis_somente_com_provas_completas():
    assert entrada()["fontes_saudaveis"] is True


def test_ausencia_de_prova_de_saude_bloqueia():
    dados = payload_base()
    dados.pop("referencias_mercado_erro")
    assert entrada(dados)["fontes_saudaveis"] is False


def test_regiao_preserva_somente_campos_congelados():
    regiao = entrada()["regioes_elegiveis"][0]
    assert tuple(regiao) == CAMPOS_REGIAO
    assert "campo_externo" not in regiao


def test_regiao_candidata_permanece_bloqueada():
    regiao = entrada()["regioes_elegiveis"][0]
    assert regiao["status"] == "CANDIDATA"
    assert regiao["uso_operacional"] == "BLOQUEADO"


def test_nao_inventa_regiao_operacional():
    regiao = entrada()["regioes_elegiveis"][0]
    assert (regiao["status"], regiao["uso_operacional"]) != (
        "ATIVA",
        "LIBERADO",
    )


def test_confluencia_recebe_schema_versionado():
    assert entrada()["confluencia_versionada"]["schema_version"] == SCHEMA_CONFLUENCIA


def test_confluencia_mapeia_somente_campos_congelados():
    assert set(entrada()["confluencia_versionada"]) == {
        "schema_version",
        "score_confluencia",
        "direcao",
        "qualidade",
        "evidencias",
    }


def test_neutro_permanece_neutro():
    assert entrada()["confluencia_versionada"]["direcao"] == "NEUTRO"


def test_confluencia_replay_nao_consumida():
    dados = payload_base()
    dados["confluencia_replay"]["direcao"] = "VENDA"
    assert entrada(dados)["confluencia_versionada"]["direcao"] == "NEUTRO"


def test_origem_ao_vivo():
    assert entrada()["origem_contexto"] == "AO_VIVO"


def test_ao_vivo_sempre_periodo_parcial():
    assert entrada()["identidade_snapshot"]["periodo_parcial"] is True


def test_timestamp_tem_timezone_oficial():
    timestamp = entrada()["identidade_snapshot"]["timestamp"]
    assert timestamp.endswith("-03:00")


def payload_replay(*, formacao=False, quantidade=2, esperados=2, indice=9):
    dados = payload_base()
    dados["modo_dados"] = "REPLAY"
    dados["replay"] = {
        "ativo": True,
        "modo_dados": "REPLAY",
        "indice": indice,
    }
    dados["historico"][-1].update(
        {
            "fonte_dados": "REPLAY_CSV",
            "status_candle": "REPLAY_COMPLETO" if not formacao else "REPLAY_PARCIAL",
            "status_fonte": "REPLAY_ATIVO",
            "candle_em_formacao": formacao,
            "qtd_candles_origem": quantidade,
            "qtd_candles_esperados": esperados,
        }
    )
    dados["painel_temporal"]["status_fonte"] = "REPLAY_ATIVO"
    return dados


def test_origem_replay():
    assert entrada(payload_replay())["origem_contexto"] == "REPLAY"


def test_replay_completo_por_contagem():
    assert entrada(payload_replay())["identidade_snapshot"]["periodo_parcial"] is False


def test_replay_em_formacao_parcial():
    assert entrada(payload_replay(formacao=True))["identidade_snapshot"]["periodo_parcial"] is True


def test_replay_curto_parcial():
    assert entrada(payload_replay(quantidade=1, esperados=2))["identidade_snapshot"]["periodo_parcial"] is True


def test_replay_sem_contagem_parcial():
    dados = payload_replay()
    dados["historico"][-1].pop("qtd_candles_origem")
    assert entrada(dados)["identidade_snapshot"]["periodo_parcial"] is True


def test_replay_sem_lookahead_tres_ordens_iguais():
    snapshot = entrada(payload_replay())["identidade_snapshot"]
    assert snapshot["sequencia"] == snapshot["ordem_evento"] == snapshot["janela_fim_ordem"] == 9


def test_mesmo_evento_repete_evento_id():
    assert entrada()["identidade_snapshot"]["evento_id"] == entrada()["identidade_snapshot"]["evento_id"]


def test_nova_sequencia_muda_evento_id():
    dados = payload_base()
    anterior = entrada(dados)["identidade_snapshot"]["evento_id"]
    dados["processamento_operacional"]["sequencia"] = 8
    novo = entrada(dados)["identidade_snapshot"]["evento_id"]
    assert novo != anterior


def test_novo_indice_replay_muda_evento_id():
    assert (
        entrada(payload_replay(indice=9))["identidade_snapshot"]["evento_id"]
        != entrada(payload_replay(indice=10))["identidade_snapshot"]["evento_id"]
    )


@pytest.mark.parametrize(
    "campo",
    [
        "entrada_inferior",
        "entrada_superior",
        "invalidacao",
        "stop",
        "parcial",
        "alvo",
        "ordem_corretora",
    ],
)
def test_saida_sombra_nunca_publica_nivel_ou_ordem(campo):
    resultado = anexar_planejamento_sombra_v1(
        payload_base(),
        planejador=PlanejadorOperacional(modo_sombra_homologado=True),
    )
    assert resultado[CAMPO_SAIDA][campo] is None


def test_saida_sombra_schema_exato():
    resultado = anexar_planejamento_sombra_v1(
        payload_base(),
        planejador=PlanejadorOperacional(modo_sombra_homologado=True),
    )
    assert resultado[CAMPO_SAIDA]["schema_version"] == SCHEMA_SAIDA


def test_saida_sombra_autorizacao_bloqueada():
    resultado = anexar_planejamento_sombra_v1(
        payload_base(),
        planejador=PlanejadorOperacional(modo_sombra_homologado=True),
    )
    assert resultado[CAMPO_SAIDA]["autorizacao"] == "BLOQUEADA"
    assert resultado[CAMPO_SAIDA]["uso_operacional"] == "BLOQUEADO"


def test_saida_sombra_status_publicado():
    resultado = anexar_planejamento_sombra_v1(
        payload_base(),
        planejador=PlanejadorOperacional(modo_sombra_homologado=True),
    )
    assert resultado[CAMPO_STATUS] == "SOMBRA_VERSIONADA_BLOQUEADA"
    assert resultado[CAMPO_ERRO] is None


def test_payload_de_entrada_nao_mutado():
    dados = payload_base()
    snapshot = deepcopy(dados)
    anexar_planejamento_sombra_v1(
        dados,
        planejador=PlanejadorOperacional(modo_sombra_homologado=True),
    )
    assert dados == snapshot


def test_confluencia_e_regioes_nao_mutadas():
    dados = payload_base()
    confluencia = deepcopy(dados["confluencia"])
    regioes = deepcopy(dados["regioes_compostas"])
    anexar_planejamento_sombra_v1(
        dados,
        planejador=PlanejadorOperacional(modo_sombra_homologado=True),
    )
    assert dados["confluencia"] == confluencia
    assert dados["regioes_compostas"] == regioes


class PlanejadorFalho:
    def planejar_sombra(self, _entrada):
        raise RuntimeError("falha_controlada")


class PlanejadorInseguro:
    def planejar_sombra(self, _entrada):
        return {
            "schema_version": "OUTRO",
            "estado": "PLANO",
            "autorizacao": "LIBERADA",
            "uso_operacional": "LIBERADO",
            "entrada_inferior": 1,
            "entrada_superior": 2,
            "invalidacao": 3,
            "stop": 4,
            "parcial": 5,
            "alvo": 6,
            "ordem_corretora": {"lado": "COMPRA"},
        }


def test_erro_adapter_permanece_fail_closed():
    resultado = anexar_planejamento_sombra_v1(
        payload_base(),
        planejador=PlanejadorFalho(),
    )
    campo = resultado[CAMPO_SAIDA]
    assert resultado[CAMPO_STATUS] == "ERRO_BLOQUEADO"
    assert "RuntimeError" in resultado[CAMPO_ERRO]
    assert campo["estado"] == "ERRO_BLOQUEADO"
    assert campo["autorizacao"] == "BLOQUEADA"


def test_fronteira_corrige_saida_insegura():
    resultado = anexar_planejamento_sombra_v1(
        payload_base(),
        planejador=PlanejadorInseguro(),
    )[CAMPO_SAIDA]
    assert resultado["schema_version"] == SCHEMA_SAIDA
    assert resultado["modo"] == "SOMBRA"
    assert resultado["autorizacao"] == "BLOQUEADA"
    assert resultado["uso_operacional"] == "BLOQUEADO"
    assert resultado["ordem_corretora"] is None
    assert all(
        resultado[campo] is None
        for campo in (
            "entrada_inferior",
            "entrada_superior",
            "invalidacao",
            "stop",
            "parcial",
            "alvo",
        )
    )


def test_campo_legado_preservado():
    dados = payload_base()
    dados["planejamento_operacional"] = {"estado": "SEM_OPERACAO"}
    resultado = anexar_planejamento_sombra_v1(
        dados,
        planejador=PlanejadorOperacional(modo_sombra_homologado=True),
    )
    assert resultado["planejamento_operacional"] == dados["planejamento_operacional"]


def test_servidor_tem_instancia_sombra_separada():
    root = Path(__file__).resolve().parents[1]
    texto = (root / "backend/server_institucional_v6.py").read_text(encoding="utf-8")
    assert "planejador_operacional_sombra = PlanejadorOperacional(" in texto
    assert "modo_sombra_homologado=True" in texto


def test_servidor_ordena_replay_sombra_p04b():
    root = Path(__file__).resolve().parents[1]
    texto = (root / "backend/server_institucional_v6.py").read_text(encoding="utf-8")
    indice_replay = texto.index("payload = replay_reader.aplicar_payload(payload, painel_timeframe_atual)")
    indice_sombra = texto.index("payload = anexar_planejamento_sombra_v1(", indice_replay)
    indice_p04b = texto.index("return _finalizar_payload_p04b(payload)", indice_sombra)
    assert indice_replay < indice_sombra < indice_p04b


def test_servidor_preserva_finalizador_p04b():
    root = Path(__file__).resolve().parents[1]
    texto = (root / "backend/server_institucional_v6.py").read_text(encoding="utf-8")
    assert texto.count("return _finalizar_payload_p04b(payload_fallback)") == 1
    assert texto.count("return _finalizar_payload_p04b(payload)") == 1
    assert texto.count("def _finalizar_payload_p04b(payload):") == 1


def test_backend_retorno_sem_historico_contem_sombra(monkeypatch):
    modulo = importlib.import_module("backend.server_institucional_v6")
    monkeypatch.setattr(modulo, "historico", [])
    monkeypatch.setattr(modulo, "atualizar_historico", lambda: None)
    monkeypatch.setattr(modulo.replay_reader, "ativo", False)
    payload = modulo.gerar_payload()
    assert payload["status_backend"] == "SEM_HISTORICO_SUFICIENTE"
    assert payload[CAMPO_SAIDA]["autorizacao"] == "BLOQUEADA"


def test_endpoint_data_expoe_sombra(monkeypatch):
    modulo = importlib.import_module("backend.server_institucional_v6")
    monkeypatch.setattr(modulo, "historico", [])
    monkeypatch.setattr(modulo, "atualizar_historico", lambda: None)
    monkeypatch.setattr(modulo.replay_reader, "ativo", False)
    with TestClient(modulo.app) as cliente:
        resposta = cliente.get("/data")
    assert resposta.status_code == 200
    assert resposta.json()[CAMPO_SAIDA]["autorizacao"] == "BLOQUEADA"


def test_endpoint_ws_expoe_sombra(monkeypatch):
    modulo = importlib.import_module("backend.server_institucional_v6")
    monkeypatch.setattr(modulo, "historico", [])
    monkeypatch.setattr(modulo, "atualizar_historico", lambda: None)
    monkeypatch.setattr(modulo.replay_reader, "ativo", False)
    with TestClient(modulo.app) as cliente:
        with cliente.websocket_connect("/ws") as websocket:
            payload = websocket.receive_json()
    assert payload[CAMPO_SAIDA]["autorizacao"] == "BLOQUEADA"
