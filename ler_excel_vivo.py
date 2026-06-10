import win32com.client
import time

print("=== TRIN EXCEL VIVO ===")

excel = win32com.client.GetActiveObject("Excel.Application")

wb = None

for livro in excel.Workbooks:
    if livro.Name.lower() == "marco_zero_institucional.xlsx":
        wb = livro
        break

if wb is None:
    print("Planilha MARCO_ZERO_INSTITUCIONAL.xlsx não encontrada aberta.")
    exit()

ws = wb.ActiveSheet

while True:

    try:

        ativo = ws.Range("A2").Value
        ultimo = ws.Range("D2").Value
        volume = ws.Range("H2").Value
        hora = ws.Range("C2").Value

        print(
            f"Ativo: {ativo} | "
            f"Último: {ultimo} | "
            f"Volume: {volume} | "
            f"Hora: {hora}"
        )

        time.sleep(2)

    except KeyboardInterrupt:
        print("\nTRIN encerrado.")
        break