import os
import pandas as pd
from datetime import datetime


# ============================================================
# BERNARDO BIBLIOTECÁRIO v1.0
# Índices + integridade + status da Biblioteca Histórica TRIN
# ============================================================

BASE = r"C:\Users\User\projeto_fluxo\TRIN_HISTORICO"
PASTA_INDICES = os.path.join(BASE, "00_INDICES")

os.makedirs(PASTA_INDICES, exist_ok=True)

IGNORAR_PASTAS = {
    "00_INDICES",
    "00_MEMORIA_PROCESSADA",
}

ARQUIVO_INDICE_GERAL = os.path.join(PASTA_INDICES, "indice_geral.csv")
ARQUIVO_INDICE_WIN = os.path.join(PASTA_INDICES, "indice_win.csv")
ARQUIVO_INDICE_WDO = os.path.join(PASTA_INDICES, "indice_wdo.csv")
ARQUIVO_INTEGRIDADE = os.path.join(PASTA_INDICES, "relatorio_integridade.csv")
ARQUIVO_STATUS = os.path.join(PASTA_INDICES, "biblioteca_status.txt")
ARQUIVO_LOG = os.path.join(PASTA_INDICES, "log_bernardo.csv")


def identificar_ativo(valor, arquivo):
    texto = f"{valor} {arquivo}".upper()

    if "WIN" in texto:
        return "WIN"

    if "WDO" in texto:
        return "WDO"

    return "DESCONHECIDO"


def identificar_fractal(pasta):
    nome = pasta.upper()

    if "1_MIN" in nome:
        return "1_MIN"
    if "2_MIN" in nome:
        return "2_MIN"
    if "3_MIN" in nome:
        return "3_MIN"
    if "5_MIN" in nome:
        return "5_MIN"
    if "10_MIN" in nome:
        return "10_MIN"
    if "15_MIN" in nome:
        return "15_MIN"
    if "30_MIN" in nome:
        return "30_MIN"
    if "60_MIN" in nome:
        return "60_MIN"
    if "DIARIO" in nome:
        return "DIARIO"
    if "SEMANAL" in nome:
        return "SEMANAL"
    if "MENSAL" in nome:
        return "MENSAL"

    return "DESCONHECIDO"


def ler_datas(df):
    if df.shape[1] < 2:
        return "N/D", "N/D", "DATA_INVALIDA"

    datas = pd.to_datetime(
        df.iloc[:, 1],
        dayfirst=True,
        errors="coerce"
    ).dropna()

    if len(datas) == 0:
        return "N/D", "N/D", "DATA_INVALIDA"

    return (
        datas.min().strftime("%d/%m/%Y"),
        datas.max().strftime("%d/%m/%Y"),
        "OK"
    )


def pasta_coerente(fractal_detectado, caminho):
    caminho_upper = caminho.upper()

    mapa = {
        "1_MIN": "01_1_MIN",
        "2_MIN": "02_2_MIN",
        "3_MIN": "03_3_MIN",
        "5_MIN": "04_5_MIN",
        "10_MIN": "05_10_MIN",
        "15_MIN": "06_15_MIN",
        "30_MIN": "07_30_MIN",
        "60_MIN": "08_60_MIN",
        "DIARIO": "09_DIARIO",
        "SEMANAL": "10_SEMANAL",
        "MENSAL": "11_MENSAL",
    }

    esperado = mapa.get(fractal_detectado)

    if esperado is None:
        return False

    return esperado in caminho_upper


def registrar_log(acao, resultado):
    linha = pd.DataFrame([{
        "data_hora": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "acao": acao,
        "resultado": resultado,
    }])

    if os.path.exists(ARQUIVO_LOG):
        linha.to_csv(
            ARQUIVO_LOG,
            sep=";",
            index=False,
            header=False,
            mode="a",
            encoding="utf-8-sig"
        )
    else:
        linha.to_csv(
            ARQUIVO_LOG,
            sep=";",
            index=False,
            encoding="utf-8-sig"
        )


def processar_arquivo(pasta_fractal, raiz, arquivo):
    caminho = os.path.join(raiz, arquivo)

    registro = {
        "fractal_pasta": pasta_fractal,
        "fractal_detectado": identificar_fractal(pasta_fractal),
        "ativo": "DESCONHECIDO",
        "arquivo": arquivo,
        "caminho": caminho,
        "linhas": 0,
        "data_inicio": "N/D",
        "data_fim": "N/D",
        "colunas": 0,
        "status": "OK",
        "observacao": "",
    }

    try:
        df = pd.read_csv(
            caminho,
            sep=";",
            header=None,
            engine="python"
        )

        registro["linhas"] = len(df)
        registro["colunas"] = df.shape[1]

        if len(df) == 0:
            registro["status"] = "ALERTA"
            registro["observacao"] = "ARQUIVO_VAZIO"
            return registro

        if df.shape[1] < 3:
            registro["status"] = "ALERTA"
            registro["observacao"] = "COLUNA_INSUFICIENTE"

        ativo_original = str(df.iloc[0, 0])
        registro["ativo"] = identificar_ativo(ativo_original, arquivo)

        data_inicio, data_fim, status_data = ler_datas(df)
        registro["data_inicio"] = data_inicio
        registro["data_fim"] = data_fim

        observacoes = []

        if status_data != "OK":
            observacoes.append(status_data)

        if registro["ativo"] == "DESCONHECIDO":
            observacoes.append("ATIVO_DESCONHECIDO")

        if not pasta_coerente(registro["fractal_detectado"], caminho):
            observacoes.append("FRACTAL_PASTA_INCOERENTE")

        if observacoes:
            registro["status"] = "ALERTA"
            registro["observacao"] = " | ".join(observacoes)

        return registro

    except Exception as erro:
        registro["status"] = "ERRO"
        registro["observacao"] = str(erro)
        return registro


def gerar_status(indice):
    total_arquivos = len(indice)
    total_linhas = int(indice["linhas"].sum()) if total_arquivos > 0 else 0

    total_win = len(indice[indice["ativo"] == "WIN"])
    total_wdo = len(indice[indice["ativo"] == "WDO"])

    datas_validas = pd.to_datetime(
        indice["data_inicio"],
        dayfirst=True,
        errors="coerce"
    ).dropna()

    datas_finais = pd.to_datetime(
        indice["data_fim"],
        dayfirst=True,
        errors="coerce"
    ).dropna()

    data_inicio = "N/D"
    data_fim = "N/D"

    if len(datas_validas) > 0:
        data_inicio = datas_validas.min().strftime("%d/%m/%Y")

    if len(datas_finais) > 0:
        data_fim = datas_finais.max().strftime("%d/%m/%Y")

    alertas = len(indice[indice["status"] == "ALERTA"])
    erros = len(indice[indice["status"] == "ERRO"])

    fractais = sorted(indice["fractal_detectado"].dropna().unique())

    texto = []
    texto.append("=" * 60)
    texto.append("BIBLIOTECA HISTÓRICA TRIN")
    texto.append("=" * 60)
    texto.append(f"Arquivos .......... {total_arquivos}")
    texto.append(f"Registros ......... {total_linhas}")
    texto.append(f"WIN ............... {total_win}")
    texto.append(f"WDO ............... {total_wdo}")
    texto.append(f"Fractais .......... {', '.join(fractais)}")
    texto.append(f"Data inicial ...... {data_inicio}")
    texto.append(f"Data final ........ {data_fim}")
    texto.append(f"Alertas ........... {alertas}")
    texto.append(f"Erros ............. {erros}")
    texto.append(f"Última atualização  {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    texto.append("=" * 60)

    with open(ARQUIVO_STATUS, "w", encoding="utf-8") as f:
        f.write("\n".join(texto))

    return "\n".join(texto)


def main():
    print("\n" + "=" * 60)
    print("📚 BERNARDO BIBLIOTECÁRIO v1.0")
    print("=" * 60)

    registros = []

    for pasta in sorted(os.listdir(BASE)):
        if pasta in IGNORAR_PASTAS:
            continue

        caminho_pasta = os.path.join(BASE, pasta)

        if not os.path.isdir(caminho_pasta):
            continue

        for raiz, _, arquivos in os.walk(caminho_pasta):
            for arquivo in arquivos:
                if not arquivo.lower().endswith(".csv"):
                    continue

                registro = processar_arquivo(pasta, raiz, arquivo)
                registros.append(registro)

                print(
                    f"{registro['status']} | "
                    f"{registro['fractal_detectado']} | "
                    f"{registro['ativo']} | "
                    f"{registro['arquivo']} | "
                    f"{registro['linhas']} linhas"
                )

    indice = pd.DataFrame(registros)

    indice.to_csv(
        ARQUIVO_INDICE_GERAL,
        sep=";",
        index=False,
        encoding="utf-8-sig"
    )

    indice[indice["ativo"] == "WIN"].to_csv(
        ARQUIVO_INDICE_WIN,
        sep=";",
        index=False,
        encoding="utf-8-sig"
    )

    indice[indice["ativo"] == "WDO"].to_csv(
        ARQUIVO_INDICE_WDO,
        sep=";",
        index=False,
        encoding="utf-8-sig"
    )

    integridade = indice[[
        "arquivo",
        "fractal_detectado",
        "ativo",
        "linhas",
        "status",
        "observacao"
    ]]

    integridade.to_csv(
        ARQUIVO_INTEGRIDADE,
        sep=";",
        index=False,
        encoding="utf-8-sig"
    )

    status_texto = gerar_status(indice)
    registrar_log("ATUALIZAR_BIBLIOTECA", "OK")

    print("\n" + status_texto)
    print("\nArquivos gerados:")
    print(ARQUIVO_INDICE_GERAL)
    print(ARQUIVO_INDICE_WIN)
    print(ARQUIVO_INDICE_WDO)
    print(ARQUIVO_INTEGRIDADE)
    print(ARQUIVO_STATUS)
    print(ARQUIVO_LOG)


if __name__ == "__main__":
    main()