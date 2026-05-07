from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta
import random
from flow_data import gerar_sinal

app = FastAPI()

# Permite conexão do frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def gerar_candles(qtd=50):
    candles = []
    preco = 100.0
    hora = datetime.now() - timedelta(minutes=qtd)
    for _ in range(qtd):
        open_p = preco
        high_p = open_p + random.uniform(0, 2)
        low_p = open_p - random.uniform(0, 2)
        close_p = random.uniform(low_p, high_p)
        candles.append({
            "time": int(hora.timestamp()),
            "open": round(open_p, 2),
            "high": round(high_p, 2),
            "low": round(low_p, 2),
            "close": round(close_p, 2)
        })
        preco = close_p
        hora += timedelta(minutes=1)
    return candles

@app.get("/data")
def get_data():
    candles = gerar_candles()
    ultimo = candles[-1]

    saldo = random.randint(-1000, 1000)
    delta = random.randint(-500, 500)
    volume = random.randint(100, 1500)

    sinal_data = gerar_sinal(saldo, volume, delta)

    # Reversão simples
    reversao = "REVERSÃO DETECTADA" if abs(delta) > 250 else "SEM REVERSÃO"

    return {
        "timestamp": datetime.now().strftime("%H:%M:%S"),
        "preco_atual": ultimo["close"],
        "saldo_agressor": saldo,
        "delta": delta,
        "volume": volume,
        "historico": sinal_data["historico"],
        "vwap": sinal_data["vwap"],
        "sinal": sinal_data["sinal"],
        "forca": sinal_data["forca"],
        "entrada": sinal_data["entrada"],
        "tendencia": sinal_data["tendencia"],
        "absorcao": sinal_data["absorcao"],
        "zona_absorcao": sinal_data["zona_absorcao"],
        "zona_quente_absorcao": sinal_data["zona_quente_absorcao"],
        "exaustao": sinal_data["exaustao"],
        "stop": sinal_data["stop"],
        "parcial": sinal_data["parcial"],
        "alvo": sinal_data["alvo"],
        "reversao": reversao
    }