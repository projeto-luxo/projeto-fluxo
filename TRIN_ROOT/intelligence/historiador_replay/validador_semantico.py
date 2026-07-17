from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

from .colaboradores.plano_percurso_temporal import validar_plano_id
from .erros import FalhaReplay


class ValidadorSemantico:
    COMPARACOES = (
        "origem_id", "arquivo", "caminho_relativo_biblioteca", "sha256",
        "ativo_fisico", "familia_ativo", "fractal", "schema_origem",
        "periodo_certificado", "cobertura_origem", "contrato_temporal",
        "contrato_temporal_versao", "timezone_origem", "convencao_timestamp",
        "tipo_certificacao", "escopo_certificacao", "nao_equivale_a", "evidencia_sha256",
    )

    def comparar_origem_certificado(self, origem: dict, cert: dict) -> list[str]:
        c = cert["origem_certificada"]
        pairs = {
            "origem_id": (origem["origem_id"], c["origem_id"]),
            "arquivo": (origem["arquivo"], c["arquivo"]),
            "caminho_relativo_biblioteca": (origem["caminho_relativo_biblioteca"], c["caminho_relativo_biblioteca"]),
            "sha256": (origem["sha256"], c["sha256_origem"]),
            "ativo_fisico": (origem["ativo_fisico"], c["ativo_fisico"]),
            "familia_ativo": (origem["familia_ativo"], c["familia_ativo"]),
            "fractal": (origem["fractal"], c["fractal"]),
            "schema_origem": (origem["schema_origem"], c["schema_origem"]),
            "periodo_certificado": (origem["periodo_disponivel"], c["periodo_certificado"]),
            "cobertura_origem": (origem["cobertura_origem"], c["cobertura_origem"]),
            "contrato_temporal": (origem["contrato_temporal"], c["contrato_temporal"]),
            "contrato_temporal_versao": (origem["contrato_temporal_versao"], c["contrato_temporal_versao"]),
            "timezone_origem": (origem["timezone_origem"], c["timezone_origem"]),
            "convencao_timestamp": (origem["convencao_timestamp"], c["convencao_timestamp"]),
            "tipo_certificacao": (cert["tipo_certificacao"], "CERTIFICACAO_CONTROLADA_DA_ORIGEM_NO_ESCOPO_PACOTE_02"),
            "escopo_certificacao": (cert["escopo_certificacao"], "HISTORIADOR_REPLAY_TESTE_CONTROLADO_WIN_1MIN_2026"),
            "nao_equivale_a": (cert["nao_equivale_a"], "FISCAL_4_2_3_PERMANENTE_HOMOLOGADO"),
            "evidencia_sha256": (len(cert["evidencia_sha256"]), 64),
        }
        return [key for key, (left, right) in pairs.items() if left != right]

    def validar_envelope(self, envelope, pacote: dict, gate: dict) -> None:
        envelope.verificar_integridade()
        if gate["resultado_gate"] != "APROVADO" or gate["nucleo_aberto"] is not True:
            raise FalhaReplay("GATE_NAO_APROVADO")
        if gate["motivo_bloqueio"] is not None or gate["divergencias"]:
            raise FalhaReplay("GATE_COM_BLOQUEIO")
        if gate["pacote_id"] != pacote["pacote_id"] or gate["pacote_id"] != envelope.pacote_id:
            raise FalhaReplay("PACOTE_ID_DIVERGENTE")
        if gate["solicitacao_id"] != envelope.solicitacao_id:
            raise FalhaReplay("SOLICITACAO_ID_DIVERGENTE")
        if gate["origem_id_avaliada"] != pacote["origem"]["origem_id"]:
            raise FalhaReplay("GATE_ORIGEM_ID_DIVERGENTE")
        if gate["origem_hash_avaliada"] != pacote["origem"]["sha256"]:
            raise FalhaReplay("GATE_ORIGEM_HASH_DIVERGENTE")
        if gate["periodo_solicitado"] != pacote["solicitacao"]["periodo_solicitado"]:
            raise FalhaReplay("GATE_PERIODO_DIVERGENTE")
        if gate["politica_cobertura"] != pacote["solicitacao"]["politica_cobertura"]:
            raise FalhaReplay("GATE_POLITICA_DIVERGENTE")

        preflight = pacote["preflight"]
        if preflight["resultado"] != "APROVADO":
            raise FalhaReplay("PREFLIGHT_REPROVADO")
        if set(preflight["comparacoes"]) != set(self.COMPARACOES):
            raise FalhaReplay("PREFLIGHT_COMPARACOES_INCOMPLETAS")
        if any(value is not True for value in preflight["comparacoes"].values()):
            raise FalhaReplay("PREFLIGHT_COMPARACAO_REPROVADA")
        if preflight["resultado_gate_cobertura"] != "APROVADO" or preflight["motivo_gate_cobertura"] is not None:
            raise FalhaReplay("PREFLIGHT_COBERTURA_REPROVADA")
        if preflight["cobertura_periodo_solicitado"] != gate["cobertura_periodo_solicitado"]:
            raise FalhaReplay("PREFLIGHT_COBERTURA_DIVERGENTE")

        cert = pacote["fiscal"]["certificado"]
        decision = cert["decisao"]
        if decision["decisao_fiscal"] != "APROVADO":
            raise FalhaReplay("FISCAL_REPROVADO")
        if decision["motivo_bloqueio"] is not None:
            raise FalhaReplay("FISCAL_COM_MOTIVO_BLOQUEADOR")
        if decision["ordens_pendentes"]:
            raise FalhaReplay("FISCAL_COM_ORDEM_PENDENTE")
        if decision["criticidade"] not in {None, "INFORMATIVA"}:
            raise FalhaReplay("FISCAL_COM_CRITICIDADE_BLOQUEADORA")
        if self.comparar_origem_certificado(pacote["origem"], cert):
            raise FalhaReplay("PACOTE_CERTIFICADO_DIVERGENTE")

        periodo = pacote["solicitacao"]["periodo_solicitado"]
        if datetime.fromisoformat(periodo["inicio"]) > datetime.fromisoformat(periodo["fim"]):
            raise FalhaReplay("PERIODO_SOLICITADO_INVALIDO")

    def validar_plano(self, plano, pacote: dict, temporal) -> None:
        validar_plano_id(plano)
        if plano.resultado_inspecao != "APROVADO":
            raise FalhaReplay("PLANO_REPROVADO")
        if plano.origem_id != pacote["origem"]["origem_id"] or plano.origem_hash != pacote["origem"]["sha256"]:
            raise FalhaReplay("PLANO_ORIGEM_DIVERGENTE")
        if plano.contrato_temporal_id != temporal.contrato_id or plano.contrato_temporal_hash != temporal.sha256:
            raise FalhaReplay("PLANO_TEMPORAL_DIVERGENTE")
        if plano.tamanho_bloco != 65536:
            raise FalhaReplay("PLANO_BLOCO_DIVERGENTE")
        if plano.primeiro_offset < 0 or plano.ultimo_offset <= plano.primeiro_offset:
            raise FalhaReplay("PLANO_OFFSETS_INVALIDOS")

    @staticmethod
    def _timestamp_de_data_hora(evento: dict, timezone_name: str) -> datetime:
        try:
            local = datetime.strptime(
                f'{evento["data"]} {evento["hora"]}',
                "%d/%m/%Y %H:%M:%S",
            ).replace(tzinfo=ZoneInfo(timezone_name))
        except Exception as exc:
            raise FalhaReplay("DATA_HORA_INVALIDAS") from exc
        return local

    def validar_contexto(self, ctx: dict) -> None:
        if ctx["ordinal_evento"] > ctx["total_eventos"]:
            raise FalhaReplay("ORDINAL_MAIOR_QUE_TOTAL")
        if ctx["timestamp_evento"] != ctx["evento_atual"]["timestamp"]:
            raise FalhaReplay("TIMESTAMP_DIVERGENTE")

        factual = datetime.fromisoformat(ctx["evento_atual"]["timestamp"])
        reconstruido = self._timestamp_de_data_hora(ctx["evento_atual"], ctx["timezone_origem"])
        if reconstruido != factual:
            raise FalhaReplay("DATA_HORA_TIMESTAMP_DIVERGENTES")

        esperado_cursor = f'{ctx["origem_hash"]}:{ctx["ordinal_evento"]}'
        if ctx["cursor"] != esperado_cursor:
            raise FalhaReplay("CURSOR_ATUAL_INCOERENTE")

        if len(ctx["janela_anterior"]) > ctx["tamanho_janela"]:
            raise FalhaReplay("JANELA_MAIOR_QUE_LIMITE")
        current = datetime.fromisoformat(ctx["timestamp_evento"])
        for event in ctx["janela_anterior"]:
            if self._timestamp_de_data_hora(event, ctx["timezone_origem"]) != datetime.fromisoformat(event["timestamp"]):
                raise FalhaReplay("JANELA_DATA_HORA_TIMESTAMP_DIVERGENTES")
            if datetime.fromisoformat(event["timestamp"]) >= current:
                raise FalhaReplay("EVENTO_ATUAL_OU_FUTURO_NA_JANELA")

        if ctx["fim"] and ctx["ordinal_evento"] != ctx["total_eventos"]:
            raise FalhaReplay("FIM_ANTES_DO_ULTIMO")
        if ctx["estado_replay"] == "CONCLUIDO" and ctx["cobertura_periodo_solicitado"] != "INTEGRAL":
            raise FalhaReplay("CONCLUSAO_INTEGRAL_INCOERENTE")
        if ctx["estado_replay"] == "CONCLUIDO_PARCIAL" and ctx["cobertura_periodo_solicitado"] not in {"PARCIAL_BORDA_INICIO", "PARCIAL_BORDA_FIM"}:
            raise FalhaReplay("CONCLUSAO_PARCIAL_INCOERENTE")

        ultimo = ctx["ordinal_evento"] == ctx["total_eventos"]
        esperado_proximo = None if ultimo else f'{ctx["origem_hash"]}:{ctx["ordinal_evento"] + 1}'
        if ctx["proximo_cursor"] != esperado_proximo:
            raise FalhaReplay("PROXIMO_CURSOR_INCOERENTE")

        token = ctx["token_retomada"]
        if ctx["estado_replay"] == "PAUSADO":
            if token is None:
                raise FalhaReplay("PAUSA_SEM_TOKEN")
            if token["proximo_ordinal"] != ctx["ordinal_evento"] + 1:
                raise FalhaReplay("TOKEN_ORDINAL_INCOERENTE")
            if token["ultimo_timestamp_entregue"] != ctx["timestamp_evento"]:
                raise FalhaReplay("TOKEN_TIMESTAMP_INCOERENTE")
            if ctx["proximo_cursor"] != f'{ctx["origem_hash"]}:{token["proximo_ordinal"]}':
                raise FalhaReplay("TOKEN_CURSOR_INCOERENTE")
        elif token is not None:
            raise FalhaReplay("TOKEN_FORA_DE_PAUSA")

        if ctx["cobertura_periodo_solicitado"] != "INTEGRAL" and ctx["consumo_operacional"] != "BLOQUEADO":
            raise FalhaReplay("PARCIAL_OPERACIONAL_LIBERADO")
