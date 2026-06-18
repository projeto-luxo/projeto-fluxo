
from pathlib import Path
import pandas as pd

TRIN_ROOT = Path(__file__).resolve().parents[1]
HISTORICO = TRIN_ROOT / "TRIN_HISTORICO"
INDICES = HISTORICO / "00_INDICES"
CONHECIMENTO = HISTORICO / "00_CONHECIMENTO"
CONHECIMENTO.mkdir(parents=True, exist_ok=True)

INDICE_GERAL = INDICES / "indice_geral.csv"
INDICE_WIN = INDICES / "indice_win.csv"
INDICE_WDO = INDICES / "indice_wdo.csv"


def carregar_indice():
    if not INDICE_GERAL.exists():
        raise FileNotFoundError(f"indice_geral.csv nao encontrado: {INDICE_GERAL}")
    df = pd.read_csv(INDICE_GERAL, sep=";", encoding="utf-8-sig")
    return df


def salvar_csv(df, nome):
    caminho = CONHECIMENTO / nome
    df.to_csv(caminho, sep=";", index=False, encoding="utf-8-sig")
    return caminho


def numero_serie(s):
    return pd.to_numeric(s, errors="coerce")

# ============================================================
# HISTORIADOR ESTATISTICO v1.0
# Missao: resumir a biblioteca por ativo e fractal.
# Nao altera dados historicos. Apenas gera conhecimento.
# ============================================================


def gerar_estatistica_biblioteca():
    indice = carregar_indice()
    if indice.empty:
        df = pd.DataFrame(columns=[
            "ativo", "fractal", "arquivos", "linhas_total", "tamanho_total_mb",
            "data_inicio", "data_fim", "alertas", "erros", "confiabilidade_media"
        ])
        return salvar_csv(df, "estatistica_biblioteca.csv")

    for col in ["linhas", "tamanho_mb", "confiabilidade"]:
        if col in indice.columns:
            indice[col] = numero_serie(indice[col]).fillna(0)

    if "data_inicio" in indice.columns:
        indice["data_inicio_dt"] = pd.to_datetime(indice["data_inicio"], dayfirst=True, errors="coerce")
    else:
        indice["data_inicio_dt"] = pd.NaT

    if "data_fim" in indice.columns:
        indice["data_fim_dt"] = pd.to_datetime(indice["data_fim"], dayfirst=True, errors="coerce")
    else:
        indice["data_fim_dt"] = pd.NaT

    registros = []
    for (ativo, fractal), grupo in indice.groupby(["ativo", "fractal"], dropna=False):
        registros.append({
            "ativo": ativo,
            "fractal": fractal,
            "arquivos": len(grupo),
            "linhas_total": int(grupo["linhas"].sum()) if "linhas" in grupo else 0,
            "tamanho_total_mb": round(float(grupo["tamanho_mb"].sum()), 3) if "tamanho_mb" in grupo else 0,
            "data_inicio": grupo["data_inicio_dt"].min().strftime("%d/%m/%Y") if grupo["data_inicio_dt"].notna().any() else "N/D",
            "data_fim": grupo["data_fim_dt"].max().strftime("%d/%m/%Y") if grupo["data_fim_dt"].notna().any() else "N/D",
            "alertas": int((grupo["status"] == "ALERTA").sum()) if "status" in grupo else 0,
            "erros": int((grupo["status"] == "ERRO").sum()) if "status" in grupo else 0,
            "confiabilidade_media": round(float(grupo["confiabilidade"].mean()), 2) if "confiabilidade" in grupo else "N/D",
        })

    df = pd.DataFrame(registros).sort_values(["ativo", "fractal"])
    return salvar_csv(df, "estatistica_biblioteca.csv")


if __name__ == "__main__":
    caminho = gerar_estatistica_biblioteca()
    print(f"Historiador estatistico concluido: {caminho}")
