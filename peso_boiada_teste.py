import time
import win32com.client

print("=== TRIN - PESO DA BOIADA VIVO / RTD 4 ===")

ARQUIVO_ALVO = "MARCO_ZERO_TRIN_RTD_4.xlsx"

COLUNAS = {
    "Asset": "A2",
    "Data": "B2",
    "Hora": "C2",
    "Ultimo": "D2",
    "Abertura": "E2",
    "Maximo": "F2",
    "Minimo": "G2",
    "Volume": "H2",
    "AAR_Delta": "I2",
    "TR_Saldo": "J2",
    "TR_Volume_1": "K2",
    "TR_Volume_2": "L2",
    "TR_Volume_3": "M2",
    "VWAP": "N2",
}
historico = []


def conectar_excel():
    excel = win32com.client.GetActiveObject("Excel.Application")

    for livro in excel.Workbooks:
        print("Planilha aberta:", livro.Name)

        if livro.Name.lower() == ARQUIVO_ALVO.lower():
            return livro.ActiveSheet

    print(f"ERRO: {ARQUIVO_ALVO} não está aberta no Excel.")
    raise SystemExit


def ler(ws, celula):
    try:
        valor = ws.Range(celula).Value

        if valor in (None, -2146826246, -2146826281, -2146826259):
            return None

        return valor

    except Exception:
        return None


def para_numero(valor):
    if valor is None:
        return None

    if isinstance(valor, (int, float)):
        return float(valor)

    texto = str(valor).strip()

    if texto in ("", "---", "#N/D", "#N/A"):
        return None

    texto = texto.replace(".", "").replace(",", ".")

    try:
        return float(texto)
    except ValueError:
        return None


def classificar_boiada(historico):
    altas = 0
    baixas = 0

    for i in range(1, len(historico)):
        if historico[i] > historico[i - 1]:
            altas += 1
        elif historico[i] < historico[i - 1]:
            baixas += 1

    peso = abs(altas - baixas)

    if peso <= 2:
        return "🐀 GABIRU", peso, altas, baixas
    elif peso <= 5:
        return "🐄 BOIADA FRACA", peso, altas, baixas
    elif peso <= 8:
        return "🐂 BOIADA FORTE", peso, altas, baixas
    else:
        return "🐂🔥 BOIADA EXTRA", peso, altas, baixas


ws = conectar_excel()

print("\nLendo planilha oficial:")
print(ARQUIVO_ALVO)
print("\nMapa:")
for nome, celula in COLUNAS.items():
    print(f"{nome.upper()} = {celula}")

print("\nPressione CTRL + C para parar.\n")

while True:
    try:
        dados = {nome: ler(ws, celula) for nome, celula in COLUNAS.items()}

        ultimo_num = para_numero(dados["ultimo"])

        if ultimo_num is not None:
            historico.append(ultimo_num)

        if len(historico) > 10:
            historico = historico[-10:]

        classificacao, peso, altas, baixas = classificar_boiada(historico)

        status = "OK" if ultimo_num is not None else "AGUARDANDO RTD"

        print(
            f"Ativo={dados['Asset']} | "
            f"Data={dados['Data']} | "
            f"Hora={dados['Hora']} | "
            f"ULT={dados['Ultimo']} | "
            f"VOL={dados['Volume']} | "
            f"Delta={dados['AAR_Delta']} | "
            f"Saldo={dados['TR_Saldo']} | "
            f"VWAP={dados['VWAP']} | "
            f"Altas={altas} | Baixas={baixas} | "
            f"Peso={peso}/10 | {classificacao}"
        )

        time.sleep(1)

    except KeyboardInterrupt:
        print("\nTRIN encerrado.")
        break