import win32com.client
import time
import csv
import os
from datetime import datetime

print("=== TRIN GRAVADOR v1 ===")

ARQUIVO_ALVO = "MARCO_ZERO_INSTITUCIONAL.xlsx"
PASTA_MEMORIA = "memoria"

if not os.path.exists(PASTA_MEMORIA):
    os.makedirs(PASTA_MEMORIA)

nome_csv = datetime.now().strftime("TRIN_MEMORIA_%Y_%m_%d.csv")
caminho_csv = os.path.join(PASTA_MEMORIA, nome_csv)

try:
    excel = win32com.client.GetActiveObject("Excel.Application")
except Exception:
    print("Excel não encontrado aberto.")
    print("Abra primeiro: Profit → Excel → planilha RTD.")
    exit()

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
    print("Abra o Excel com a planilha correta antes de rodar.")
    exit()

ws = wb.ActiveSheet


def valor_invalido(valor):
    if valor is None:
        return True

    texto = str(valor).strip().upper()

    if texto in ["#N/D", "#N/A", "N/D", "N/A", ""]:
        return True

    return False


def ler_celulas():
    return {
        "ativo": ws.Range("A2").Value,
        "data": ws.Range("B2").Value,
        "hora": ws.Range("C2").Value,
        "ultimo": ws.Range("D2").Value,
        "abertura": ws.Range("E2").Value,
        "maximo": ws.Range("F2").Value,
        "minimo": ws.Range("G2").Value,
        "volume": ws.Range("H2").Value,
        "delta": ws.Range("I2").Value,
        "saldo": ws.Range("J2").Value,
        "agressao_compra": ws.Range("K2").Value,
        "agressao_saldo": ws.Range("L2").Value,
        "agressao_venda": ws.Range("M2").Value,
        "vwap": ws.Range("N2").Value,
    }


cabecalho = [
    "timestamp_pc",
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
    "agressao_compra",
    "agressao_saldo",
    "agressao_venda",
    "vwap",
]

print(f"Planilha encontrada: {ARQUIVO_ALVO}")
print(f"Gravando em: {caminho_csv}")
print("Pressione CTRL + C para parar.")
print("=================================")

with open(caminho_csv, "a", newline="", encoding="utf-8-sig") as arquivo:
    writer = csv.writer(arquivo, delimiter=";")

    if arquivo.tell() == 0:
        writer.writerow(cabecalho)

    while True:
        try:
            dados = ler_celulas()

            campos_criticos = [
                dados["ativo"],
                dados["ultimo"],
                dados["volume"],
                dados["delta"],
                dados["saldo"],
                dados["vwap"],
            ]

            if any(valor_invalido(v) for v in campos_criticos):
                print("RTD ainda inválido (#N/D). Aguardando...")
                time.sleep(1)
                continue

            timestamp_pc = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            linha = [
                timestamp_pc,
                dados["ativo"],
                dados["data"],
                dados["hora"],
                dados["ultimo"],
                dados["abertura"],
                dados["maximo"],
                dados["minimo"],
                dados["volume"],
                dados["delta"],
                dados["saldo"],
                dados["agressao_compra"],
                dados["agressao_saldo"],
                dados["agressao_venda"],
                dados["vwap"],
            ]

            writer.writerow(linha)
            arquivo.flush()

            print(
                f"{timestamp_pc} | "
                f"{dados['ativo']} | "
                f"ULT: {dados['ultimo']} | "
                f"VOL: {dados['volume']} | "
                f"DELTA: {dados['delta']} | "
                f"SALDO: {dados['saldo']} | "
                f"VWAP: {dados['vwap']}"
            )

            time.sleep(1)

        except KeyboardInterrupt:
            print("\nTRIN_GRAVADOR encerrado pelo usuário.")
            break

        except Exception as erro:
            print("Excel ocupado ou erro temporário. Aguardando...")
            print("Erro:", erro)
            time.sleep(2)