import os
import pandas as pd


# ============================================================
# BERNARDO v1.0
# GUARDIÃO DA MEMÓRIA
# ============================================================

BASE_PATH = r"C:\Users\User\projeto_fluxo\TRIN_HISTORICO"

PASTA_INDICES = os.path.join(
    BASE_PATH,
    "00_INDICES"
)

ARQUIVO_WIN = os.path.join(
    PASTA_INDICES,
    "indice_win.csv"
)

ARQUIVO_WDO = os.path.join(
    PASTA_INDICES,
    "indice_wdo.csv"
)

ARQUIVO_SAIDA = os.path.join(
    PASTA_INDICES,
    "relatorio_memoria.csv"
)


def carregar_indice(caminho):

    if not os.path.exists(caminho):
        return pd.DataFrame()

    return pd.read_csv(
        caminho,
        sep=";",
        encoding="utf-8-sig"
    )


def resumir(df, ativo):

    if len(df) == 0:
        return None

    datas_inicio = pd.to_datetime(
        df["data_inicio"],
        dayfirst=True,
        errors="coerce"
    )

    datas_fim = pd.to_datetime(
        df["data_fim"],
        dayfirst=True,
        errors="coerce"
    )

    return {
        "ativo": ativo,
        "arquivos": len(df),
        "linhas": int(df["linhas"].sum()),
        "primeira_data": datas_inicio.min().strftime("%d/%m/%Y"),
        "ultima_data": datas_fim.max().strftime("%d/%m/%Y")
    }


def main():

    print("\n" + "=" * 60)
    print("BERNARDO v1.0 - GUARDIAO DA MEMORIA")
    print("=" * 60)

    df_win = carregar_indice(ARQUIVO_WIN)
    df_wdo = carregar_indice(ARQUIVO_WDO)

    resumo_win = resumir(df_win, "WIN")
    resumo_wdo = resumir(df_wdo, "WDO")

    relatorio = []

    if resumo_win:
        relatorio.append(resumo_win)

    if resumo_wdo:
        relatorio.append(resumo_wdo)

    df_saida = pd.DataFrame(relatorio)

    df_saida.to_csv(
        ARQUIVO_SAIDA,
        sep=";",
        index=False,
        encoding="utf-8-sig"
    )

    print("\nMEMORIA WIN")

    if resumo_win:
        print(f"Arquivos      : {resumo_win['arquivos']}")
        print(f"Linhas        : {resumo_win['linhas']}")
        print(f"Primeira data : {resumo_win['primeira_data']}")
        print(f"Ultima data   : {resumo_win['ultima_data']}")

    print("\nMEMORIA WDO")

    if resumo_wdo:
        print(f"Arquivos      : {resumo_wdo['arquivos']}")
        print(f"Linhas        : {resumo_wdo['linhas']}")
        print(f"Primeira data : {resumo_wdo['primeira_data']}")
        print(f"Ultima data   : {resumo_wdo['ultima_data']}")

    print("\n" + "=" * 60)
    print("PATRIMONIO HISTORICO CATALOGADO")
    print("=" * 60)
    print(f"Relatorio salvo em:")
    print(ARQUIVO_SAIDA)
    print("=" * 60)


if __name__ == "__main__":
    main()