import os
import pandas as pd


# ============================================================
# BERNARDO v0.8
# CONSULTOR HISTÓRICO
# ============================================================

BASE_PATH = r"C:\Users\User\projeto_fluxo\TRIN_HISTORICO"

PASTA_INDICES = os.path.join(BASE_PATH, "00_INDICES")

ATIVO = "WIN"
FRACTAL = "06_15_MIN"

ARQUIVO_INDICE = os.path.join(
    PASTA_INDICES,
    f"indice_{ATIVO.lower()}.csv"
)

ARQUIVO_SAIDA = os.path.join(
    PASTA_INDICES,
    "relatorio_consulta.csv"
)


def main():

    print("\n" + "=" * 60)
    print("BERNARDO v0.8 - CONSULTOR HISTORICO")
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

    resultado = df[
        df["fractal"].astype(str).str.upper()
        ==
        FRACTAL.upper()
    ]

    resultado.to_csv(
        ARQUIVO_SAIDA,
        sep=";",
        index=False,
        encoding="utf-8-sig"
    )

    print(f"ATIVO   : {ATIVO}")
    print(f"FRACTAL : {FRACTAL}")

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
    print(f"RELATORIO SALVO : {ARQUIVO_SAIDA}")
    print("=" * 60)


if __name__ == "__main__":
    main()