
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
# HISTORIADOR PADROES v1.0
# Missao: preparar catalogo inicial de padroes a serem minerados.
# Ainda nao detecta trades; cria mapa oficial para fases futuras.
# ============================================================


def gerar_padroes_iniciais():
    padroes = [
        ("HP001", "REVERSAO_VWAP", "Reversao perto da VWAP apos perda de agressao contraria"),
        ("HP002", "EXAUSTAO_COMPRA", "Compra agressiva perde eficiencia perto de maxima/regiao extrema"),
        ("HP003", "EXAUSTAO_VENDA", "Venda agressiva perde eficiencia perto de minima/regiao extrema"),
        ("HP004", "ABSORCAO", "Fluxo agressivo aparece sem deslocamento proporcional do preco"),
        ("HP005", "ROMPIMENTO_COM_FLUXO", "Rompimento acompanhado de volume, delta e saldo favoraveis"),
        ("HP006", "FALSO_ROMPIMENTO", "Rompimento sem continuidade com retorno para dentro da regiao"),
    ]
    df = pd.DataFrame([
        {"codigo": c, "padrao": p, "descricao": d, "status": "PREPARADO_PARA_MINERACAO", "origem": "HISTORIADOR_v1_0"}
        for c, p, d in padroes
    ])
    return salvar_csv(df, "catalogo_padroes_historiador.csv")


if __name__ == "__main__":
    print(f"Catalogo de padroes criado: {gerar_padroes_iniciais()}")
