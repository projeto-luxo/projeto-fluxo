import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# ==========================
# LOCALIZAR CSV MAIS RECENTE
# ==========================

pasta_memoria = Path("memoria")

arquivos = sorted(
    pasta_memoria.glob("TRIN_MEMORIA_*.csv"),
    key=lambda x: x.stat().st_mtime,
    reverse=True
)

if not arquivos:
    print("Nenhum arquivo de memória encontrado.")
    exit()

csv_path = arquivos[0]

print(f"Lendo: {csv_path}")

# ==========================
# LER CSV COM CABEÇALHO
# ==========================

df = pd.read_csv(
    csv_path,
    sep=";",
    engine="python"
)

# ==========================
# CONVERTER NUMÉRICOS
# ==========================

df["ultimo"] = pd.to_numeric(
    df["ultimo"],
    errors="coerce"
)

df["vwap"] = pd.to_numeric(
    df["vwap"],
    errors="coerce"
)

# ==========================
# CALIBRAÇÃO DE ESCALA
# ==========================

media_ultimo = df["ultimo"].dropna().abs().median()
media_vwap = df["vwap"].dropna().abs().median()

if media_ultimo > 10000 and media_vwap < 1000:
    print("Calibrando preço: ultimo / 1000")
    df["ultimo"] = df["ultimo"] / 1000

df["delta"] = pd.to_numeric(df["delta"], errors="coerce")

df["saldo"] = (
    df["saldo"]
    .astype(str)
    .str.replace(".", "", regex=False)
    .str.replace(",", ".", regex=False)
)
df["saldo"] = pd.to_numeric(df["saldo"], errors="coerce")

df["agressao_compra"] = (
    df["agressao_compra"]
    .astype(str)
    .str.replace(".", "", regex=False)
    .str.replace(",", ".", regex=False)
)
df["agressao_compra"] = pd.to_numeric(
    df["agressao_compra"],
    errors="coerce"
)

df["agressao_venda"] = (
    df["agressao_venda"]
    .astype(str)
    .str.replace(".", "", regex=False)
    .str.replace(",", ".", regex=False)
)
df["agressao_venda"] = pd.to_numeric(
    df["agressao_venda"],
    errors="coerce"
)

print("\nDELTA")
print(df["delta"].tail())

print("\nSALDO")
print(df["saldo"].tail())

print("\nSALDO ORIGINAL")
print(df["saldo"].tail())

# ==========================
# GRÁFICOS
# ==========================

fig, (ax1, ax2, ax3, ax4, ax5) = plt.subplots(
    5,
    1,
    figsize=(14, 18),
    sharex=True
)

ax1.plot(df.index, df["ultimo"], label="Preço", linewidth=1.2)
ax1.plot(df.index, df["vwap"], label="VWAP", linewidth=1.2)
ax1.set_title("TRIN - Preço x VWAP")
ax1.set_ylabel("Preço")
ax1.legend()
ax1.grid(True)

ax2.plot(df.index, df["delta"], label="Delta", linewidth=1.2)
ax2.set_title("TRIN - Delta")
ax2.set_ylabel("Delta")
ax2.legend()
ax2.grid(True)

ax3.plot(df.index, df["saldo"], label="Saldo", linewidth=1.2)
ax3.set_title("TRIN - Saldo")
ax3.set_ylabel("Saldo")
ax3.legend()
ax3.grid(True)

ax4.plot(df.index, df["agressao_compra"], label="Compra", linewidth=1.2)
ax4.set_title("TRIN - Volume de Agressão Compra")
ax4.set_ylabel("Compra")
ax4.legend()
ax4.grid(True)

ax5.plot(df.index, df["agressao_venda"], label="Venda", linewidth=1.2)
ax5.set_title("TRIN - Volume de Agressão Venda")
ax5.set_ylabel("Venda")
ax5.set_xlabel("Registros")
ax5.legend()
ax5.grid(True)

# ==========================
# SALVAR
# ==========================

saida = pasta_memoria / "GRAFICO_PRECO_VWAP.png"

plt.savefig(saida, dpi=150)

print(f"Gráfico salvo em: {saida}")

plt.show()