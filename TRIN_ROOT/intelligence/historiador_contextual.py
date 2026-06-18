
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
# HISTORIADOR CONTEXTUAL v1.0
# Missao: criar contexto inicial para futuras leituras por horario/evento.
# ============================================================


def gerar_contexto_inicial():
    contextos = [
        ("ABERTURA", "09:00", "10:30", "Maior disputa inicial de fluxo"),
        ("MEIO_PREGAO", "10:31", "15:30", "Desenvolvimento do movimento e zonas de valor"),
        ("FECHAMENTO", "15:31", "18:20", "Zeragem, ajuste, defesa e distorcoes finais"),
        ("VENCIMENTO", "N/D", "N/D", "Vencimento de contratos pode distorcer historico"),
        ("ROLAGEM", "N/D", "N/D", "Periodo de transicao de contrato exige marcacao futura"),
    ]
    df = pd.DataFrame([
        {"contexto": n, "hora_inicio": i, "hora_fim": f, "descricao": d, "status": "CATALOGADO"}
        for n, i, f, d in contextos
    ])
    return salvar_csv(df, "contexto_historiador.csv")


if __name__ == "__main__":
    print(f"Contexto inicial criado: {gerar_contexto_inicial()}")
