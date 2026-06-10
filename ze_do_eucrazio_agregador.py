import os
import pandas as pd


# ============================================================
# ZÉ DO EUCRÁZIO v0.3
# AGREGADOR INTELIGENTE DE FRACTAIS
#
# Reconhece:
# - Histórico Profit: 9 colunas
# - Memória Viva TRIN: 15 colunas
#
# Gera:
# - 2 minutos
# - 3 minutos
# ============================================================

BASE_PATH = r"C:\Users\User\projeto_fluxo\TRIN_HISTORICO"

PASTA_ORIGEM = os.path.join(BASE_PATH, "01_1_MIN", "win")
PASTA_2MIN = os.path.join(BASE_PATH, "02_2_MIN", "win")
PASTA_3MIN = os.path.join(BASE_PATH, "03_3_MIN", "win")

os.makedirs(PASTA_2MIN, exist_ok=True)
os.makedirs(PASTA_3MIN, exist_ok=True)


def limpar_numero(valor):
    if pd.isna(valor):
        return 0.0

    texto = str(valor).strip()
    texto = texto.replace(".", "").replace(",", ".")

    try:
        return float(texto)
    except Exception:
        return 0.0


def encontrar_primeiro_csv():
    arquivos = [
        f for f in os.listdir(PASTA_ORIGEM)
        if f.lower().endswith(".csv")
    ]

    if not arquivos:
        raise FileNotFoundError("Nenhum CSV encontrado em 01_1_MIN\\win")

    return os.path.join(PASTA_ORIGEM, sorted(arquivos)[0])


def carregar_csv(caminho_csv):
    df = pd.read_csv(
        caminho_csv,
        sep=";",
        header=None,
        engine="python"
    )

    if str(df.iloc[0, 0]).lower() in ["ativo", "timestamp_pc"]:
        df = df.iloc[1:].reset_index(drop=True)

    qtd_colunas = df.shape[1]

    if qtd_colunas >= 15:
        tipo = "MEMORIA_VIVA_TRIN"

        df = df.iloc[:, :15]
        df.columns = [
            "timestamp_pc",
            "ativo",
            "data",
            "hora",
            "ultimo",
            "abertura",
            "maximo",
            "minimo",
            "volume",
            "delta",
            "saldo",
            "agressao_compra",
            "agressao_saldo",
            "agressao_venda",
            "vwap",
        ]

    elif qtd_colunas >= 9:
        tipo = "HISTORICO_PROFIT"

        df = df.iloc[:, :9]
        df.columns = [
            "ativo",
            "data",
            "hora",
            "abertura",
            "maximo",
            "minimo",
            "ultimo",
            "volume",
            "volume_quantidade",
        ]

        df["delta"] = 0.0
        df["saldo"] = 0.0
        df["agressao_compra"] = 0.0
        df["agressao_saldo"] = 0.0
        df["agressao_venda"] = 0.0
        df["vwap"] = df["ultimo"]

    elif qtd_colunas >= 8:
        tipo = "HISTORICO_PROFIT_REDUZIDO"

        df = df.iloc[:, :8]
        df.columns = [
            "ativo",
            "data",
            "hora",
            "abertura",
            "maximo",
            "minimo",
            "ultimo",
            "volume",
        ]

        df["volume_quantidade"] = 0.0
        df["delta"] = 0.0
        df["saldo"] = 0.0
        df["agressao_compra"] = 0.0
        df["agressao_saldo"] = 0.0
        df["agressao_venda"] = 0.0
        df["vwap"] = df["ultimo"]

    else:
        raise ValueError("Arquivo com colunas insuficientes.")

    df["datetime"] = pd.to_datetime(
        df["data"].astype(str) + " " + df["hora"].astype(str),
        dayfirst=True,
        errors="coerce"
    )

    df = df.dropna(subset=["datetime"])
    df = df.sort_values("datetime")

    campos_numericos = [
        "ultimo",
        "abertura",
        "maximo",
        "minimo",
        "volume",
        "volume_quantidade",
        "delta",
        "saldo",
        "agressao_compra",
        "agressao_saldo",
        "agressao_venda",
        "vwap",
    ]

    for campo in campos_numericos:
        if campo in df.columns:
            df[campo] = df[campo].apply(limpar_numero)

    return df, tipo


def agregar_fractal(df, minutos):
    df = df.copy()
    df = df.set_index("datetime")

    agregado = df.resample(f"{minutos}min").agg({
        "ativo": "first",
        "data": "first",
        "hora": "first",
        "abertura": "first",
        "maximo": "max",
        "minimo": "min",
        "ultimo": "last",
        "volume": "sum",
        "volume_quantidade": "sum",
        "delta": "sum",
        "saldo": "last",
        "agressao_compra": "sum",
        "agressao_saldo": "sum",
        "agressao_venda": "sum",
        "vwap": "last",
    }).dropna(subset=["ativo", "ultimo"])

    saida = agregado.reset_index(drop=True)[[
        "ativo",
        "data",
        "hora",
        "abertura",
        "maximo",
        "minimo",
        "ultimo",
        "volume",
        "volume_quantidade",
        "delta",
        "saldo",
        "agressao_compra",
        "agressao_saldo",
        "agressao_venda",
        "vwap",
    ]]

    return saida


def nome_saida(caminho_csv, minutos):
    nome = os.path.basename(caminho_csv)

    nome = nome.replace("1min", f"{minutos}min")
    nome = nome.replace("1MIN", f"{minutos}MIN")
    nome = nome.replace("1_Min", f"{minutos}_Min")
    nome = nome.replace("1_MIN", f"{minutos}_MIN")

    if nome == os.path.basename(caminho_csv):
        nome = f"WIN_{minutos}min_" + os.path.basename(caminho_csv)

    return nome


def salvar(saida, pasta_destino, nome_arquivo):
    caminho_saida = os.path.join(pasta_destino, nome_arquivo)

    saida.to_csv(
        caminho_saida,
        sep=";",
        index=False,
        header=False,
        encoding="utf-8-sig"
    )

    return caminho_saida


def processar():
    print("\n" + "=" * 60)
    print("🌽 ZÉ DO EUCRÁZIO v0.3 - AGREGADOR INTELIGENTE")
    print("=" * 60)

    caminho_csv = encontrar_primeiro_csv()

    print("\nArquivo origem:")
    print(caminho_csv)

    df, tipo = carregar_csv(caminho_csv)

    print(f"\nTipo detectado : {tipo}")
    print(f"Linhas origem : {len(df)}")

    saida_2 = agregar_fractal(df, 2)
    arquivo_2 = salvar(
        saida_2,
        PASTA_2MIN,
        nome_saida(caminho_csv, 2)
    )

    saida_3 = agregar_fractal(df, 3)
    arquivo_3 = salvar(
        saida_3,
        PASTA_3MIN,
        nome_saida(caminho_csv, 3)
    )

    print("\nArquivos gerados:")
    print(f"2 MIN: {arquivo_2}")
    print(f"3 MIN: {arquivo_3}")

    print("\nResumo:")
    print(f"Linhas 2 min: {len(saida_2)}")
    print(f"Linhas 3 min: {len(saida_3)}")

    print("\nObservação:")
    if tipo == "HISTORICO_PROFIT":
        print("Arquivo histórico não possui Delta/Saldo/Agressões.")
        print("Esses campos foram preservados como 0.0.")
    else:
        print("Arquivo possui fluxo TRIN. Delta/Saldo/Agressões agregados.")

    print("=" * 60)


if __name__ == "__main__":
    processar()