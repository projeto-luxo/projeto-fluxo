import os
import pandas as pd


# ============================================================
# BERNARDO v0.9
# CAÇADOR DE HISTÓRICO
# Busca arquivos por ATIVO + FRACTAL + ANO
# ============================================================

BASE_PATH = r"C:\Users\User\projeto_fluxo\TRIN_HISTORICO"

PASTA_INDICES = os.path.join(BASE_PATH, "00_INDICES")

ATIVO = "WDO"
FRACTAL = "07_30_MIN"
ANO = 2019

ARQUIVO_INDICE = os.path.join(
    PASTA_INDICES,
    f"indice_{ATIVO.lower()}.csv"
)

ARQUIVO_SAIDA = os.path.join(
    PASTA_INDICES,
    "relatorio_consulta_ano.csv"
)


def main():
    print("\n" + "=" * 60)
    print("BERNARDO v0.9 - CACADOR DE HISTORICO")
    print("=" * 60)

    if not os.path.exists(ARQUIVO_INDICE):
        print("Indice nao encontrado:")
        print(ARQUIVO_INDICE)
        return

    df = pd.read_csv(
        ARQUIVO_INDICE,
        sep=";",
        encoding="utf-8-sig"
    )

    df["data_inicio_dt"] = pd.to_datetime(
        df["data_inicio"],
        dayfirst=True,
        errors="coerce"
    )

    df["data_fim_dt"] = pd.to_datetime(
        df["data_fim"],
        dayfirst=True,
        errors="coerce"
    )

    inicio_ano = pd.Timestamp(year=ANO, month=1, day=1)
    fim_ano = pd.Timestamp(year=ANO, month=12, day=31)

    resultado = df[
        (df["fractal"].astype(str).str.upper() == FRACTAL.upper()) &
        (df["data_inicio_dt"] <= fim_ano) &
        (df["data_fim_dt"] >= inicio_ano)
    ].copy()

    resultado = resultado.drop(
        columns=["data_inicio_dt", "data_fim_dt"]
    )

    resultado.to_csv(
        ARQUIVO_SAIDA,
        sep=";",
        index=False,
        encoding="utf-8-sig"
    )

    print(f"ATIVO   : {ATIVO}")
    print(f"FRACTAL : {FRACTAL}")
    print(f"ANO     : {ANO}")

    print("\nArquivos encontrados:")

    for _, linha in resultado.iterrows():
        print(
            f"{linha['arquivo']} | "
            f"{linha['data_inicio']} -> "
            f"{linha['data_fim']} | "
            f"{linha['linhas']} linhas"
        )

    print("\n" + "=" * 60)
    print(f"TOTAL ENCONTRADO : {len(resultado)}")
    print(f"RELATORIO SALVO  : {ARQUIVO_SAIDA}")
    print("=" * 60)


if __name__ == "__main__":
    main()