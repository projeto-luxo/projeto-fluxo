from pathlib import Path
import pandas as pd


class FiscalAdapter:

    def __init__(self):

        self.root = Path(__file__).resolve().parents[1]

        self.arquivo = (
            self.root
            / "TRIN_HISTORICO"
            / "00_CERTIFICACOES"
            / "laudo_temporal.txt"
        )

    def consultar(self):

        if not self.arquivo.exists():

            return {
                "status": "DESCONHECIDO"
            }

        texto = self.arquivo.read_text(
            encoding="utf-8",
            errors="ignore"
        ).upper()

        if "REPROVADO_COM_PENDENCIAS" in texto:
            return {"status": "REPROVADO_COM_PENDENCIAS"}

        if "REPROVADO" in texto:
            return {"status": "REPROVADO"}

        if "APROVADO_COM_RESSALVAS" in texto:
            return {"status": "APROVADO_COM_RESSALVAS"}

        if "CERTIFICADO" in texto:
            return {"status": "CERTIFICADO"}

        return {"status": "DESCONHECIDO"}


if __name__ == "__main__":

    fiscal = FiscalAdapter()

    print("=" * 60)
    print("FISCAL ADAPTER")
    print("=" * 60)

    print(fiscal.consultar())
