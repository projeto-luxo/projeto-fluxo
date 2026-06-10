import os
import shutil
import pandas as pd


# ============================================================
# BERNARDO v1.1.2
# ZELADOR DA MEMORIA VIVA
# ============================================================

PASTA_MEMORIA = r"C:\Users\User\projeto_fluxo\memoria"

PASTA_RELATORIOS = os.path.join(
    PASTA_MEMORIA,
    "00_RELATORIOS"
)

ARQUIVO_RELATORIO = os.path.join(
    PASTA_RELATORIOS,
    "relatorio_limpeza_memoria.csv"
)


def main():

    print("\n" + "=" * 60)
    print("BERNARDO v1.1.2 - ZELADOR DA MEMORIA VIVA")
    print("=" * 60)

    os.makedirs(
        PASTA_RELATORIOS,
        exist_ok=True
    )

    registros = []

    for arquivo in sorted(os.listdir(PASTA_MEMORIA)):

        caminho_origem = os.path.join(
            PASTA_MEMORIA,
            arquivo
        )

        if os.path.isdir(caminho_origem):
            continue

        if not arquivo.lower().startswith("relatorio_"):
            continue

        caminho_destino = os.path.join(
            PASTA_RELATORIOS,
            arquivo
        )

        shutil.move(
            caminho_origem,
            caminho_destino
        )

        registros.append({
            "arquivo": arquivo,
            "acao": "MOVIDO",
            "destino": caminho_destino
        })

        print(
            f"MOVER | EXECUTADO | {arquivo}"
        )

    pd.DataFrame(registros).to_csv(
        ARQUIVO_RELATORIO,
        sep=";",
        index=False,
        encoding="utf-8-sig"
    )

    print("\n" + "=" * 60)
    print("RESUMO")
    print("=" * 60)
    print(f"Arquivos movidos : {len(registros)}")
    print(f"Relatorio salvo  : {ARQUIVO_RELATORIO}")
    print("=" * 60)


if __name__ == "__main__":
    main()