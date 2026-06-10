import os
import pandas as pd


# ============================================================
# BERNARDO v1.1
# FISCAL DA MEMÓRIA VIVA
# ============================================================

PASTA_MEMORIA = r"C:\Users\User\projeto_fluxo\memoria"

ARQUIVO_RELATORIO = os.path.join(
    PASTA_MEMORIA,
    "relatorio_memoria_viva.csv"
)


def analisar_csv(caminho):

    try:
        df = pd.read_csv(
            caminho,
            sep=";",
            engine="python"
        )

        linhas = len(df)

        return {
            "arquivo": os.path.basename(caminho),
            "linhas": linhas,
            "colunas": len(df.columns),
            "status": "OK"
        }

    except Exception as erro:

        return {
            "arquivo": os.path.basename(caminho),
            "linhas": 0,
            "colunas": 0,
            "status": f"ERRO: {erro}"
        }


def main():

    print("\n" + "=" * 60)
    print("BERNARDO v1.1 - FISCAL DA MEMORIA VIVA")
    print("=" * 60)

    registros = []

    for arquivo in sorted(os.listdir(PASTA_MEMORIA)):

        if not arquivo.lower().endswith(".csv"):
            continue

        caminho = os.path.join(
            PASTA_MEMORIA,
            arquivo
        )

        resultado = analisar_csv(caminho)

        registros.append(resultado)

        print(
            f"{resultado['arquivo']} | "
            f"{resultado['linhas']} linhas | "
            f"{resultado['colunas']} colunas | "
            f"{resultado['status']}"
        )

    df = pd.DataFrame(registros)

    df.to_csv(
        ARQUIVO_RELATORIO,
        sep=";",
        index=False,
        encoding="utf-8-sig"
    )

    print("\n" + "=" * 60)
    print("RESUMO MEMORIA VIVA")
    print("=" * 60)

    print(f"Arquivos analisados : {len(df)}")

    if len(df) > 0:
        print(f"Total registros     : {df['linhas'].sum()}")

    print(f"Relatorio salvo em  : {ARQUIVO_RELATORIO}")

    print("=" * 60)


if __name__ == "__main__":
    main()