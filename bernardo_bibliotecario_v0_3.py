import os
import pandas as pd

BASE = r"C:\Users\User\projeto_fluxo\TRIN_HISTORICO"

saida = []

print("=" * 60)
print("📚 BERNARDO BIBLIOTECÁRIO v0.3")
print("=" * 60)

for pasta in sorted(os.listdir(BASE)):

    caminho_pasta = os.path.join(BASE, pasta)

    if not os.path.isdir(caminho_pasta):
        continue

    for raiz, dirs, arquivos in os.walk(caminho_pasta):

        for arquivo in arquivos:

            if not arquivo.lower().endswith(".csv"):
                continue

            caminho = os.path.join(raiz, arquivo)

            try:

                df = pd.read_csv(
                    caminho,
                    sep=";",
                    header=None,
                    engine="python"
                )

                linhas = len(df)

                data_inicio = ""
                data_fim = ""

                if linhas > 0 and df.shape[1] >= 2:

                    data_inicio = str(df.iloc[0, 1])

                    data_fim = str(df.iloc[-1, 1])

                ativo = ""

                if df.shape[1] >= 1:
                    ativo = str(df.iloc[0, 0])

                saida.append({

                    "fractal": pasta,

                    "ativo": ativo,

                    "arquivo": arquivo,

                    "linhas": linhas,

                    "data_inicio": data_inicio,

                    "data_fim": data_fim,

                    "status": "OK"

                })

                print(f"✔ {arquivo}")

            except Exception as erro:

                saida.append({

                    "fractal": pasta,

                    "ativo": "",

                    "arquivo": arquivo,

                    "linhas": 0,

                    "data_inicio": "",

                    "data_fim": "",

                    "status": f"ERRO: {erro}"

                })

                print(f"❌ {arquivo}")

indice = pd.DataFrame(saida)

indice.to_csv(

    os.path.join(BASE, "00_INDICES", "indice_geral.csv"),

    sep=";",

    index=False,

    encoding="utf-8-sig"

)

print()

print("=" * 60)

print("📚 Índice geral criado com sucesso!")

print()

print(indice)

print("=" * 60)