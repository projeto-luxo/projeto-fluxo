import os
import pandas as pd
from datetime import datetime


# ============================================================
# BERNARDO v0.5 - ZELADOR DA BIBLIOTECA HISTÓRICA
# Corrige nomes reais encontrados nas pastas
# NÃO APAGA
# NÃO SOBRESCREVE
# ============================================================

BASE_PATH = r"C:\Users\User\projeto_fluxo\TRIN_HISTORICO"

PASTA_INDICES = os.path.join(BASE_PATH, "00_INDICES")
ARQUIVO_CORRECOES = os.path.join(PASTA_INDICES, "relatorio_correcoes.csv")


def corrigir_nome(nome):
    novo_nome = nome

    while "__" in novo_nome:
        novo_nome = novo_nome.replace("__", "_")

    novo_nome = novo_nome.replace("+", "_")
    novo_nome = novo_nome.replace("60min2026", "60min_2026")
    novo_nome = novo_nome.replace("60MIN2026", "60MIN_2026")

    return novo_nome


def main():
    print("\n" + "=" * 60)
    print("BERNARDO v0.5 - ZELADOR DA BIBLIOTECA")
    print("VASCULHANDO PASTAS REAIS E CORRIGINDO NOMES")
    print("=" * 60)

    os.makedirs(PASTA_INDICES, exist_ok=True)

    correcoes = []

    for raiz, dirs, arquivos in os.walk(BASE_PATH):

        if "00_INDICES" in raiz:
            continue

        for arquivo in arquivos:
            if not arquivo.lower().endswith(".csv"):
                continue

            caminho_antigo = os.path.join(raiz, arquivo)
            arquivo_novo = corrigir_nome(arquivo)

            if arquivo_novo == arquivo:
                continue

            caminho_novo = os.path.join(raiz, arquivo_novo)

            if os.path.exists(caminho_novo):
                acao = "NAO_RENOMEAR"
                resultado = "CONFLITO"
                motivo = "Arquivo destino ja existe"
            else:
                try:
                    os.rename(caminho_antigo, caminho_novo)
                    acao = "RENOMEAR"
                    resultado = "EXECUTADO"
                    motivo = "Nome corrigido automaticamente"
                except Exception as erro:
                    acao = "FALHA"
                    resultado = "ERRO"
                    motivo = str(erro)

            correcoes.append({
                "data_hora": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                "pasta": raiz,
                "arquivo_antigo": arquivo,
                "arquivo_novo": arquivo_novo,
                "caminho_antigo": caminho_antigo,
                "caminho_novo": caminho_novo,
                "acao": acao,
                "resultado": resultado,
                "motivo": motivo
            })

            print(f"{acao} | {resultado} | {arquivo} -> {arquivo_novo}")

    df = pd.DataFrame(correcoes)

    df.to_csv(
        ARQUIVO_CORRECOES,
        sep=";",
        index=False,
        encoding="utf-8-sig"
    )

    executados = len(df[df["resultado"] == "EXECUTADO"]) if len(df) > 0 else 0
    conflitos = len(df[df["resultado"] == "CONFLITO"]) if len(df) > 0 else 0
    erros = len(df[df["resultado"] == "ERRO"]) if len(df) > 0 else 0

    print("\n" + "=" * 60)
    print("RESUMO BERNARDO v0.5")
    print("=" * 60)
    print(f"Correcoes executadas : {executados}")
    print(f"Conflitos            : {conflitos}")
    print(f"Erros                : {erros}")
    print(f"Relatorio salvo em   : {ARQUIVO_CORRECOES}")
    print("=" * 60)


if __name__ == "__main__":
    main()