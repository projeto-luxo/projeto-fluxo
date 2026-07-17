from __future__ import annotations
class ResolvedorSessaoReplayV1:
    def __init__(self, contrato_temporal) -> None:
        self.contrato_temporal = contrato_temporal
    def resolver(self, timestamp: str) -> dict:
        return self.contrato_temporal.resolver(timestamp)
