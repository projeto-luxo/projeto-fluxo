import time
import win32com.client

print("=== TRIN - LEITOR OFICIAL PLAN1 / MARCO ZERO INSTITUCIONAL ===")

ARQUIVO_ALVO = "MARCO_ZERO_INSTITUCIONAL.xlsx"
ABA_ALVO = "Plan1"

COLUNAS = {
    "Asset": "A2",
    "Data": "B2",
    "Hora": "C2",
    "Ultimo": "D2",
    "Abertura": "E2",
    "Maximo": "F2",
    "Minimo": "G2",
    "Volume": "H2",
    "TR_Delta": "I2",
    "TR_Saldo_Acumulado": "J2",
    "TR_Volume_Compra": "K2",
    "TR_Volume_Saldo": "L2",
    "TR_Volume_Venda": "M2",
    "VWAP": "N2",
}

historico = []


def conectar_planilha():
    try:
        excel = win32com.client.GetActiveObject("Excel.Application")
    except Exception:
        print("ERRO: Excel não está aberto.")
        print("Abra o Excel como administrador com MARCO_ZERO_INSTITUCIONAL.xlsx antes de rodar.")
        raise SystemExit

    for livro in excel.Workbooks:
        print("Planilha aberta:", livro.Name)

        if livro.Name.lower() == ARQUIVO_ALVO.lower():
            print(f"\nArquivo oficial encontrado: {livro.Name}")
            return livro.Worksheets(ABA_ALVO)

    print(f"\nERRO: {ARQUIVO_ALVO} não está aberto no Excel.")
    raise SystemExit


def ler_celula(ws, celula):
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

    if texto in ("", "---", "#N/D", "#N/A", "Atributo", "Atributo Inválido"):
        return None

    texto = texto.replace(".", "").replace(",", ".")

    try:
        return float(texto)
    except ValueError:
        return None


def classificar_boiada(historico_precos):
    altas = 0
    baixas = 0

    for i in range(1, len(historico_precos)):
        if historico_precos[i] > historico_precos[i - 1]:
            altas += 1
        elif historico_precos[i] < historico_precos[i - 1]:
            baixas += 1

    peso = abs(altas - baixas)

    if peso <= 2:
        classificacao = "GABIRU"
    elif peso <= 5:
        classificacao = "BOIADA FRACA"
    elif peso <= 8:
        classificacao = "BOIADA FORTE"
    else:
        classificacao = "BOIADA EXTRA"

    return classificacao, peso, altas, baixas


ws = conectar_planilha()

print("\nMapa oficial da Plan1:")
for nome, celula in COLUNAS.items():
    print(f"{nome} = {celula}")

print("\nPressione CTRL + C para parar.\n")

while True:
    try:
        dados = {
            nome: ler_celula(ws, celula)
            for nome, celula in COLUNAS.items()
        }

        ultimo_num = para_numero(dados["Ultimo"])

        if ultimo_num is not None:
            historico.append(ultimo_num)

        if len(historico) > 10:
            historico = historico[-10:]

        classificacao, peso, altas, baixas = classificar_boiada(historico)

        status = "OK" if ultimo_num is not None else "AGUARDANDO DADO"

        print(
            f"Status={status} | "
            f"Ativo={dados['Asset']} | "
            f"Data={dados['Data']} | "
            f"Hora={dados['Hora']} | "
            f"ULT={dados['Ultimo']} | "
            f"Abertura={dados['Abertura']} | "
            f"Max={dados['Maximo']} | "
            f"Min={dados['Minimo']} | "
            f"VOL={dados['Volume']} | "
            f"Delta={dados['TR_Delta']} | "
            f"SaldoAcum={dados['TR_Saldo_Acumulado']} | "
            f"VolCompra={dados['TR_Volume_Compra']} | "
            f"VolSaldo={dados['TR_Volume_Saldo']} | "
            f"VolVenda={dados['TR_Volume_Venda']} | "
            f"VWAP={dados['VWAP']} | "
            f"Altas={altas} | Baixas={baixas} | "
            f"Peso={peso}/10 | {classificacao}"
        )

        time.sleep(1)

    except KeyboardInterrupt:
        print("\nTRIN encerrado.")
        break

    except Exception as erro:
        print("Erro geral:", erro)
        time.sleep(1)