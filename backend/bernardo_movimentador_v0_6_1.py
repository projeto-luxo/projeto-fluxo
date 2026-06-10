import os
import shutil
import pandas as pd
from datetime import datetime


# ============================================================
# BERNARDO - MOVIMENTADOR DA BIBLIOTECA HISTÓRICA
# v0.6.1 - Move arquivos para pasta correta baseado no conteúdo
# NÃO APAGA
# NÃO SOBRESCREVE
# ============================================================

BASE_PATH = r"C:\Users\User\projeto_fluxo\TRIN_HISTORICO"

PASTA_INDICES = os.path.join(BASE_PATH, "00_INDICES")
ARQUIVO_MOVIMENTACOES = os.path.join(PASTA_INDICES, "relatorio_movimentacoes.csv")
ARQUIVO_CORRECOES = os.path.join(PASTA_INDICES, "relatorio_correcoes.csv")


def main():
    print("\n" + "=" * 60)
    print("BERNARDO v0.6.1 - MOVIMENTADOR")
    print("MOVENDO ARQUIVOS COM BASE NO CONTEUDO")
    print("=" * 60)

    if not os.path.exists(ARQUIVO_MOVIMENTACOES):
        print(f"ERRO: relatorio_movimentacoes.csv nao encontrado:")
        print(ARQUIVO_MOVIMENTACOES)
        return

    df = pd.read_csv(
        ARQUIVO_MOVIMENTACOES,
        sep=";",
        encoding="utf-8-sig"
    )

    correcoes = []

    df_mover = df[df["acao"] == "MOVER"]

    for _, linha in df_mover.iterrows():
        arquivo = str(linha["arquivo"])
        origem = str(linha["caminho_atual"])
        destino = str(linha["destino_sugerido"])

        if not os.path.exists(origem):
            acao = "NAO_MOVER"
            resultado = "ORIGEM_NAO_EXISTE"
            motivo = "Arquivo de origem nao encontrado"

        elif os.path.exists(destino):
            acao = "NAO_MOVER"
            resultado = "CONFLITO"
            motivo = "Arquivo destino ja existe"

        else:
            try:
                os.makedirs(os.path.dirname(destino), exist_ok=True)
                shutil.move(origem, destino)

                acao = "MOVER"
                resultado = "EXECUTADO"
                motivo = "Movido com base no conteudo do CSV"

            except Exception as erro:
                acao = "FALHA"
                resultado = "ERRO"
                motivo = str(erro)

        correcoes.append({
            "data_hora": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            "arquivo": arquivo,
            "ativo_detectado": linha["ativo_detectado"],
            "fractal": linha["fractal"],
            "origem": origem,
            "destino": destino,
            "acao": acao,
            "resultado": resultado,
            "motivo": motivo
        })

        print(f"{acao} | {resultado} | {arquivo}")

    df_correcoes = pd.DataFrame(correcoes)

    df_correcoes.to_csv(
        ARQUIVO_CORRECOES,
        sep=";",
        index=False,
        encoding="utf-8-sig"
    )

    total = len(df_correcoes)

    if total > 0:
        executados = len(df_correcoes[df_correcoes["resultado"] == "EXECUTADO"])
        conflitos = len(df_correcoes[df_correcoes["resultado"] == "CONFLITO"])
        erros = len(df_correcoes[df_correcoes["resultado"] == "ERRO"])
    else:
        executados = conflitos = erros = 0

    print("\n" + "=" * 60)
    print("RESUMO BERNARDO v0.6.1")
    print("=" * 60)
    print(f"Movimentacoes encontradas : {total}")
    print(f"Executadas                : {executados}")
    print(f"Conflitos                 : {conflitos}")
    print(f"Erros                     : {erros}")
    print(f"Relatorio salvo em        : {ARQUIVO_CORRECOES}")
    print("=" * 60)


if __name__ == "__main__":
    main()