import time
from datetime import datetime

try:
    import pythoncom
    import pywintypes
    import win32com.client
except ModuleNotFoundError as erro_importacao_com:
    pythoncom = None
    pywintypes = None
    win32com = None
    ERRO_IMPORTACAO_COM = erro_importacao_com
else:
    ERRO_IMPORTACAO_COM = None


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



def _exigir_com_excel():
    if ERRO_IMPORTACAO_COM is not None:
        raise RuntimeError(
            "DEPENDENCIA_EXCEL_COM_INDISPONIVEL: instale pywin32 e execute "
            "no Windows com o Excel aberto."
        ) from ERRO_IMPORTACAO_COM


CAMPOS_CRITICOS = [
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
    "vwap",
]


def _com_retry(func, tentativas=10, espera=0.08):
    _exigir_com_excel()
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


def valor_excel_invalido(valor):
    if valor is None:
        return True

    # Excel COM pode retornar erros de celula como inteiros HRESULT,
    # por exemplo #N/D / #N/A como valores negativos perto de -2146826xxx.
    if isinstance(valor, (int, float)):
        if valor <= -1000000000:
            return True
        return False

    texto = str(valor).strip()

    if texto in (
        "",
        "---",
        "#N/D",
        "#N/A",
        "#VALOR!",
        "#VALUE!",
        "#REF!",
        "#DIV/0!",
        "Atributo",
        "Atributo Inválido",
        "Atributo Inválido",
    ):
        return True

    return False


def para_numero(valor, padrao=0):
    if valor_excel_invalido(valor):
        return padrao

    if isinstance(valor, (int, float)):
        return float(valor)

    texto = str(valor).strip()
    texto = texto.replace(".", "").replace(",", ".")

    try:
        return float(texto)
    except ValueError:
        return padrao


def conectar_planilha():
    _exigir_com_excel()
    pythoncom.CoInitialize()

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


def validar_dados_rtd(dados):
    invalidos = {}

    for campo in CAMPOS_CRITICOS:
        valor = dados.get(campo)

        if valor_excel_invalido(valor):
            invalidos[campo] = str(valor)

    if invalidos:
        raise RuntimeError(
            "RTD_EXCEL_PLAN1_INVALIDO: células críticas sem dado válido: "
            f"{invalidos}"
        )


def ler_dados_institucionais():
    ws = conectar_planilha()

    dados = {
        nome: ler_celula(ws, celula)
        for nome, celula in CELULAS.items()
    }

    validar_dados_rtd(dados)

    preco = para_numero(dados["ultimo"])
    abertura_bruta = para_numero(dados["abertura"], 0)
    maximo_bruto = para_numero(dados["maximo"], 0)
    minimo_bruto = para_numero(dados["minimo"], 0)

    abertura_origem_confirmada = abertura_bruta > 0
    maxima_origem_confirmada = maximo_bruto > 0
    minima_origem_confirmada = minimo_bruto > 0

    abertura = abertura_bruta if abertura_origem_confirmada else preco
    maximo = maximo_bruto if maxima_origem_confirmada else preco
    minimo = minimo_bruto if minima_origem_confirmada else preco
    vwap_bruta = para_numero(dados["vwap"], 0)
    vwap_origem_confirmada = vwap_bruta > 0
    vwap = vwap_bruta if vwap_origem_confirmada else preco

    if preco <= 0:
        raise RuntimeError(f"RTD_EXCEL_PLAN1_INVALIDO: preço inválido: {preco}")

    volume_real = int(para_numero(dados["volume"]))
    delta_real = int(para_numero(dados["delta"]))
    saldo_real = int(para_numero(dados["saldo"]))

    volume_compra_real = int(para_numero(dados["volume_compra"]))
    volume_venda_real = int(para_numero(dados["volume_venda"]))
    volume_saldo_real = int(para_numero(dados["volume_saldo"]))

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

        "abertura_sessao": round(abertura, 2),
        "abertura_fonte": (
            "RTD_EXCEL_PLAN1_E2" if abertura_origem_confirmada else ""
        ),
        "abertura_origem_confirmada": abertura_origem_confirmada,

        "maxima_sessao": round(maximo, 2),
        "maxima_fonte": (
            "RTD_EXCEL_PLAN1_F2" if maxima_origem_confirmada else ""
        ),
        "maxima_origem_confirmada": maxima_origem_confirmada,

        "minima_sessao": round(minimo, 2),
        "minima_fonte": (
            "RTD_EXCEL_PLAN1_G2" if minima_origem_confirmada else ""
        ),
        "minima_origem_confirmada": minima_origem_confirmada,
        "ultimo": round(preco, 2),

        "volume": volume_trin,
        "volume_real": volume_real,

        "delta": delta_real,
        "saldo": saldo_real,

        "ativo": dados["ativo"],

        "vwap": round(vwap, 2),
        "vwap_real": round(vwap, 2),
        "vwap_origem_confirmada": vwap_origem_confirmada,

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
