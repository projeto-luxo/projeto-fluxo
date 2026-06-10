import os
import pandas as pd


# ============================================================
# BERNARDO v1.1.1
# INSPETOR DA MEMÓRIA VIVA
# ============================================================

PASTA_MEMORIA = r"C:\Users\User\projeto_fluxo\memoria"

COLUNAS_OBRIGATORIAS = [
    "ativo",
    "data",
    "hora",
    "ultimo",
    "volume",
    "delta",
    "saldo",
    "vwap"
]


def analisar_csv(caminho):

    try:

        df = pd.read_csv(
            caminho,
            sep=";",
            engine="python"
        )

        colunas = list(df.columns)

        faltando = []

        for coluna in COLUNAS_OBRIGATORIAS:
            if coluna not in colunas:
                faltando.append(coluna)

        ativo = "N/D"

        if "ativo" in colunas and len(df) > 0:
            ativo = str(df["ativo"].iloc[0])

        data_inicial = "N/D"
        data_final = "N/D"

        if "data" in colunas and len(df) > 0:
            data_inicial = str(df["data"].iloc[0])
            data_final = str(df["data"].iloc[-1])

        return {
            "arquivo": os.path.basename(caminho),
            "linhas": len(df),
            "ativo": ativo,
            "data_inicial": data_inicial,
            "data_final": data_final,
            "colunas": len(colunas),
            "faltando": ", ".join(faltando) if faltando else "NENHUMA",
            "status": "OK"
        }

    except Exception as erro:

        return {
            "arquivo": os.path.basename(caminho),
            "linhas": 0,
            "ativo": "ERRO",
            "data_inicial": "N/D",
            "data_final": "N/D",
            "colunas": 0,
            "faltando": "N/D",
            "status": str(erro)
        }


def main():

    print("\n" + "=" * 60)
    print("BERNARDO v1.1.1 - INSPETOR DA MEMORIA VIVA")
    print("=" * 60)

    for arquivo in sorted(os.listdir(PASTA_MEMORIA)):

        if arquivo.lower().startswith("relatorio_"):
            continue

        if not arquivo.lower().endswith(".csv"):
            continue

        resultado = analisar_csv(
            os.path.join(PASTA_MEMORIA, arquivo)
        )

        print("\n" + "-" * 60)

        print(f"Arquivo      : {resultado['arquivo']}")
        print(f"Ativo        : {resultado['ativo']}")
        print(f"Linhas       : {resultado['linhas']}")
        print(f"Colunas      : {resultado['colunas']}")
        print(f"Data inicial : {resultado['data_inicial']}")
        print(f"Data final   : {resultado['data_final']}")
        print(f"Faltando     : {resultado['faltando']}")
        print(f"Status       : {resultado['status']}")

    print("\n" + "=" * 60)
    print("INSPECAO CONCLUIDA")
    print("=" * 60)


if __name__ == "__main__":
    main()