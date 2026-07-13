from __future__ import annotations

import re
from pathlib import Path
from typing import Any


class FiscalAdapter:
    STATUS_LIBERADOS = {
        "CERTIFICADO",
        "APROVADO",
        "OK",
        "APROVADO_COM_RESSALVAS",
        "RESSALVA",
    }

    STATUS_OFICIAIS = STATUS_LIBERADOS | {
        "REPROVADO",
        "REPROVADO_COM_PENDENCIAS",
    }

    def __init__(self) -> None:
        self.root = Path(__file__).resolve().parents[1]
        self.arquivo = (
            self.root
            / "TRIN_HISTORICO"
            / "00_CERTIFICACOES"
            / "laudo_temporal.txt"
        )

    def _resposta(
        self,
        status: str,
        motivo: str,
        erro: str | None = None,
    ) -> dict[str, Any]:
        status_normalizado = str(status or "DESCONHECIDO").strip().upper()
        aprovado = status_normalizado in self.STATUS_LIBERADOS

        resposta: dict[str, Any] = {
            "status": status_normalizado,
            "aprovado_operacional": aprovado,
            "bloqueio_operacional": not aprovado,
            "motivo": motivo,
            "fonte": "FISCAL_TEMPORAL_LAUDO_OFICIAL",
            "arquivo": str(self.arquivo),
        }

        if erro:
            resposta["erro"] = erro

        return resposta

    def consultar(self) -> dict[str, Any]:
        if not self.arquivo.exists():
            return self._resposta(
                "DESCONHECIDO",
                "LAUDO_FISCAL_INDISPONIVEL",
            )

        try:
            texto = self.arquivo.read_text(
                encoding="utf-8",
                errors="strict",
            ).upper()
        except Exception as erro:
            return self._resposta(
                "ERRO_FISCAL",
                "ERRO_LEITURA_LAUDO_FISCAL",
                str(erro),
            )

        correspondencia = re.search(
            r"(?im)^STATUS FINAL:[ \t]*\r?\n[ \t]*([A-Z_]+)[ \t]*$",
            texto,
        )

        if correspondencia is None:
            return self._resposta(
                "DESCONHECIDO",
                "STATUS_FINAL_NAO_ENCONTRADO_NO_LAUDO",
            )

        status = correspondencia.group(1).strip().upper()

        if status not in self.STATUS_OFICIAIS:
            return self._resposta(
                "DESCONHECIDO",
                f"STATUS_FINAL_NAO_RECONHECIDO:{status}",
            )

        return self._resposta(
            status,
            f"STATUS_FINAL_FISCAL:{status}",
        )


if __name__ == "__main__":
    print("=" * 60)
    print("FISCAL ADAPTER")
    print("=" * 60)
    print(FiscalAdapter().consultar())
