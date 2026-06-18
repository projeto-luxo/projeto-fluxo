
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
# HISTORIADOR DELTA v1.0
# Missao: consolidar estatisticas de delta quando existirem no indice.
# ============================================================


def gerar_estatistica_delta():
    indice = carregar_indice()
    colunas_base = ["ativo", "fractal", "arquivos", "linhas_total", "delta_medio_disponivel", "observacao"]

    if indice.empty:
        return salvar_csv(pd.DataFrame(columns=colunas_base), "estatistica_delta.csv")

    registros = []
    possui_delta = "delta_medio" in indice.columns

    if possui_delta:
        indice["delta_medio_num"] = numero_serie(indice["delta_medio"])

    for (ativo, fractal), grupo in indice.groupby(["ativo", "fractal"], dropna=False):
        registros.append({
            "ativo": ativo,
            "fractal": fractal,
            "arquivos": len(grupo),
            "linhas_total": int(numero_serie(grupo.get("linhas", 0)).fillna(0).sum()),
            "delta_medio_disponivel": round(float(grupo["delta_medio_num"].mean()), 2) if possui_delta and grupo["delta_medio_num"].notna().any() else "N/D",
            "observacao": "Indice possui delta_medio" if possui_delta else "Delta detalhado exige leitura dos CSV historicos na v1.1",
        })

    return salvar_csv(pd.DataFrame(registros).sort_values(["ativo", "fractal"]), "estatistica_delta.csv")


if __name__ == "__main__":
    print(f"Historiador delta concluido: {gerar_estatistica_delta()}")
