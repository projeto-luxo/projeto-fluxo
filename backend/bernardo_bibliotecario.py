import os
import pandas as pd


# ============================================================
# BERNARDO - BIBLIOTECÁRIO DO TRIN
# v0.4 - Índice Geral + Relatório de Integridade
# ============================================================

BASE_PATH = r"C:\Users\User\projeto_fluxo\TRIN_HISTORICO"

PASTA_INDICES = os.path.join(BASE_PATH, "00_INDICES")
ARQUIVO_INDICE = os.path.join(PASTA_INDICES, "indice_geral.csv")
ARQUIVO_INTEGRIDADE = os.path.join(PASTA_INDICES, "relatorio_integridade.csv")


def ler_csv_profit(caminho_csv):
    return pd.read_csv(
        caminho_csv,
        sep=";",
        header=None,
        engine="python"
    )


def detectar_ativo(nome_arquivo, df):
    nome = nome_arquivo.upper()

    if nome.startswith("WIN"):
        return "WIN"

    if nome.startswith("WDO"):
        return "WDO"

    if len(df) > 0:
        valor = str(df.iloc[0, 0]).upper()

        if "WIN" in valor:
            return "WIN"

        if "WDO" in valor:
            return "WDO"

    return "DESCONHECIDO"


def analisar_csv(caminho_csv, fractal, pasta_ativo, nome_arquivo):
    df = ler_csv_profit(caminho_csv)

    linhas = len(df)
    ativo = detectar_ativo(nome_arquivo, df)

    data_inicio = "N/D"
    data_fim = "N/D"
    status = "OK"
    observacao = ""

    if linhas == 0:
        status = "VAZIO"
        observacao = "Arquivo sem linhas"

    elif df.shape[1] < 2:
        status = "SUSPEITO"
        observacao = "Arquivo com poucas colunas"

    else:
        datas = pd.to_datetime(
            df.iloc[:, 1],
            dayfirst=True,
            errors="coerce"
        )

        datas_validas = datas.dropna()

        if len(datas_validas) == 0:
            status = "SUSPEITO"
            observacao = "Não foi possível converter datas"
        else:
            data_inicio = datas_validas.min().strftime("%d/%m/%Y")
            data_fim = datas_validas.max().strftime("%d/%m/%Y")

    if pasta_ativo.lower() in ["win", "wdo"]:
        if ativo != "DESCONHECIDO" and ativo.lower() != pasta_ativo.lower():
            status = "SUSPEITO"
            observacao = f"Arquivo {ativo} dentro da pasta {pasta_ativo}"

    return {
        "fractal": fractal,
        "ativo": ativo,
        "pasta": pasta_ativo,
        "arquivo": nome_arquivo,
        "linhas": linhas,
        "data_inicio": data_inicio,
        "data_fim": data_fim,
        "status": status,
        "observacao": observacao,
        "caminho": caminho_csv
    }


def auditar_integridade(registros):
    integridade = []

    for registro in registros:
        arquivo = registro["arquivo"]
        arquivo_upper = arquivo.upper()
        fractal = registro["fractal"]
        ativo = registro["ativo"]
        status = registro["status"]
        observacao = registro["observacao"]

        if "__" in arquivo:
            integridade.append({
                "tipo": "NOME",
                "arquivo": arquivo,
                "fractal": fractal,
                "ativo": ativo,
                "problema": "Duplo underline (__)"
            })

        if "+" in arquivo:
            integridade.append({
                "tipo": "NOME",
                "arquivo": arquivo,
                "fractal": fractal,
                "ativo": ativo,
                "problema": "Contém caractere +"
            })

        if "60MIN2026" in arquivo_upper:
            integridade.append({
                "tipo": "NOME",
                "arquivo": arquivo,
                "fractal": fractal,
                "ativo": ativo,
                "problema": "Falta underscore após 60min"
            })

        if status == "VAZIO":
            integridade.append({
                "tipo": "ARQUIVO",
                "arquivo": arquivo,
                "fractal": fractal,
                "ativo": ativo,
                "problema": "Arquivo vazio"
            })

        if status == "SUSPEITO":
            integridade.append({
                "tipo": "SUSPEITO",
                "arquivo": arquivo,
                "fractal": fractal,
                "ativo": ativo,
                "problema": observacao
            })

    return integridade


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
    print("📚 BERNARDO - BIBLIOTECÁRIO DO TRIN v0.4")
    print("ÍNDICE GERAL + RELATÓRIO DE INTEGRIDADE")
    print("=" * 60)

    os.makedirs(PASTA_INDICES, exist_ok=True)

    registros = []

    for fractal in sorted(os.listdir(BASE_PATH)):
        caminho_fractal = os.path.join(BASE_PATH, fractal)

        if not os.path.isdir(caminho_fractal):
            continue

        if fractal in ["00_INDICES", "99_MEMORIA_PROCESSADA", "00_MEMORIA_PROCESSADA"]:
            continue

        print(f"\n📂 {fractal}")

        for raiz, dirs, arquivos in os.walk(caminho_fractal):
            pasta_ativo = os.path.basename(raiz)

            for arquivo in sorted(arquivos):
                if not arquivo.lower().endswith(".csv"):
                    continue

                caminho_csv = os.path.join(raiz, arquivo)

                try:
                    registro = analisar_csv(
                        caminho_csv=caminho_csv,
                        fractal=fractal,
                        pasta_ativo=pasta_ativo,
                        nome_arquivo=arquivo
                    )

                    registros.append(registro)

                    print(
                        f"   {registro['ativo']} | "
                        f"{arquivo} | "
                        f"{registro['linhas']} linhas | "
                        f"{registro['data_inicio']} até {registro['data_fim']} | "
                        f"{registro['status']}"
                    )

                except Exception as erro:
                    registros.append({
                        "fractal": fractal,
                        "ativo": "ERRO",
                        "pasta": pasta_ativo,
                        "arquivo": arquivo,
                        "linhas": 0,
                        "data_inicio": "N/D",
                        "data_fim": "N/D",
                        "status": "ERRO",
                        "observacao": str(erro),
                        "caminho": caminho_csv
                    })

                    print(f"   ERRO AO LER: {arquivo} -> {erro}")

    df_indice = pd.DataFrame(registros)

    df_indice.to_csv(
        ARQUIVO_INDICE,
        sep=";",
        index=False,
        encoding="utf-8-sig"
    )

    integridade = auditar_integridade(registros)
    df_integridade = pd.DataFrame(integridade)

    df_integridade.to_csv(
        ARQUIVO_INTEGRIDADE,
        sep=";",
        index=False,
        encoding="utf-8-sig"
    )

    total = len(df_indice)
    suspeitos = len(df_indice[df_indice["status"] == "SUSPEITO"])
    vazios = len(df_indice[df_indice["status"] == "VAZIO"])
    erros = len(df_indice[df_indice["status"] == "ERRO"])

    print("\n" + "=" * 60)
    print("📊 RESUMO DO BERNARDO v0.4")
    print("=" * 60)
    print(f"Arquivos catalogados        : {total}")
    print(f"Suspeitos                   : {suspeitos}")
    print(f"Vazios                      : {vazios}")
    print(f"Erros                       : {erros}")
    print(f"Ocorrências de integridade  : {len(df_integridade)}")
    print(f"Índice geral salvo em       : {ARQUIVO_INDICE}")
    print(f"Relatório integridade salvo : {ARQUIVO_INTEGRIDADE}")
    print("=" * 60)


if __name__ == "__main__":
    mai