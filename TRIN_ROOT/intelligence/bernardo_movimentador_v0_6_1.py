import shutil
import pandas as pd
from pathlib import Path
from datetime import datetime


# ============================================================
# BERNARDO - MOVIMENTADOR DA BIBLIOTECA HISTÓRICA
# v0.6.1
# Ajustado:
# - Histórico em projeto_fluxo\TRIN_HISTORICO
# - NÃO APAGA
# - NÃO SOBRESCREVE
# ============================================================

TRIN_ROOT = Path(__file__).resolve().parents[1]
PROJETO_FLUXO = TRIN_ROOT.parent

BASE_PATH = PROJETO_FLUXO / "TRIN_HISTORICO"

PASTA_INDICES = BASE_PATH / "00_INDICES"
ARQUIVO_MOVIMENTACOES = PASTA_INDICES / "relatorio_movimentacoes.csv"
ARQUIVO_CORRECOES = PASTA_INDICES / "relatorio_correcoes.csv"


def main():
    print("\n" + "=" * 60)
    print("BERNARDO v0.6.1 - MOVIMENTADOR")
    print("MOVENDO ARQUIVOS COM BASE NO CONTEUDO")
    print("=" * 60)

    print(f"Pasta historico : {BASE_PATH}")
    print(f"Pasta indices   : {PASTA_INDICES}")

    PASTA_INDICES.mkdir(parents=True, exist_ok=True)

    if not ARQUIVO_MOVIMENTACOES.exists():
        print("ERRO: relatorio_movimentacoes.csv nao encontrado:")
        print(ARQUIVO_MOVIMENTACOES)
        return

    df = pd.read_csv(
        ARQUIVO_MOVIMENTACOES,
        sep=";",
        encoding="utf-8-sig"
    )

    correcoes = []

    if "acao" not in df.columns:
        print("ERRO: coluna 'acao' nao encontrada no relatorio_movimentacoes.csv")
        return

    df_mover = df[df["acao"].astype(str).str.upper() == "MOVER"]

    for _, linha in df_mover.iterrows():
        arquivo = str(linha.get("arquivo", "N/D"))
        origem = Path(str(linha.get("caminho_atual", "")))
        destino = Path(str(linha.get("destino_sugerido", "")))

        if not origem.exists():
            acao = "NAO_MOVER"
            resultado = "ORIGEM_NAO_EXISTE"
            motivo = "Arquivo de origem nao encontrado"

        elif destino.exists():
            acao = "NAO_MOVER"
            resultado = "CONFLITO"
            motivo = "Arquivo destino ja existe"

        else:
            try:
                destino.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(origem), str(destino))

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
            "ativo_detectado": linha.get("ativo_detectado", "N/D"),
            "fractal": linha.get("fractal", "N/D"),
            "origem": str(origem),
            "destino": str(destino),
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