import pandas as pd
from pathlib import Path

TRIN_ROOT = Path(__file__).resolve().parents[1]

BASE_PATH = TRIN_ROOT / "TRIN_HISTORICO"
PASTA_INDICES = BASE_PATH / "00_INDICES"

ARQUIVO_INDICE_GERAL = PASTA_INDICES / "indice_geral.csv"
ARQUIVO_WIN = PASTA_INDICES / "indice_win.csv"
ARQUIVO_WDO = PASTA_INDICES / "indice_wdo.csv"


def main():
    print("\n" + "=" * 60)
    print("BERNARDO v0.7 - CATALOGADOR MESTRE")
    print("=" * 60)

    print(f"Pasta historico: {BASE_PATH}")
    print(f"Pasta indices  : {PASTA_INDICES}")

    if not ARQUIVO_INDICE_GERAL.exists():
        print("ERRO: indice_geral.csv nao encontrado:")
        print(ARQUIVO_INDICE_GERAL)
        return

    try:
        df = pd.read_csv(
            ARQUIVO_INDICE_GERAL,
            sep=";",
            encoding="utf-8-sig"
        )
    except pd.errors.EmptyDataError:
        print("ERRO: indice_geral.csv esta vazio.")
        return

    if "ativo" not in df.columns:
        print("ERRO: coluna 'ativo' nao encontrada.")
        print("Colunas encontradas:")
        print(list(df.columns))
        return

    df_win = df[df["ativo"].astype(str).str.upper() == "WIN"]
    df_wdo = df[df["ativo"].astype(str).str.upper() == "WDO"]

    if "fractal" in df.columns and "data_inicio" in df.columns:
        df_win = df_win.sort_values(by=["fractal", "data_inicio"])
        df_wdo = df_wdo.sort_values(by=["fractal", "data_inicio"])

    df_win.to_csv(ARQUIVO_WIN, sep=";", index=False, encoding="utf-8-sig")
    df_wdo.to_csv(ARQUIVO_WDO, sep=";", index=False, encoding="utf-8-sig")

    print(f"WIN catalogados : {len(df_win)}")
    print(f"WDO catalogados : {len(df_wdo)}")

    print("\nArquivos gerados:")
    print(ARQUIVO_WIN)
    print(ARQUIVO_WDO)

    print("\n" + "=" * 60)
    print("CATALOGACAO CONCLUIDA")
    print("=" * 60)


if __name__ == "__main__":
    main()