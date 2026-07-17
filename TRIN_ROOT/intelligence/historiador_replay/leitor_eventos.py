from __future__ import annotations
from contextlib import contextmanager
from datetime import datetime
from typing import BinaryIO, Iterator
from .erros import FalhaReplay
from .colaboradores.inspecionador_percurso_temporal import InspecionadorPercursoTemporalV1
from .colaboradores.normalizador_evento_profit import NormalizadorEventoProfitV1

class LeitorEventos:
    def __init__(self, bernardo, semantico, normalizador: NormalizadorEventoProfitV1 | None = None) -> None:
        self.bernardo=bernardo; self.semantico=semantico; self.normalizador=normalizador or NormalizadorEventoProfitV1(); self.inspecionador=InspecionadorPercursoTemporalV1(self.normalizador)
    @contextmanager
    def preparar(self, pacote: dict, temporal):
        fonte = self.bernardo.abrir_fonte(pacote["origem"]["origem_id"])
        with fonte:
            inicial=fonte.verificar(pacote["origem"]["sha256"],pacote["origem"]["bytes"])
            plano=self.inspecionador.inspecionar(fonte,pacote,temporal)
            self.semantico.validar_plano(plano,pacote,temporal)
            fonte.verificar(plano.origem_hash,pacote["origem"]["bytes"],plano.fonte_selada_id)
            yield fonte,plano
            fonte.verificar(plano.origem_hash,pacote["origem"]["bytes"],plano.fonte_selada_id)
    @staticmethod
    def _linhas_reversas(handle: BinaryIO, start: int, end: int, block: int) -> Iterator[bytes]:
        position=end; buffer=b""
        while position>start:
            size=min(block,position-start); position-=size; handle.seek(position); chunk=handle.read(size)
            if len(chunk)!=size: raise FalhaReplay("LEITURA_REVERSA_INCOMPLETA")
            buffer=chunk+buffer; parts=buffer.split(b"\n"); buffer=parts[0]
            for line in reversed(parts[1:]):
                line=line.rstrip(b"\r")
                if line: yield line
        remaining=buffer.rstrip(b"\r\n")
        if remaining: yield remaining
    def iterar(self, fonte, plano) -> Iterator[dict]:
        h=fonte.handle
        if h is None or h.closed: raise FalhaReplay("FONTE_NAO_ABERTA")
        count=0
        if plano.ordem_fisica=="CRESCENTE":
            h.seek(plano.primeiro_offset)
            while h.tell()<plano.ultimo_offset:
                raw=h.readline(65536)
                if not raw: break
                if raw.strip():
                    count+=1; yield self.normalizador.normalizar(raw)
        else:
            for raw in self._linhas_reversas(h,plano.primeiro_offset,plano.ultimo_offset,plano.tamanho_bloco):
                count+=1; yield self.normalizador.normalizar(raw)
        if count!=plano.total_eventos_elegiveis: raise FalhaReplay("TOTAL_EVENTOS_DIVERGENTE")
