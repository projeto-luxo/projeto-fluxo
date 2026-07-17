from __future__ import annotations
from copy import deepcopy
from typing import Iterable
from .util.json_canonico import json_canonico_bytes
from .util.hash_sha256 import sha256_bytes

class SerializadorContexto:
    SCHEMA = "CONTEXTO_HISTORIADOR_REPLAY_V2_2.schema.json"
    def __init__(self, estrutural, semantico) -> None:
        self.estrutural = estrutural; self.semantico = semantico
    def validar(self, contexto: dict) -> None:
        self.estrutural.validar_replay(self.SCHEMA, contexto); self.semantico.validar_contexto(contexto)
    def serializar(self, contexto: dict) -> bytes:
        self.validar(contexto); return json_canonico_bytes(contexto)
    def impressao_logica(self, contexto: dict) -> str:
        self.validar(contexto); proj = deepcopy(contexto); proj.pop("timestamp_execucao_utc"); return sha256_bytes(json_canonico_bytes(proj))
    def impressao_sequencia(self, contextos: Iterable[dict]) -> str:
        hashes = [self.impressao_logica(c) for c in contextos]
        return sha256_bytes("\n".join(hashes).encode("ascii"))
