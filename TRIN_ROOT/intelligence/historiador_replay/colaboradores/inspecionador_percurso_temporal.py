from __future__ import annotations
from datetime import datetime
from ..erros import FalhaReplay
from ..modelos_internos import PlanoPercursoTemporalV1
from .plano_percurso_temporal import calcular_plano_id

class InspecionadorPercursoTemporalV1:
    TAMANHO_BLOCO = 65536
    MAX_LINHA = 65536

    def __init__(self, normalizador) -> None:
        self.normalizador = normalizador

    def inspecionar(self, fonte, pacote: dict, temporal) -> PlanoPercursoTemporalV1:
        h = fonte.handle
        if h is None or h.closed:
            raise FalhaReplay("FONTE_NAO_ABERTA")
        h.seek(0)
        inicio = datetime.fromisoformat(pacote["solicitacao"]["periodo_solicitado"]["inicio"])
        fim = datetime.fromisoformat(pacote["solicitacao"]["periodo_solicitado"]["fim"])
        anterior = None; sinal = None
        total = elegiveis = 0
        primeiro_offset = ultimo_offset = None
        primeiro_ts = ultimo_ts = None
        while True:
            start = h.tell()
            raw = h.readline(self.MAX_LINHA)
            if not raw:
                break
            if len(raw) >= self.MAX_LINHA and not raw.endswith(b"\n"):
                raise FalhaReplay("LINHA_MAIOR_QUE_LIMITE")
            end = h.tell()
            if not raw.strip():
                continue
            total += 1
            evento = self.normalizador.normalizar(raw)
            temporal.resolver(evento["timestamp"])
            ts = datetime.fromisoformat(evento["timestamp"])
            if anterior is not None:
                current_sign = 1 if ts > anterior else (-1 if ts < anterior else 0)
                if current_sign == 0:
                    raise FalhaReplay("TIMESTAMP_DUPLICADO")
                if sinal is None:
                    sinal = current_sign
                elif sinal != current_sign:
                    raise FalhaReplay("ORDEM_MISTA")
            anterior = ts
            if inicio <= ts <= fim:
                elegiveis += 1
                primeiro_offset = start if primeiro_offset is None else min(primeiro_offset, start)
                ultimo_offset = end if ultimo_offset is None else max(ultimo_offset, end)
                iso = ts.isoformat()
                primeiro_ts = iso if primeiro_ts is None or iso < primeiro_ts else primeiro_ts
                ultimo_ts = iso if ultimo_ts is None or iso > ultimo_ts else ultimo_ts
        if total == 0:
            raise FalhaReplay("ORIGEM_SEM_EVENTOS")
        if elegiveis == 0 or primeiro_offset is None or ultimo_offset is None:
            raise FalhaReplay("ZERO_EVENTOS_ELEGIVEIS")
        ordem = "CRESCENTE" if sinal in (None, 1) else "DECRESCENTE"
        fp = fonte.fingerprint_inicial
        if fp is None:
            raise FalhaReplay("FONTE_SEM_FINGERPRINT")
        data = {
            "origem_id": pacote["origem"]["origem_id"], "origem_hash": pacote["origem"]["sha256"],
            "fonte_selada_id": fp.fonte_selada_id, "contrato_temporal_id": temporal.contrato_id,
            "contrato_temporal_versao": temporal.versao, "contrato_temporal_hash": temporal.sha256,
            "ordem_fisica": ordem, "estrategia_leitura": "DIRETA_CRESCENTE" if ordem == "CRESCENTE" else "REVERSA_BLOCOS",
            "periodo_solicitado": pacote["solicitacao"]["periodo_solicitado"],
            "inicio_elegivel": primeiro_ts, "fim_elegivel": ultimo_ts,
            "primeiro_offset": primeiro_offset, "ultimo_offset": ultimo_offset,
            "total_linhas_fisicas": total, "total_eventos_elegiveis": elegiveis,
            "primeiro_timestamp": primeiro_ts, "ultimo_timestamp": ultimo_ts,
            "tamanho_bloco": self.TAMANHO_BLOCO, "resultado_inspecao": "APROVADO", "motivo_reprovacao": None,
        }
        return PlanoPercursoTemporalV1(plano_id=calcular_plano_id(data), **data)
