import os
import pandas as pd
from pathlib import Path


# ============================================================
# BERNARDO v1.1
# INSPETOR DA MEMORIA VIVA
# Ajustado para TRIN_ROOT
# Missao: inspecionar arquivos TRIN_MEMORIA_*.csv
# ============================================================

TRIN_ROOT = Path(__file__).resolve().parents[1]

PASTA_MEMORIA = TRIN_ROOT / "memoria"
PASTA_RELATORIOS = PASTA_MEMORIA / "00_RELATORIOS"

ARQUIVO_RELATORIO = PASTA_RELATORIOS / "relatorio_inspetor_memoria.csv"

COLUNAS_OBRIGATORIAS = [
    "ativo",
    "data",
    "hora",
    "ultimo",
    "volume",
    "delta",
    "saldo",
    "vwap",
]


def analisar_csv(caminho):
    try:
        df = pd.read_csv(
            caminho,
            sep=";",
            engine="python"
        )

        colunas = list(df.columns)
        faltando = [
            coluna for coluna in COLUNAS_OBRIGATORIAS
            if coluna not in colunas
        ]

        ativo = "N/D"
        data_inicio = "N/D"
        data_fim = "N/D"

        if len(df) > 0 and "ativo" in df.columns:
            ativo = str(df["ativo"].iloc[0])

        if len(df) > 0 and "data" in df.columns:
            data_inicio = str(df["data"].iloc[0])
            data_fim = str(df["data"].iloc[-1])

        status = "OK" if not faltando else "ALERTA"

        return {
            "arquivo": caminho.name,
            "ativo": ativo,
            "linhas": len(df),
            "colunas": len(colunas),
            "data_inicio": data_inicio,
            "data_fim": data_fim,
            "faltando": ", ".join(faltando) if faltando else "NENHUMA",
            "status": status,
        }

    except Exception as erro:
        return {
            "arquivo": caminho.name,
            "ativo": "ERRO",
            "linhas": 0,
            "colunas": 0,
            "data_inicio": "N/D",
            "data_fim": "N/D",
            "faltando": "N/D",
            "status": str(erro),
        }


def main():
    print("\n" + "=" * 60)
    print("BERNARDO v1.1 - INSPETOR DA MEMORIA VIVA")
    print("=" * 60)

    print(f"Pasta memoria    : {PASTA_MEMORIA}")
    print(f"Pasta relatorios : {PASTA_RELATORIOS}")

    if not PASTA_MEMORIA.exists():
        print("ERRO: pasta de memoria nao encontrada.")
        return

    PASTA_RELATORIOS.mkdir(parents=True, exist_ok=True)

    registros = []

    for arquivo in sorted(os.listdir(PASTA_MEMORIA)):
        if not arquivo.lower().endswith(".csv"):
            continue

        if not arquivo.startswith("TRIN_MEMORIA_"):
            continue

        caminho = PASTA_MEMORIA / arquivo
        resultado = analisar_csv(caminho)
        registros.append(resultado)

        print(
            f"{resultado['status']} | "
            f"{resultado['arquivo']} | "
            f"{resultado['linhas']} linhas | "
            f"faltando: {resultado['faltando']}"
        )

    df = pd.DataFrame(registros)

    df.to_csv(
        ARQUIVO_RELATORIO,
        sep=";",
        index=False,
        encoding="utf-8-sig"
    )

    print("\n" + "=" * 60)
    print("RESUMO INSPETOR")
    print("=" * 60)
    print(f"Arquivos analisados : {len(df)}")

    if len(df) > 0:
        print(f"OK                  : {len(df[df['status'] == 'OK'])}")
        print(f"Alertas             : {len(df[df['status'] != 'OK'])}")

    print(f"Relatorio salvo em  : {ARQUIVO_RELATORIO}")
    print("=" * 60)


if __name__ == "__main__":
    main()