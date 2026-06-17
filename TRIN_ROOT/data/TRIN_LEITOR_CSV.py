import csv
import os
from datetime import datetime

PASTA_MEMORIA = "memoria"

print("=== TRIN LEITOR CSV v1 ===")

if not os.path.exists(PASTA_MEMORIA):
    print("Pasta memoria não encontrada.")
    exit()

arquivos = [
    f for f in os.listdir(PASTA_MEMORIA)
    if f.startswith("TRIN_MEMORIA_")
    and f.lower().endswith(".csv")
    and os.path.isfile(os.path.join(PASTA_MEMORIA, f))
]

if not arquivos:
    print("Nenhum CSV encontrado na pasta memoria.")
    exit()

arquivos.sort(reverse=True)
arquivo_csv = arquivos[0]
caminho = os.path.join(PASTA_MEMORIA, arquivo_csv)

print(f"Arquivo analisado: {arquivo_csv}")

with open(caminho, "r", encoding="utf-8-sig") as arquivo:
    leitor = list(csv.reader(arquivo, delimiter=";"))

if len(leitor) <= 1:
    print("CSV sem registros suficientes.")
    exit()

cabecalho = leitor[0]
linhas = leitor[1:]

primeira = linhas[0]
ultima = linhas[-1]

print("--------------------------------")
print(f"Total de registros: {len(linhas)}")
print(f"Primeiro registro: {primeira[0]}")
print(f"Último registro:   {ultima[0]}")

try:
    inicio = datetime.strptime(primeira[0], "%Y-%m-%d %H:%M:%S")
    fim = datetime.strptime(ultima[0], "%Y-%m-%d %H:%M:%S")
    duracao = fim - inicio
    print(f"Tempo coletado:    {duracao}")
except Exception:
    print("Não foi possível calcular o tempo coletado.")

print("--------------------------------")
print("Primeira linha:")
print(primeira)

print("--------------------------------")
print("Última linha:")
print(ultima)

print("--------------------------------")
print("Leitura concluída.")