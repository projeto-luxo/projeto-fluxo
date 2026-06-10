import win32com.client
from datetime import datetime


ARQUIVO_ALVO = "MARCO_ZERO_INSTITUCIONAL.xlsx"
ABA_ALVO = "Plan1"

CELULAS = {
    "ativo": "A2",
    "data": "B2",
    "hora": "C2",
    "ultimo": "D2",
    "abertura": "E2",
    "maximo": "F2",
    "minimo": "G2",
    "volume": "H2",
    "delta": "I2",
    "saldo": "J2",
    "volume_compra": "K2",
    "volume_saldo": "L2",
    "volume_venda": "M2",
    "vwap": "N2",
}


def para_numero(valor, padrao=0):
    if valor is None:
        return padrao

    if isinstance(valor, (int, float)):
        return float(valor)

    texto = str(valor).strip()

    if texto in ("", "---", "#N/D", "#N/A", "Atributo", "Atributo Inválido"):
        return padrao

    texto = texto.replace(".", "").replace(",", ".")

    try:
        return float(texto)
    except ValueError:
        return padrao


def conectar_planilha():
    excel = win32com.client.GetActiveObject("Excel.Application")

    for livro in excel.Workbooks:
        if livro.Name.lower() == ARQUIVO_ALVO.lower():
            return livro.Worksheets(ABA_ALVO)

    raise RuntimeError(f"{ARQUIVO_ALVO} não está aberto no Excel.")


def ler_dados_institucionais():
    ws = conectar_planilha()

    dados = {
        nome: ws.Range(celula).Value
        for nome, celula in CELULAS.items()
    }

    preco = para_numero(dados["ultimo"])
    abertura = para_numero(dados["abertura"], preco)
    maximo = para_numero(dados["maximo"], preco)
    minimo = para_numero(dados["minimo"], preco)

    volume_real = int(para_numero(dados["volume"]))
    delta_real = int(para_numero(dados["delta"]))
    saldo_real = int(para_numero(dados["saldo"]))

    volume_compra_real = int(para_numero(dados["volume_compra"]))
    volume_venda_real = int(para_numero(dados["volume_venda"]))
    volume_saldo_real = int(para_numero(dados["volume_saldo"]))

    # ==============================
    # NORMALIZAÇÃO TRIN
    # ==============================
    # Mantém o volume real preservado,
    # mas entrega ao motor um volume proporcional,
    # para não explodir intensidade, score e frequência.
    volume_trin = int(volume_real / 100000000)

    if volume_trin < 0:
        volume_trin = 0

    if volume_trin > 5000:
        volume_trin = 5000

    return {
        "time": int(datetime.now().timestamp()),
        "open": round(abertura, 2),
        "high": round(maximo, 2),
        "low": round(minimo, 2),
        "close": round(preco, 2),

        # Volume usado pelo motor TRIN
        "volume": volume_trin,

        # Valores reais preservados
        "volume_real": volume_real,
        "delta": delta_real,
        "saldo": saldo_real,

        "ativo": dados["ativo"],
        "vwap_real": para_numero(dados["vwap"]),

        "volume_compra": volume_compra_real,
        "volume_venda": volume_venda_real,
        "volume_saldo": volume_saldo_real,

        "reversao_detectada": False,
    }