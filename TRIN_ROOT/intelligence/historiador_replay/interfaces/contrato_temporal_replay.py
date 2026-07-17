from __future__ import annotations
from typing import Protocol

class IContratoTemporalReplaySomenteLeitura(Protocol):
    contrato_id: str
    versao: str
    timezone: str
    sha256: str
    def validar_identidade(self, contrato_id: str, versao: str, timezone: str) -> None: ...
    def resolver(self, timestamp_iso: str) -> dict: ...
