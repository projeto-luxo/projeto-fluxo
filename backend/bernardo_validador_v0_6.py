import os
import pandas as pd
from datetime import datetime


# ============================================================
# BERNARDO - VALIDADOR DE CONTEÚDO DO TRIN
# v0.6 - Verifica se WIN/WDO está na pasta correta
# NÃO MOVE ARQUIVOS AINDA
# Apenas gera relatorio_movimentacoes.csv
# ============================================================

BASE_PATH = r"C:\Users\User\projeto_fluxo\TRIN_HISTORICO"

PASTA_INDICES = os.path.join(BASE_PATH, "00_INDICES")
ARQUIVO_MOVIMENTACOES = os.path.join(PASTA_INDICES, "relatorio_movimentacoes.csv")


def ler_csv_profit(caminho_csv):
    return pd.read_csv(
        caminho_csv,
        sep=";",
        header=None,
        engine="python"
    )


def detectar_ativo_por_conteudo(df):
    if len(df) == 0:
        return "DESCONHECIDO"

    valor = str(df.iloc[0, 0]).upper()

    if "WIN" in valor:
        return "WIN"

    if "WDO" in valor:
        return "WDO"

    return "DESCONHECIDO"


def main():
    print("\n" + "=" * 60)
    print("BERNARDO v0.6 - VALIDADOR DE CONTEUDO")
    print("CONTEUDO > PASTA > NOME")
    print("MODO AUDITORIA - NAO MOVE ARQUIVOS")
    print("=" * 60)

    os.makedirs(PASTA_INDICES, exist_ok=True)

    registros = []

    for raiz, dirs, arquivos in os.walk(BASE_PATH):

        if "00_INDICES" in raiz:
            continue

        if "00_MEMORIA_PROCESSADA" in raiz:
            continue

        for arquivo in sorted(arquivos):
            if not arquivo.lower().endswith(".csv"):
                continue

            caminho_csv = os.path.join(raiz, arquivo)
            pasta_atual = os.path.basename(raiz).lower()
            fractal = os.path.basename(os.path.dirname(raiz))

            if pasta_atual not in ["win", "wdo"]:
                continue

            try:
                df = ler_csv_profit(caminho_csv)
                ativo_detectado = detectar_ativo_por_conteudo(df)

                pasta_correta = ativo_detectado.lower()

                if ativo_detectado == "DESCONHECIDO":
                    acao = "VERIFICAR"
                    resultado = "ATIVO_DESCONHECIDO"
                    destino = "N/D"

                elif pasta_atual != pasta_correta:
                    acao = "MOVER"
                    resultado = "MOVIMENTACAO_NECESSARIA"
                    destino = os.path.join(
                        os.path.dirname(raiz),
                        pasta_correta,
                        arquivo
                    )

                else:
                    acao = "OK"
                    resultado = "PASTA_CORRETA"
                    destino = caminho_csv

                registros.append({
                    "data_hora": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                    "fractal": fractal,
                    "arquivo": arquivo,
                    "ativo_detectado": ativo_detectado,
                    "pasta_atual": pasta_atual,
                    "pasta_correta": pasta_correta if ativo_detectado != "DESCONHECIDO" else "N/D",
                    "acao": acao,
                    "resultado": resultado,
                    "caminho_atual": caminho_csv,
                    "destino_sugerido": destino
                })

                if acao != "OK":
                    print(
                        f"{acao} | {resultado} | "
                        f"{arquivo} | pasta atual: {pasta_atual} | "
                        f"ativo: {ativo_detectado}"
                    )

            except Exception as erro:
                registros.append({
                    "data_hora": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                    "fractal": fractal,
                    "arquivo": arquivo,
                    "ativo_detectado": "ERRO",
                    "pasta_atual": pasta_atual,
                    "pasta_correta": "N/D",
                    "acao": "ERRO",
                    "resultado": str(erro),
                    "caminho_atual": caminho_csv,
                    "destino_sugerido": "N/D"
                })

                print(f"ERRO | {arquivo} | {erro}")

    df_registros = pd.DataFrame(registros)

    df_registros.to_csv(
        ARQUIVO_MOVIMENTACOES,
        sep=";",
        index=False,
        encoding="utf-8-sig"
    )

    total = len(df_registros)

    if total > 0:
        corretos = len(df_registros[df_registros["acao"] == "OK"])
        mover = len(df_registros[df_registros["acao"] == "MOVER"])
        verificar = len(df_registros[df_registros["acao"] == "VERIFICAR"])
        erros = len(df_registros[df_registros["acao"] == "ERRO"])
    else:
        corretos = mover = verificar = erros = 0

    print("\n" + "=" * 60)
    print("RESUMO BERNARDO v0.6")
    print("=" * 60)
    print(f"Arquivos analisados        : {total}")
    print(f"Pastas corretas            : {corretos}")
    print(f"Movimentacoes necessarias  : {mover}")
    print(f"Verificar manualmente      : {verificar}")
    print(f"Erros                      : {erros}")
    print(f"Relatorio salvo em         : {ARQUIVO_MOVIMENTACOES}")
    print("=" * 60)


if __name__ == "__main__":
    main()