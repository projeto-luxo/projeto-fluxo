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
# HISTORIADOR TEMPORAL v1.0
# Missao: mapear cobertura temporal por ativo/fractal/arquivo.
# ============================================================


def gerar_cobertura_temporal():
    indice = carregar_indice()
    if indice.empty:
        df = pd.DataFrame(columns=["ativo", "fractal", "arquivo", "data_inicio", "data_fim", "anos_cobertos"])
        return salvar_csv(df, "cobertura_temporal.csv")

    registros = []
    for _, linha in indice.iterrows():
        data_i = pd.to_datetime(linha.get("data_inicio", "N/D"), dayfirst=True, errors="coerce")
        data_f = pd.to_datetime(linha.get("data_fim", "N/D"), dayfirst=True, errors="coerce")
        anos = "N/D"
        if pd.notna(data_i) and pd.notna(data_f):
            anos = ",".join(str(ano) for ano in range(data_i.year, data_f.year + 1))

        registros.append({
            "ativo": linha.get("ativo", "N/D"),
            "fractal": linha.get("fractal", "N/D"),
            "arquivo": linha.get("arquivo", "N/D"),
            "data_inicio": linha.get("data_inicio", "N/D"),
            "data_fim": linha.get("data_fim", "N/D"),
            "anos_cobertos": anos,
            "linhas": linha.get("linhas", 0),
            "status": linha.get("status", "N/D"),
        })

    df = pd.DataFrame(registros).sort_values(["ativo", "fractal", "data_inicio"])
    return salvar_csv(df, "cobertura_temporal.csv")


def gerar_distribuicao_fractais():
    indice = carregar_indice()
    if indice.empty:
        df = pd.DataFrame(columns=["fractal", "ativos", "arquivos", "linhas_total"])
        return salvar_csv(df, "distribuicao_fractais.csv")

    indice["linhas_num"] = numero_serie(indice.get("linhas", 0)).fillna(0)
    registros = []
    for fractal, grupo in indice.groupby("fractal", dropna=False):
        registros.append({
            "fractal": fractal,
            "ativos": ",".join(sorted(set(grupo["ativo"].astype(str)))) if "ativo" in grupo else "N/D",
            "arquivos": len(grupo),
            "linhas_total": int(grupo["linhas_num"].sum()),
            "status_ok": int((grupo["status"] == "OK").sum()) if "status" in grupo else 0,
            "status_alerta": int((grupo["status"] == "ALERTA").sum()) if "status" in grupo else 0,
        })

    df = pd.DataFrame(registros).sort_values("fractal")
    return salvar_csv(df, "distribuicao_fractais.csv")


if __name__ == "__main__":
    print(f"Cobertura temporal: {gerar_cobertura_temporal()}")
    print(f"Distribuicao fractais: {gerar_distribuicao_fractais()}")