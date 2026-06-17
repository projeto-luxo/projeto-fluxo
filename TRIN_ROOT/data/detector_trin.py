import sys
import time
from pathlib import Path
import win32com.client

TRIN_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TRIN_ROOT))

from core.confluence_engine import ConfluenceEngine
from core.memory_writer import MemoryWriter

engine = ConfluenceEngine()
writer = MemoryWriter()
# ==========================
# GARANTIR IMPORT DO CORE
# ==========================

TRIN_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TRIN_ROOT))

from core.confluence_engine import ConfluenceEngine
from core.memory_writer import MemoryWriter

print("=== TRIN DETECTOR + CONFLUÊNCIA + WRITER ===")

ARQUIVO_ALVO = "MARCO_ZERO_INSTITUCIONAL.xlsx"

engine = ConfluenceEngine()
writer = MemoryWriter()

try:
    excel = win32com.client.GetActiveObject("Excel.Application")
except Exception:
    excel = win32com.client.Dispatch("Excel.Application")

wb = None

for i in range(1, excel.Workbooks.Count + 1):
    livro = excel.Workbooks.Item(i)
    if livro.Name.lower() == ARQUIVO_ALVO.lower():
        wb = livro
        break

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
            return 0.0

        texto = str(valor).strip()

        if texto == "" or texto.lower() in ["none", "nan"]:
            return 0.0

        texto = texto.replace(".", "")
        texto = texto.replace(",", ".")

        return float(texto)

    except Exception:
        return 0.0


while True:
    try:
        ativo = ws.Range("A2").Value
        data = ws.Range("B2").Value
        hora = ws.Range("C2").Value

        ultimo = numero(ws.Range("D2").Value)
        abertura = numero(ws.Range("E2").Value)
        maximo = numero(ws.Range("F2").Value)
        minimo = numero(ws.Range("G2").Value)
        volume = numero(ws.Range("H2").Value)
        delta = numero(ws.Range("I2").Value)
        saldo = numero(ws.Range("J2").Value)
        agressao_compra = numero(ws.Range("K2").Value)
        agressao_saldo = numero(ws.Range("L2").Value)
        agressao_venda = numero(ws.Range("M2").Value)
        vwap = numero(ws.Range("N2").Value)

        tick = {
            "ativo": ativo,
            "data": data,
            "hora": hora,
            "ultimo": ultimo,
            "abertura": abertura,
            "maximo": maximo,
            "minimo": minimo,
            "volume": volume,
            "delta": delta,
            "saldo": saldo,
            "vwap": vwap,
            "agressao_compra": agressao_compra,
            "agressao_saldo": agressao_saldo,
            "agressao_venda": agressao_venda,
        }

        writer.write(tick)

        resultado = engine.process(tick)

        print(
            f"Ativo: {ativo} | Data: {data} | Hora: {hora} | "
            f"Último: {ultimo} | Volume: {volume} | Delta: {delta} | "
            f"Saldo: {saldo} | VWAP: {vwap}"
        )

        print(
            f"🔥 TRIN | Estado: {resultado['estado']} | "
            f"Força: {resultado['forca']} | "
            f"Pressão: {resultado['pressao']} | "
            f"Score: {resultado['score']}"
        )

        if resultado["alerta"]:
            print(f"🚨 {resultado['alerta']}")

        if ultimo_anterior is not None:
            if ultimo > ultimo_anterior:
                print(f"📈 SUBIU: {ultimo_anterior} -> {ultimo}")
            elif ultimo < ultimo_anterior:
                print(f"📉 CAIU: {ultimo_anterior} -> {ultimo}")

        if volume_anterior is not None and volume > volume_anterior:
            print(f"🐂 VOLUME + {int(volume - volume_anterior)}")

        ultimo_anterior = ultimo
        volume_anterior = volume

        print("-" * 80)

        time.sleep(2)

    except KeyboardInterrupt:
        print("\nTRIN encerrado.")
        break

    except Exception as erro:
        print("Excel ocupado ou erro no detector:", erro)
        time.sleep(2)