from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta
import random

app = FastAPI()

# Permitir conexão do frontend
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

@app.get("/fluxo")
def fluxo():
    candles = gerar_candles()
    ultimo = candles[-1]["close"]
    stop = round(ultimo + random.uniform(-2, -1), 2)
    parcial = round(ultimo + random.uniform(-1, 0), 2)
    alvo = round(ultimo + random.uniform(0.5, 1.5), 2)

    return {
        "historico": candles,
        "stop": stop,
        "parcial": parcial,
        "alvo": alvo,
        "entrada": random.choice(["EXECUTAR CONSERVADOR", "EXECUTAR SCALPING", "PREPARAR"]),
        "direcao": random.choice(["COMPRA", "VENDA", "NEUTRO"]),
        "modo": random.choice(["CONSERVADOR", "SCALPING"]),
        "score": random.randint(1, 10),
        "padrao": random.choice(["FORTE", "MEDIO", "FRACO"]),
        "confirmado": random.choice([True, False]),
        "preco_atual": ultimo,
        "pressao_compra": random.randint(20, 80),
        "pressao_venda": random.randint(20, 80)
    }