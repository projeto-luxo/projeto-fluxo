import time
from datetime import datetime

import pythoncom
import pywintypes
import win32com.client


ARQUIVO_ALVO = "MARCO_ZERO_INSTITUCIONAL.xlsx"

ABAS_CANDIDATAS = [
    "PLAN1 RTD_PAINEL",
    "Plan1",
    "RTD_PAINEL",
]

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


def _com_retry(func, tentativas=10, espera=0.08):
    ultimo_erro = None

    for _ in range(tentativas):
        try:
            pythoncom.PumpWaitingMessages()
            return func()
        except pywintypes.com_error as erro:
            ultimo_erro = erro
            time.sleep(espera)

    raise ultimo_erro


def _nome_limpo(valor):
    return str(valor or "").strip().lower()


def para_numero(valor, padrao=0):
    if valor is None:
        return padrao

    if isinstance(valor, (int, float)):
        return float(valor)

    texto = str(valor).strip()

    if texto in ("", "---", "#N/D", "#N/A", "Atributo", "Atributo Inválido", "Atributo InvÃ¡lido"):
        return padrao

    texto = texto.replace(".", "").replace(",", ".")

    try:
        return float(texto)
    except ValueError:
        return padrao


def conectar_planilha():
    excel = _com_retry(lambda: win32com.client.GetActiveObject("Excel.Application"))

    qtd_livros = _com_retry(lambda: excel.Workbooks.Count)

    livro_alvo = None

    for i in range(1, qtd_livros + 1):
        livro = _com_retry(lambda i=i: excel.Workbooks(i))
        nome_livro = _nome_limpo(livro.Name)

        if nome_livro == _nome_limpo(ARQUIVO_ALVO):
            livro_alvo = livro
            break

        if "marco_zero_institucional" in nome_livro:
            livro_alvo = livro
            break

    if livro_alvo is None:
        raise RuntimeError(f"{ARQUIVO_ALVO} não está aberto no Excel.")

    qtd_abas = _com_retry(lambda: livro_alvo.Worksheets.Count)

    abas = []
    for i in range(1, qtd_abas + 1):
        aba = _com_retry(lambda i=i: livro_alvo.Worksheets(i))
        abas.append(str(aba.Name))

    for nome_desejado in ABAS_CANDIDATAS:
        for aba_nome in abas:
            if _nome_limpo(aba_nome) == _nome_limpo(nome_desejado):
                return _com_retry(lambda aba_nome=aba_nome: livro_alvo.Worksheets(aba_nome))

    for aba_nome in abas:
        nome = _nome_limpo(aba_nome)

        if "rtd_painel" in nome and "t.t" not in nome and "tt" not in nome:
            return _com_retry(lambda aba_nome=aba_nome: livro_alvo.Worksheets(aba_nome))

    raise RuntimeError(
        "Aba RTD operacional não encontrada. "
        f"Esperado: {ABAS_CANDIDATAS}. "
        f"Abas disponíveis: {abas}"
    )


def ler_celula(ws, celula):
    return _com_retry(lambda: ws.Range(celula).Value)


def ler_dados_institucionais():
    ws = conectar_planilha()

    dados = {
        nome: ler_celula(ws, celula)
        for nome, celula in CELULAS.items()
    }

    preco = para_numero(dados["ultimo"])
    abertura = para_numero(dados["abertura"], preco)
    maximo = para_numero(dados["maximo"], preco)
    minimo = para_numero(dados["minimo"], preco)
    vwap = para_numero(dados["vwap"], preco)

    volume_real = int(para_numero(dados["volume"]))
    delta_real = int(para_numero(dados["delta"]))
    saldo_real = int(para_numero(dados["saldo"]))

    volume_compra_real = int(para_numero(dados["volume_compra"]))
    volume_venda_real = int(para_numero(dados["volume_venda"]))
    volume_saldo_real = int(para_numero(dados["volume_saldo"]))

    # Volume normalizado para o motor TRIN.
    # O volume real continua preservado em volume_real.
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
        "ultimo": round(preco, 2),

        "volume": volume_trin,
        "volume_real": volume_real,

        "delta": delta_real,
        "saldo": saldo_real,

        "ativo": dados["ativo"],

        "vwap": round(vwap, 2),
        "vwap_real": round(vwap, 2),

        "volume_compra": volume_compra_real,
        "volume_venda": volume_venda_real,
        "volume_saldo": volume_saldo_real,

        "compra": volume_compra_real,
        "venda": volume_venda_real,

        "data_excel": str(dados["data"]),
        "hora_excel": str(dados["hora"]),

        "fonte_dados": "RTD_EXCEL_PLAN1",
        "aba_origem": "PLAN1 RTD_PAINEL",
        "reversao_detectada": False,
    }
