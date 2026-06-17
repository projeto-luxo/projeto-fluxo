import os
import pandas as pd
from pathlib import Path


# ============================================================
# BERNARDO v1.2
# PONTE DE MEMORIA
# Compara memoria viva com memoria historica
# Ajustado para arquitetura TRIN_ROOT
# ============================================================

TRIN_ROOT = Path(__file__).resolve().parents[1]
PROJETO_FLUXO = TRIN_ROOT.parent

PASTA_MEMORIA = TRIN_ROOT / "memoria"
PASTA_HISTORICO = PROJETO_FLUXO / "TRIN_HISTORICO"
PASTA_INDICES = PASTA_HISTORICO / "00_INDICES"

ARQUIVO_MEMORIA_HISTORICA = PASTA_INDICES / "relatorio_memoria.csv"
ARQUIVO_SAIDA = PASTA_INDICES / "relatorio_ponte_memoria.csv"


def carregar_memoria_historica():
    if not ARQUIVO_MEMORIA_HISTORICA.exists():
        return pd.DataFrame()

    return pd.read_csv(
        ARQUIVO_MEMORIA_HISTORICA,
        sep=";",
        encoding="utf-8-sig"
    )


def analisar_memoria_viva():
    registros = []

    if not PASTA_MEMORIA.exists():
        print(f"ERRO: pasta de memoria nao encontrada: {PASTA_MEMORIA}")
        return pd.DataFrame()

    for arquivo in sorted(os.listdir(PASTA_MEMORIA)):

        if not arquivo.lower().endswith(".csv"):
            continue

        if not arquivo.startswith("TRIN_MEMORIA_"):
            continue

        caminho = PASTA_MEMORIA / arquivo

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
    texto = str(ativo).upper()

    if "WIN" in texto:
        return "WIN"

    if "WDO" in texto:
        return "WDO"

    return "DESCONHECIDO"


def main():

    print("\n" + "=" * 60)
    print("BERNARDO v1.2 - PONTE DE MEMORIA")
    print("=" * 60)

    print(f"Pasta memoria  : {PASTA_MEMORIA}")
    print(f"Pasta historico: {PASTA_HISTORICO}")
    print(f"Pasta indices  : {PASTA_INDICES}")

    PASTA_INDICES.mkdir(parents=True, exist_ok=True)

    df_hist = carregar_memoria_historica()
    df_viva = analisar_memoria_viva()

    registros = []

    for _, linha in df_viva.iterrows():

        ativo_base = normalizar_ativo(linha.get("ativo_vivo", "N/D"))

        if (
            len(df_hist) > 0
            and "ativo" in df_hist.columns
        ):
            historico_ativo = df_hist[
                df_hist["ativo"].astype(str).str.upper() == ativo_base
            ]
        else:
            historico_ativo = pd.DataFrame()

        ultima_hist = "N/D"

        if len(historico_ativo) > 0 and "ultima_data" in historico_ativo.columns:
            ultima_hist = str(historico_ativo["ultima_data"].iloc[0])

        status = "SEM_HISTORICO"

        if ultima_hist != "N/D" and linha.get("data_fim_viva", "N/D") != "N/D":
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

        registros.append({
            "arquivo_memoria": linha.get("arquivo_memoria", "N/D"),
            "ativo_vivo": linha.get("ativo_vivo", "N/D"),
            "ativo_base": ativo_base,
            "linhas_vivas": linha.get("linhas_vivas", 0),
            "data_inicio_viva": linha.get("data_inicio_viva", "N/D"),
            "data_fim_viva": linha.get("data_fim_viva", "N/D"),
            "ultima_data_historica": ultima_hist,
            "status_ponte": status,
            "status_leitura": linha.get("status_leitura", "N/D")
        })

        print(
            f"{linha.get('arquivo_memoria', 'N/D')} | "
            f"{ativo_base} | "
            f"{linha.get('data_inicio_viva', 'N/D')} -> "
            f"{linha.get('data_fim_viva', 'N/D')} | "
            f"historico ate {ultima_hist} | "
            f"{status}"
        )

    df_saida = pd.DataFrame(registros)

    df_saida.to_csv(
        ARQUIVO_SAIDA,
        sep=";",
        index=False,
        encoding="utf-8-sig"
    )

    print("\n" + "=" * 60)
    print("RESUMO PONTE MEMORIA")
    print("=" * 60)
    print(f"Arquivos analisados : {len(df_saida)}")
    print(f"Relatorio salvo em  : {ARQUIVO_SAIDA}")
    print("=" * 60)


if __name__ == "__main__":
    main()