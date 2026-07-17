from __future__ import annotations

from .colaboradores.janela_anterior_replay import JanelaAnteriorReplayV1
from .colaboradores.resolvedor_sessao_replay import ResolvedorSessaoReplayV1
from .cursor_replay import CursorReplay
from .erros import FalhaReplay
from .modelos_internos import EnvelopeExecucaoAprovada, EstadoReplay


class NucleoHistoriadorReplay:
    PACKAGE_SCHEMA = "PACOTE_ENTRADA_HISTORIADOR_REPLAY_V2_1.schema.json"
    GATE_SCHEMA = "RESPOSTA_GATE_HISTORIADOR_REPLAY_V1_2.schema.json"

    def __init__(self, leitor, temporal, relogio, serializador, semantico, estrutural) -> None:
        self.leitor = leitor
        self.temporal = temporal
        self.relogio = relogio
        self.serializador = serializador
        self.semantico = semantico
        self.estrutural = estrutural
        self.estado = EstadoReplay.NAO_INICIADO

    def _revalidar_envelope(self, envelope: EnvelopeExecucaoAprovada) -> tuple[dict, dict]:
        if not isinstance(envelope, EnvelopeExecucaoAprovada):
            raise FalhaReplay("ENVELOPE_EXECUCAO_OBRIGATORIO")
        envelope.verificar_integridade()
        pacote = envelope.pacote_dict()
        gate = envelope.gate_dict()
        self.estrutural.validar_replay(self.PACKAGE_SCHEMA, pacote)
        self.estrutural.validar_replay(self.GATE_SCHEMA, gate)
        self.semantico.validar_envelope(envelope, pacote, gate)
        return pacote, gate

    def iterar_contextos(self, envelope: EnvelopeExecucaoAprovada, *, pausar_apos: int | None = None, token_retomada: dict | None = None):
        try:
            pacote, _gate = self._revalidar_envelope(envelope)
            self.estado = EstadoReplay.PRONTO
            with self.leitor.preparar(pacote, self.temporal) as (fonte, plano):
                self.semantico.validar_plano(plano, pacote, self.temporal)
                cursor = CursorReplay(
                    pacote["origem"]["sha256"],
                    pacote["solicitacao"]["periodo_solicitado"],
                    pacote["solicitacao"]["politica_cobertura"],
                    pacote["solicitacao"]["tamanho_janela"],
                    plano.total_eventos_elegiveis,
                    self.estrutural,
                )
                start = 1
                if token_retomada is not None:
                    start = cursor.validar_token(token_retomada)

                janela = JanelaAnteriorReplayV1(pacote["solicitacao"]["tamanho_janela"])
                sessao_resolver = ResolvedorSessaoReplayV1(self.temporal)
                self.estado = EstadoReplay.EM_CURSO
                timestamp_anterior: str | None = None
                token_factual_validado = token_retomada is None

                for ordinal, event in enumerate(self.leitor.iterar(fonte, plano), start=1):
                    sessao = sessao_resolver.resolver(event["timestamp"])
                    mudou = janela.preparar_sessao(sessao["sessao_id"])

                    if ordinal < start:
                        timestamp_anterior = event["timestamp"]
                        janela.confirmar(event)
                        continue

                    if token_retomada is not None and not token_factual_validado:
                        cursor.validar_timestamp_anterior(token_retomada, timestamp_anterior)
                        token_factual_validado = True

                    is_last = ordinal == plano.total_eventos_elegiveis
                    coverage = pacote["preflight"]["cobertura_periodo_solicitado"]
                    if pausar_apos == ordinal and not is_last:
                        state = EstadoReplay.PAUSADO
                        fim = False
                        prox = cursor.proximo(ordinal)
                        token = cursor.criar_token(ordinal + 1, event["timestamp"])
                    elif is_last:
                        state = EstadoReplay.CONCLUIDO if coverage == "INTEGRAL" else EstadoReplay.CONCLUIDO_PARCIAL
                        fim = True
                        prox = None
                        token = None
                    else:
                        state = EstadoReplay.EM_CURSO
                        fim = False
                        prox = cursor.proximo(ordinal)
                        token = None

                    janela_anterior = janela.snapshot()
                    contexto = {
                        "contrato_contexto": "ContextoHistoriadorReplayV2_2",
                        "versao": "2.2.0",
                        "solicitacao_id": envelope.solicitacao_id,
                        "origem_id": pacote["origem"]["origem_id"],
                        "origem_caminho": pacote["origem"]["caminho_relativo_biblioteca"],
                        "origem_hash": pacote["origem"]["sha256"],
                        "schema_origem": pacote["origem"]["schema_origem"],
                        "ativo_fisico": pacote["origem"]["ativo_fisico"],
                        "familia_ativo": pacote["origem"]["familia_ativo"],
                        "fractal": pacote["origem"]["fractal"],
                        "periodo_solicitado": pacote["solicitacao"]["periodo_solicitado"],
                        "cobertura_origem": pacote["origem"]["cobertura_origem"],
                        "cobertura_periodo_solicitado": coverage,
                        "politica_cobertura": pacote["solicitacao"]["politica_cobertura"],
                        "uso_como_periodo_completo": "PERMITIDO" if coverage == "INTEGRAL" else "PROIBIDO",
                        "consumo_operacional": "PERMITIDO" if coverage == "INTEGRAL" else "BLOQUEADO",
                        "tamanho_janela": pacote["solicitacao"]["tamanho_janela"],
                        "decisao_fiscal": pacote["fiscal"]["certificado"]["decisao"]["decisao_fiscal"],
                        "certificado_id": pacote["fiscal"]["certificado"]["certificado_id"],
                        "contrato_temporal": pacote["origem"]["contrato_temporal"],
                        "contrato_temporal_versao": pacote["origem"]["contrato_temporal_versao"],
                        "timestamp_evento": event["timestamp"],
                        "timezone_origem": pacote["origem"]["timezone_origem"],
                        "convencao_timestamp": pacote["origem"]["convencao_timestamp"],
                        "cursor": cursor.cursor(ordinal),
                        "ordinal_evento": ordinal,
                        "total_eventos": plano.total_eventos_elegiveis,
                        "sessao": {"sessao_id": sessao["sessao_id"], "mudou_sessao": mudou},
                        "evento_atual": event,
                        "janela_anterior": janela_anterior,
                        "estado_replay": str(state),
                        "fim": fim,
                        "proximo_cursor": prox,
                        "token_retomada": token,
                        "timestamp_execucao_utc": self.relogio.agora_utc(),
                    }
                    self.serializador.validar(contexto)

                    # A transição é confirmada antes da entrega.
                    janela.confirmar(event)
                    self.estado = state
                    yield contexto
                    if state == EstadoReplay.PAUSADO:
                        return

                if token_retomada is not None and not token_factual_validado:
                    raise FalhaReplay("TOKEN_ORDINAL_SEM_EVENTO")
        except Exception:
            if self.estado not in {EstadoReplay.NAO_INICIADO, EstadoReplay.GATE_REPROVADO}:
                self.estado = EstadoReplay.FALHA
            else:
                self.estado = EstadoReplay.FALHA
            raise
