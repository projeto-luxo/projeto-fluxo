import os
import shutil
import pandas as pd
from pathlib import Path


# ============================================================
# BERNARDO v1.1.2
# ZELADOR DA MEMORIA VIVA
# Ajustado:
# - Memória viva em TRIN_ROOT\memoria
# - Relatórios em TRIN_ROOT\memoria\00_RELATORIOS
# ============================================================

TRIN_ROOT = Path(__file__).resolve().parents[1]

PASTA_MEMORIA = TRIN_ROOT / "memoria"

PASTA_RELATORIOS = PASTA_MEMORIA / "00_RELATORIOS"

ARQUIVO_RELATORIO = PASTA_RELATORIOS / "relatorio_limpeza_memoria.csv"


def main():

    print("\n" + "=" * 60)
    print("BERNARDO v1.1.2 - ZELADOR DA MEMORIA VIVA")
    print("=" * 60)

    print(f"Pasta memoria    : {PASTA_MEMORIA}")
    print(f"Pasta relatorios : {PASTA_RELATORIOS}")

    if not PASTA_MEMORIA.exists():
        print("ERRO: pasta de memoria nao encontrada.")
        return

    os.makedirs(
        PASTA_RELATORIOS,
        exist_ok=True
    )

    registros = []

    for arquivo in sorted(os.listdir(PASTA_MEMORIA)):

        caminho_origem = PASTA_MEMORIA / arquivo

        if caminho_origem.is_dir():
            continue

        if not arquivo.lower().startswith("relatorio_"):
            continue

        caminho_destino = PASTA_RELATORIOS / arquivo

        if caminho_destino.exists():
            registros.append({
                "arquivo": arquivo,
                "acao": "NAO_MOVIDO",
                "destino": str(caminho_destino),
                "motivo": "DESTINO_JA_EXISTE"
            })

            print(f"NAO MOVER | CONFLITO | {arquivo}")
            continue

        shutil.move(
            str(caminho_origem),
            str(caminho_destino)
        )

        registros.append({
            "arquivo": arquivo,
            "acao": "MOVIDO",
            "destino": str(caminho_destino),
            "motivo": "OK"
        })

        print(f"MOVER | EXECUTADO | {arquivo}")

    pd.DataFrame(registros).to_csv(
        ARQUIVO_RELATORIO,
        sep=";",
        index=False,
        encoding="utf-8-sig"
    )

    print("\n" + "=" * 60)
    print("RESUMO")
    print("=" * 60)
    print(f"Arquivos movidos : {len([r for r in registros if r['acao'] == 'MOVIDO'])}")
    print(f"Conflitos        : {len([r for r in registros if r['acao'] == 'NAO_MOVIDO'])}")
    print(f"Relatorio salvo  : {ARQUIVO_RELATORIO}")
    print("=" * 60)


if __name__ == "__main__":
    main()