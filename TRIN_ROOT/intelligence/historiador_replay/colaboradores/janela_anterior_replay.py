from __future__ import annotations
from collections import deque
from copy import deepcopy

class JanelaAnteriorReplayV1:
    def __init__(self, limite: int) -> None:
        self._dados = deque(maxlen=limite)
        self._sessao: str | None = None
    def preparar_sessao(self, sessao_id: str) -> bool:
        mudou = self._sessao != sessao_id
        if mudou:
            self._dados.clear(); self._sessao = sessao_id
        return mudou
    def snapshot(self) -> list[dict]:
        return deepcopy(list(self._dados))
    def confirmar(self, evento: dict) -> None:
        self._dados.append(deepcopy(evento))
