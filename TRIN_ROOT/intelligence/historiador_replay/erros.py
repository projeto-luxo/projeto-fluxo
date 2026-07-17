from __future__ import annotations

class ErroReplay(Exception):
    def __init__(self, codigo: str, detalhe: str = "") -> None:
        self.codigo = codigo
        self.detalhe = detalhe
        super().__init__(f"{codigo}: {detalhe}" if detalhe else codigo)

class GateReprovado(ErroReplay):
    pass

class FalhaReplay(ErroReplay):
    pass

class ViolacaoEscopo(ErroReplay):
    pass
