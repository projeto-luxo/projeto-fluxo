from __future__ import annotations
from datetime import datetime, timezone
from typing import Protocol

class IRelogioExecucao(Protocol):
    def agora_utc(self) -> str: ...

class RelogioExecucaoReal:
    def agora_utc(self) -> str:
        return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
