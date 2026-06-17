MEMÓRIA DO TRIN

Data de início:
04/06/2026

Status:
TRIN_GRAVADOR v1 operacional.

Objetivo:
Capturar continuamente dados RTD do Profit via Excel e salvar em CSV diário.

Sequência operacional obrigatória:
1) Abrir Profit
2) Esperar conectar
3) Abrir Excel
4) Abrir MARCO_ZERO_INSTITUCIONAL.xlsx
5) Confirmar que o RTD está atualizando
6) Rodar TRIN_GRAVADOR.py

Arquivo gerado:
TRIN_MEMORIA_AAAA_MM_DD.csv

Campos coletados:
timestamp_pc
ativo
data
hora
ultimo
abertura
maximo
minimo
volume
delta
saldo
agressao_compra
agressao_saldo
agressao_venda
vwap

Regra:
TRIN_GRAVADOR não analisa, não calcula sinal e não interpreta.
Ele apenas grava dados brutos.

Observação:
Se aparecer #N/D, verificar se o Profit foi aberto antes do Excel.