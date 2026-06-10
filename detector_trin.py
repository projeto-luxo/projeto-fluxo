import win32com.client
import time

print("=== TRIN DETECTOR ===")

ARQUIVO_ALVO = "MARCO_ZERO_INSTITUCIONAL.xlsx"

try:
    excel = win32com.client.GetActiveObject("Excel.Application")
except Exception:
    excel = win32com.client.Dispatch("Excel.Application")

wb = None

try:
    for i in range(1, excel.Workbooks.Count + 1):
        livro = excel.Workbooks.Item(i)
        if livro.Name.lower() == ARQUIVO_ALVO.lower():
            wb = livro
            break
except Exception as erro:
    print("Excel ocupado ou inacessível:", erro)
    exit()

if wb is None:
    print(f"Planilha {ARQUIVO_ALVO} não encontrada aberta.")
    print(f"Abra o Excel e o arquivo {ARQUIVO_ALVO} antes de rodar.")
    exit()

ws = wb.ActiveSheet

ultimo_anterior = None
volume_anterior = None


def numero(valor):
    try:
        if valor is None:
            return None
        return float(valor)
    except Exception:
        return None


while True:
    try:
        ativo = ws.Range("A2").Value
        data = ws.Range("B2").Value
        hora = ws.Range("C2").Value

        ultimo = numero(ws.Range("D2").Value)
        volume = numero(ws.Range("H2").Value)
        delta = numero(ws.Range("I2").Value)
        saldo = numero(ws.Range("J2").Value)
        vwap = numero(ws.Range("N2").Value)

        if ultimo is None:
            time.sleep(1)
            continue

        print(
            f"Ativo: {ativo} | "
            f"Data: {data} | "
            f"Hora: {hora} | "
            f"Último: {ultimo} | "
            f"Volume: {volume} | "
            f"Delta: {delta} | "
            f"Saldo: {saldo} | "
            f"VWAP: {vwap}"
        )

        if ultimo_anterior is not None:
            if ultimo > ultimo_anterior:
                print(f"📈 SUBIU: {ultimo_anterior} -> {ultimo}")
            elif ultimo < ultimo_anterior:
                print(f"📉 CAIU: {ultimo_anterior} -> {ultimo}")

        if volume is not None and volume_anterior is not None:
            if volume > volume_anterior:
                print(f"🐂 VOLUME + {int(volume - volume_anterior)}")

        ultimo_anterior = ultimo

        if volume is not None:
            volume_anterior = volume

        time.sleep(2)

    except KeyboardInterrupt:
        print("\nTRIN encerrado.")
        break

    except Exception as erro:
        print("Excel ocupado, aguardando...", erro)
        time.sleep(2)