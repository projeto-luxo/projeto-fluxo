from pathlib import Path
import pandas as pd


class CalendarioB3:
    def __init__(self):
        trin_root = Path(__file__).resolve().parents[1]
        self.arquivo = trin_root / "TRIN_HISTORICO" / "00_CONFIG" / "calendario_b3_2026.csv"

        self.df = pd.read_csv(
            self.arquivo,
            sep=";",
            encoding="utf-8-sig",
            dtype=str,
            keep_default_na=False,
        )

        obrigatorias = ["data", "tipo", "negociavel", "inicio", "fim", "motivo", "fonte"]
        faltando = [c for c in obrigatorias if c not in self.df.columns]

        if faltando:
            raise ValueError(f"Calendario B3 invalido. Colunas faltando: {faltando}")

    def consultar(self, data):
        data = str(data)
        resultado = self.df[self.df["data"] == data]
        return resultado.to_dict("records")

    def eh_negociavel(self, data):
        eventos = self.consultar(data)

        if not eventos:
            return True

        for evento in eventos:
            if str(evento["negociavel"]).upper() == "NAO":
                return False

        return True

    def eh_feriado(self, data):
        return any(e["tipo"] == "FERIADO_B3" for e in self.consultar(data))

    def horario_especial(self, data):
        for evento in self.consultar(data):
            if evento["tipo"] == "HORARIO_ESPECIAL":
                return {
                    "inicio": evento["inicio"],
                    "fim": evento["fim"],
                    "motivo": evento["motivo"],
                }
        return None


if __name__ == "__main__":
    calendario = CalendarioB3()

    print("=" * 60)
    print("CALENDARIO B3 OK")
    print("=" * 60)
    print("Arquivo:", calendario.arquivo)
    print("Linhas:", len(calendario.df))
    print("Colunas:", list(calendario.df.columns))
    print()
    print("2026-02-16 negociavel?", calendario.eh_negociavel("2026-02-16"))
    print("2026-02-18 horario especial:", calendario.horario_especial("2026-02-18"))