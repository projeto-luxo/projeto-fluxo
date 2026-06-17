import os
import pandas as pd
from pathlib import Path
from datetime import datetime


# ============================================================
# BERNARDO - VALIDADOR DE CONTEÚDO DO TRIN
# v0.6
# Ajustado para arquitetura atual
# - Histórico em projeto_fluxo\TRIN_HISTORICO
# - NÃO MOVE ARQUIVOS
# - Apenas gera relatorio_movimentacoes.csv
# ============================================================

TRIN_ROOT = Path(__file__).resolve().parents[1]

BASE_PATH = TRIN_ROOT / "TRIN_HISTORICO"
PASTA_INDICES = BASE_PATH / "00_INDICES"
ARQUIVO_MOVIMENTACOES = PASTA_INDICES / "relatorio_movimentacoes.csv"


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

    print(f"Pasta historico : {BASE_PATH}")
    print(f"Pasta indices   : {PASTA_INDICES}")

    PASTA_INDICES.mkdir(parents=True, exist_ok=True)

    registros = []

    for raiz, dirs, arquivos in os.walk(BASE_PATH):

        if "00_INDICES" in raiz:
            continue

        if "00_MEMORIA_PROCESSADA" in raiz:
            continue

        for arquivo in sorted(arquivos):

            if not arquivo.lower().endswith(".csv"):
                continue

            caminho_csv = Path(raiz) / arquivo
            pasta_atual = Path(raiz).name.lower()
            fractal = Path(raiz).parent.name

            if pasta_atual not in ["win", "wdo"]:
                continue

            try:
                df = ler_csv_profit(caminho_csv)
                ativo_detectado = detectar_ativo_por_conteudo(df)

                if ativo_detectado == "DESCONHECIDO":
                    acao = "VERIFICAR"
                    destino_sugerido = str(caminho_csv)
                    motivo = "Ativo nao identificado pelo conteudo"

                else:
                    pasta_correta = ativo_detectado.lower()

                    if pasta_atual == pasta_correta:
                        acao = "OK"
                        destino_sugerido = str(caminho_csv)
                        motivo = "Arquivo ja esta na pasta correta"
                    else:
                        destino_sugerido = str(
                            Path(raiz).parent / pasta_correta / arquivo
                        )
                        acao = "MOVER"
                        motivo = (
                            f"Conteudo indica {ativo_detectado}, "
                            f"mas arquivo esta em {pasta_atual}"
                        )

                registros.append({
                    "data_hora": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                    "arquivo": arquivo,
                    "fractal": fractal,
                    "pasta_atual": pasta_atual,
                    "ativo_detectado": ativo_detectado,
                    "caminho_atual": str(caminho_csv),
                    "destino_sugerido": destino_sugerido,
                    "acao": acao,
                    "motivo": motivo
                })

                print(
                    f"{acao} | {ativo_detectado} | "
                    f"{fractal} | {arquivo}"
                )

            except Exception as erro:
                registros.append({
                    "data_hora": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                    "arquivo": arquivo,
                    "fractal": fractal,
                    "pasta_atual": pasta_atual,
                    "ativo_detectado": "ERRO",
                    "caminho_atual": str(caminho_csv),
                    "destino_sugerido": str(caminho_csv),
                    "acao": "ERRO",
                    "motivo": str(erro)
                })

                print(f"ERRO | {arquivo} | {erro}")

    df_saida = pd.DataFrame(registros)

    df_saida.to_csv(
        ARQUIVO_MOVIMENTACOES,
        sep=";",
        index=False,
        encoding="utf-8-sig"
    )

    print("\n" + "=" * 60)
    print("RESUMO VALIDADOR")
    print("=" * 60)
    print(f"Arquivos analisados : {len(df_saida)}")

    if len(df_saida) > 0:
        print(f"OK                  : {len(df_saida[df_saida['acao'] == 'OK'])}")
        print(f"MOVER               : {len(df_saida[df_saida['acao'] == 'MOVER'])}")
        print(f"VERIFICAR           : {len(df_saida[df_saida['acao'] == 'VERIFICAR'])}")
        print(f"ERRO                : {len(df_saida[df_saida['acao'] == 'ERRO'])}")

    print(f"Relatorio salvo em  : {ARQUIVO_MOVIMENTACOES}")
    print("=" * 60)


if __name__ == "__main__":
    main()