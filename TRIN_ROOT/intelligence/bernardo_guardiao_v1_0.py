import pandas as pd
from pathlib import Path
from datetime import datetime


# ============================================================
# BERNARDO v1.0
# GUARDIAO DA BIBLIOTECA HISTORICA
# Ajustado para TRIN_ROOT
# Missao: auditar se os indices principais existem e estao legiveis
# ============================================================

TRIN_ROOT = Path(__file__).resolve().parents[1]

BASE_PATH = TRIN_ROOT / "TRIN_HISTORICO"
PASTA_INDICES = BASE_PATH / "00_INDICES"

ARQUIVO_RELATORIO = PASTA_INDICES / "relatorio_guardiao.csv"

ARQUIVOS_OBRIGATORIOS = [
    "indice_geral.csv",
    "indice_win.csv",
    "indice_wdo.csv",
    "relatorio_integridade.csv",
    "biblioteca_status.txt",
]


def verificar_arquivo(nome):
    caminho = PASTA_INDICES / nome

    if not caminho.exists():
        return {
            "arquivo": nome,
            "existe": "NAO",
            "linhas": 0,
            "colunas": 0,
            "status": "AUSENTE",
            "observacao": "Arquivo obrigatorio nao encontrado",
        }

    if caminho.suffix.lower() == ".txt":
        try:
            conteudo = caminho.read_text(encoding="utf-8", errors="ignore")
            return {
                "arquivo": nome,
                "existe": "SIM",
                "linhas": len(conteudo.splitlines()),
                "colunas": "N/A",
                "status": "OK",
                "observacao": "Arquivo texto legivel",
            }
        except Exception as erro:
            return {
                "arquivo": nome,
                "existe": "SIM",
                "linhas": 0,
                "colunas": 0,
                "status": "ERRO",
                "observacao": str(erro),
            }

    try:
        df = pd.read_csv(
            caminho,
            sep=";",
            encoding="utf-8-sig",
            engine="python"
        )

        return {
            "arquivo": nome,
            "existe": "SIM",
            "linhas": len(df),
            "colunas": len(df.columns),
            "status": "OK",
            "observacao": "CSV legivel",
        }

    except Exception as erro:
        return {
            "arquivo": nome,
            "existe": "SIM",
            "linhas": 0,
            "colunas": 0,
            "status": "ERRO",
            "observacao": str(erro),
        }


def main():
    print("\n" + "=" * 60)
    print("BERNARDO v1.0 - GUARDIAO DA BIBLIOTECA")
    print("=" * 60)

    print(f"Pasta historico: {BASE_PATH}")
    print(f"Pasta indices  : {PASTA_INDICES}")

    PASTA_INDICES.mkdir(parents=True, exist_ok=True)

    registros = []

    for nome in ARQUIVOS_OBRIGATORIOS:
        resultado = verificar_arquivo(nome)
        registros.append(resultado)

        print(
            f"{resultado['status']} | "
            f"{resultado['arquivo']} | "
            f"{resultado['linhas']} linhas | "
            f"{resultado['observacao']}"
        )

    df = pd.DataFrame(registros)

    df.insert(
        0,
        "data_hora",
        datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    )

    df.to_csv(
        ARQUIVO_RELATORIO,
        sep=";",
        index=False,
        encoding="utf-8-sig"
    )

    total_erros = len(df[df["status"] == "ERRO"])
    total_ausentes = len(df[df["status"] == "AUSENTE"])

    print("\n" + "=" * 60)
    print("RESUMO GUARDIAO")
    print("=" * 60)
    print(f"Arquivos verificados : {len(df)}")
    print(f"Ausentes             : {total_ausentes}")
    print(f"Erros                : {total_erros}")
    print(f"Relatorio salvo em   : {ARQUIVO_RELATORIO}")

    if total_erros == 0 and total_ausentes == 0:
        print("STATUS FINAL         : BIBLIOTECA PROTEGIDA")
    else:
        print("STATUS FINAL         : VERIFICAR PENDENCIAS")

    print("=" * 60)


if __name__ == "__main__":
    main()