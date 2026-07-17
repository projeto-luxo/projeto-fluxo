from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class DetalheFalha:
    codigo: str
    mensagem: str
    experiencia_id: str | None = None


class FalhaConfluenciaReplay(RuntimeError):
    def __init__(
        self,
        codigo: str,
        mensagem: str = "",
        *,
        experiencia_id: str | None = None,
    ) -> None:
        self.codigo = str(codigo)
        self.mensagem = str(mensagem)
        self.experiencia_id = experiencia_id
        texto = self.codigo if not self.mensagem else f"{self.codigo}: {self.mensagem}"
        if experiencia_id:
            texto += f" [experiencia_id={experiencia_id}]"
        super().__init__(texto)

    def como_dict(self) -> dict[str, str | None]:
        return {
            "codigo": self.codigo,
            "motivo": self.mensagem or self.codigo,
            "experiencia_id": self.experiencia_id,
        }
