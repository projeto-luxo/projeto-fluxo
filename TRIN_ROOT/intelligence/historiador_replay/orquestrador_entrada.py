from __future__ import annotations

from datetime import datetime

from .erros import GateReprovado
from .modelos_internos import EnvelopeExecucaoAprovada


class OrquestradorEntradaReplay:
    CERT = "CERTIFICACAO_FISCAL_REPLAY_V2_1.schema.json"
    PACKAGE = "PACOTE_ENTRADA_HISTORIADOR_REPLAY_V2_1.schema.json"
    GATE = "RESPOSTA_GATE_HISTORIADOR_REPLAY_V1_2.schema.json"

    def __init__(self, bernardo, fiscal, temporal, estrutural, semantico) -> None:
        self.bernardo = bernardo
        self.fiscal = fiscal
        self.temporal = temporal
        self.estrutural = estrutural
        self.semantico = semantico

    @staticmethod
    def periodo_valido(periodo: dict) -> bool:
        return datetime.fromisoformat(periodo["inicio"]) <= datetime.fromisoformat(periodo["fim"])

    @staticmethod
    def classificar(periodo: dict, cobertura: dict, parcial_interno: bool = False) -> str:
        if parcial_interno:
            return "PARCIAL_INTERNO"
        inicio = datetime.fromisoformat(periodo["inicio"])
        fim = datetime.fromisoformat(periodo["fim"])
        disponivel_inicio = datetime.fromisoformat(cobertura["inicio_disponivel"])
        disponivel_fim = datetime.fromisoformat(cobertura["fim_disponivel"])
        if fim < disponivel_inicio or inicio > disponivel_fim:
            return "FORA_DA_COBERTURA"
        if inicio < disponivel_inicio:
            return "PARCIAL_BORDA_INICIO"
        if fim > disponivel_fim:
            return "PARCIAL_BORDA_FIM"
        return "INTEGRAL"

    def _gate(self, req, origem, coverage, divergencias, package_id=None):
        partial_allowed = req["politica_cobertura"] == "PERMITIR_BORDA_PARCIAL_DIAGNOSTICA"
        cov_ok = coverage == "INTEGRAL" or (
            coverage in {"PARCIAL_BORDA_INICIO", "PARCIAL_BORDA_FIM"} and partial_allowed
        )
        general = cov_ok and not divergencias
        reason_cov = None if cov_ok else (
            coverage if coverage in {"FORA_DA_COBERTURA", "PARCIAL_INTERNO"}
            else "BORDA_PARCIAL_NAO_PERMITIDA"
        )
        gate = {
            "contrato_resposta": "RespostaGateHistoriadorReplayV1_2",
            "versao": "1.2.0",
            "gate_id": "TRIN-GATE-P03E-001",
            "solicitacao_id": req["solicitacao_id"],
            "origem_id_avaliada": origem["origem_id"],
            "origem_hash_avaliada": origem["sha256"],
            "periodo_solicitado": req["periodo_solicitado"],
            "resultado_gate": "APROVADO" if general else "REPROVADO",
            "nucleo_aberto": general,
            "pacote_id": package_id if general else None,
            "politica_cobertura": req["politica_cobertura"],
            "cobertura_origem": origem["cobertura_origem"],
            "cobertura_periodo_solicitado": coverage,
            "resultado_gate_cobertura": "APROVADO" if cov_ok else "REPROVADO",
            "motivo_gate_cobertura": reason_cov,
            "uso_como_periodo_completo": "PERMITIDO" if coverage == "INTEGRAL" else "PROIBIDO",
            "consumo_operacional": "PERMITIDO" if general and coverage == "INTEGRAL" else "BLOQUEADO",
            "motivo_bloqueio": None if general else (divergencias[0] if divergencias else "COBERTURA_REPROVADA"),
            "divergencias": [] if general else (divergencias or ["COBERTURA_REPROVADA"]),
        }
        self.estrutural.validar_gate(self.GATE, gate)
        return gate

    def preparar(self, req: dict):
        origem = self.bernardo.descrever_origem()
        periodo = req["periodo_solicitado"]
        if not self.periodo_valido(periodo):
            gate = self._gate(req, origem, "INTEGRAL", ["PERIODO_SOLICITADO_INVALIDO"])
            return gate, None

        coverage = self.classificar(periodo, origem["cobertura_origem"], req.get("parcial_interno", False))
        try:
            self.temporal.validar_identidade(
                origem["contrato_temporal"],
                origem["contrato_temporal_versao"],
                origem["timezone_origem"],
            )
        except Exception as exc:
            return self._gate(req, origem, coverage, [getattr(exc, "codigo", type(exc).__name__)]), None

        cert = self.fiscal.certificar(origem)
        try:
            self.estrutural.validar_gate(self.CERT, cert)
        except GateReprovado as exc:
            return self._gate(req, origem, coverage, [exc.codigo]), None

        divergencias = self.semantico.comparar_origem_certificado(origem, cert)
        if cert["decisao"]["decisao_fiscal"] != "APROVADO":
            divergencias.append("FISCAL_REPROVADO")

        package_id = "TRIN-P03E-PACOTE-001"
        gate = self._gate(req, origem, coverage, divergencias, package_id)
        if gate["resultado_gate"] != "APROVADO":
            return gate, None

        package = {
            "contrato": "PacoteEntradaHistoriadorReplayV2_1",
            "versao": "2.1.0",
            "pacote_id": package_id,
            "montado_por": "OrquestradorEntradaReplayV1",
            "origem": origem,
            "solicitacao": {
                "periodo_solicitado": req["periodo_solicitado"],
                "politica_cobertura": req["politica_cobertura"],
                "tamanho_janela": req["tamanho_janela"],
            },
            "fiscal": {"certificado": cert},
            "preflight": {
                "preflight_id": "TRIN-P03E-PREFLIGHT-001",
                "resultado": "APROVADO",
                "comparacoes": {key: True for key in self.semantico.COMPARACOES},
                "cobertura_periodo_solicitado": coverage,
                "resultado_gate_cobertura": "APROVADO",
                "motivo_gate_cobertura": None,
            },
        }
        self.estrutural.validar_gate(self.PACKAGE, package)
        envelope = EnvelopeExecucaoAprovada.criar(package, gate)
        return gate, envelope
