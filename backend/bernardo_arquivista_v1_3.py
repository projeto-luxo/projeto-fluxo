import os
import pandas as pd


# ============================================================
# BERNARDO v1.3
# ARQUIVISTA
# Decide se deve arquivar ou não
# ============================================================

PASTA_MEMORIA = r"C:\Users\User\projeto_fluxo\memoria"
PASTA_HISTORICO = r"C:\Users\User\projeto_fluxo\TRIN_HISTORICO"
PASTA_INDICES = os.path.join(PASTA_HISTORICO, "00_INDICES")

ARQUIVO_MEMORIA_HISTORICA = os.path.join(
    PASTA_INDICES,
    "relatorio_memoria.csv"
)

ARQUIVO_SAIDA = os.path.join(
    PASTA_INDICES,
    "relatorio_arquivamento.csv"
)


def carregar_memoria_historica():
    if not os.path.exists(ARQUIVO_MEMORIA_HISTORICA):
        return pd.DataFrame()

    return pd.read_csv(
        ARQUIVO_MEMORIA_HISTORICA,
        sep=";",
        encoding="utf-8-sig"
    )


def analisar_memoria_viva():
    registros = []

    for arquivo in sorted(os.listdir(PASTA_MEMORIA)):

        if not arquivo.lower().endswith(".csv"):
            continue

        if not arquivo.startswith("TRIN_MEMORIA_"):
            continue

        caminho = os.path.join(PASTA_MEMORIA, arquivo)

        try:

            df = pd.read_csv(
                caminho,
                sep=";",
                engine="python"
            )

            ativo = "N/D"
            data_inicio = "N/D"
            data_fim = "N/D"

            if "ativo" in df.columns and len(df) > 0:
                ativo = str(df["ativo"].iloc[0])

            if "data" in df.columns and len(df) > 0:

                datas = pd.to_datetime(
                    df["data"],
                    dayfirst=True,
                    errors="coerce"
                ).dropna()

                if len(datas) > 0:
                    data_inicio = datas.min().strftime("%d/%m/%Y")
                    data_fim = datas.max().strftime("%d/%m/%Y")

            registros.append({
                "arquivo_memoria": arquivo,
                "ativo_vivo": ativo,
                "linhas_vivas": len(df),
                "data_inicio_viva": data_inicio,
                "data_fim_viva": data_fim,
                "status_leitura": "OK"
            })

        except Exception as erro:

            registros.append({
                "arquivo_memoria": arquivo,
                "ativo_vivo": "ERRO",
                "linhas_vivas": 0,
                "data_inicio_viva": "N/D",
                "data_fim_viva": "N/D",
                "status_leitura": str(erro)
            })

    return pd.DataFrame(registros)


def normalizar_ativo(ativo):

    ativo = str(ativo).upper()

    if "WIN" in ativo:
        return "WIN"

    if "WDO" in ativo:
        return "WDO"

    return "DESCONHECIDO"


def main():

    print("\n" + "=" * 60)
    print("BERNARDO v1.3 - ARQUIVISTA")
    print("=" * 60)

    df_hist = carregar_memoria_historica()
    df_viva = analisar_memoria_viva()

    resultados = []

    for _, linha in df_viva.iterrows():

        ativo_base = normalizar_ativo(
            linha["ativo_vivo"]
        )

        historico_ativo = df_hist[
            df_hist["ativo"].astype(str).str.upper()
            ==
            ativo_base
        ] if (
            len(df_hist) > 0
            and
            "ativo" in df_hist.columns
        ) else pd.DataFrame()

        ultima_hist = "N/D"

        if len(historico_ativo) > 0:
            ultima_hist = str(
                historico_ativo["ultima_data"].iloc[0]
            )

        status = "SEM_HISTORICO"

        if (
            ultima_hist != "N/D"
            and
            linha["data_fim_viva"] != "N/D"
        ):

            data_hist = pd.to_datetime(
                ultima_hist,
                dayfirst=True,
                errors="coerce"
            )

            data_viva = pd.to_datetime(
                linha["data_fim_viva"],
                dayfirst=True,
                errors="coerce"
            )

            if pd.notna(data_hist) and pd.notna(data_viva):

                if data_viva > data_hist:
                    status = "MEMORIA_VIVA_MAIS_NOVA"

                elif data_viva == data_hist:
                    status = "SINCRONIZADA"

                else:
                    status = "MEMORIA_VIVA_MAIS_ANTIGA"

        acao = "VERIFICAR"

        if status == "SINCRONIZADA":
            acao = "NAO_ARQUIVAR"

        elif status == "MEMORIA_VIVA_MAIS_NOVA":
            acao = "ARQUIVAR"

        elif status == "MEMORIA_VIVA_MAIS_ANTIGA":
            acao = "JA_ARQUIVADO"

        resultados.append({
            "arquivo_memoria": linha["arquivo_memoria"],
            "ativo_vivo": linha["ativo_vivo"],
            "ativo_base": ativo_base,
            "linhas_vivas": linha["linhas_vivas"],
            "data_inicio_viva": linha["data_inicio_viva"],
            "data_fim_viva": linha["data_fim_viva"],
            "ultima_data_historica": ultima_hist,
            "status_ponte": status,
            "acao": acao,
            "status_leitura": linha["status_leitura"]
        })

        print(
            f"{linha['arquivo_memoria']} | "
            f"{ativo_base} | "
            f"{linha['data_inicio_viva']} -> "
            f"{linha['data_fim_viva']} | "
            f"historico ate {ultima_hist} | "
            f"{status} | "
            f"{acao}"
        )

    df_saida = pd.DataFrame(resultados)

    df_saida.to_csv(
        ARQUIVO_SAIDA,
        sep=";",
        index=False,
        encoding="utf-8-sig"
    )

    print("\n" + "=" * 60)
    print("RESUMO ARQUIVISTA")
    print("=" * 60)

    print(
        f"Arquivos analisados : {len(df_saida)}"
    )

    if len(df_saida) > 0:

        print(
            "Arquivar           : "
            f"{len(df_saida[df_saida['acao'] == 'ARQUIVAR'])}"
        )

        print(
            "Nao arquivar       : "
            f"{len(df_saida[df_saida['acao'] == 'NAO_ARQUIVAR'])}"
        )

        print(
            "Ja arquivado       : "
            f"{len(df_saida[df_saida['acao'] == 'JA_ARQUIVADO'])}"
        )

    print(
        f"Relatorio salvo em : {ARQUIVO_SAIDA}"
    )

    print("=" * 60)


if __name__ == "__main__":
    main()