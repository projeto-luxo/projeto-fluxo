import os
import pandas as pd


# ============================================================
# BERNARDO v0.7
# CATALOGADOR MESTRE
# ============================================================

BASE_PATH = r"C:\Users\User\projeto_fluxo\TRIN_HISTORICO"

PASTA_INDICES = os.path.join(BASE_PATH, "00_INDICES")

ARQUIVO_INDICE_GERAL = os.path.join(
    PASTA_INDICES,
    "indice_geral.csv"
)

ARQUIVO_WIN = os.path.join(
    PASTA_INDICES,
    "indice_win.csv"
)

ARQUIVO_WDO = os.path.join(
    PASTA_INDICES,
    "indice_wdo.csv"
)


def main():

    print("\n" + "=" * 60)
    print("BERNARDO v0.7 - CATALOGADOR MESTRE")
    print("=" * 60)

    df = pd.read_csv(
        ARQUIVO_INDICE_GERAL,
        sep=";",
        encoding="utf-8-sig"
    )

    df_win = df[df["ativo"] == "WIN"]
    df_wdo = df[df["ativo"] == "WDO"]

    df_win = df_win.sort_values(
        by=["fractal", "data_inicio"]
    )

    df_wdo = df_wdo.sort_values(
        by=["fractal", "data_inicio"]
    )

    df_win.to_csv(
        ARQUIVO_WIN,
        sep=";",
        index=False,
        encoding="utf-8-sig"
    )

    df_wdo.to_csv(
        ARQUIVO_WDO,
        sep=";",
        index=False,
        encoding="utf-8-sig"
    )

    print(f"WIN catalogados : {len(df_win)}")
    print(f"WDO catalogados : {len(df_wdo)}")

    print("\nArquivos gerados:")

    print(ARQUIVO_WIN)
    print(ARQUIVO_WDO)

    print("\n" + "=" * 60)
    print("CATALOGAÇÃO CONCLUÍDA")
    print("=" * 60)


if __name__ == "__main__":
    main()