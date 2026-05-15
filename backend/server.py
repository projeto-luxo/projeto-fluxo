from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import random
import asyncio

from backend.flow_data import gerar_sinal
from core.engine import Engine
from core.vwap_engine import VWAPEngine
from core.candle_engine import CandleEngine
from core.aggression_engine import AggressionEngine


app = FastAPI(
    title="TRIN FLOW PRO",
    version="5.8.1 WS HARDENED"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)


engine = Engine()
vwap_engine = VWAPEngine()
candle_engine = CandleEngine()
aggression_engine = AggressionEngine()

historico = []
preco_atual = 100.0


def gerar_candle():
    global preco_atual

    abertura = preco_atual
    fechamento = abertura + random.uniform(-0.8, 0.8)

    maxima = max(abertura, fechamento) + random.uniform(0, 1)
    minima = min(abertura, fechamento) - random.uniform(0, 1)

    volume = random.randint(100, 1200)
    delta = random.randint(-300, 300)
    saldo = random.randint(-500, 500)

    candle = {
        "time": int(datetime.now().timestamp()),
        "open": round(abertura, 2),
        "high": round(maxima, 2),
        "low": round(minima, 2),
        "close": round(fechamento, 2),
        "volume": volume,
        "delta": delta,
        "saldo": saldo,
        "reversao_detectada": False
    }

    preco_atual = fechamento
    return candle


def atualizar_historico():
    candle = gerar_candle()

    candle_engine.adicionar_candle(candle)
    candle["reversao_detectada"] = candle_engine.calcular_reversao()

    vwap_engine.adicionar_candle(candle)

    historico.append(candle)

    if len(historico) > 100:
        historico.pop(0)

    return candle


def gerar_payload():
    if len(historico) < 2:
        atualizar_historico()
        atualizar_historico()

    anterior = historico[-2]
    atual = historico[-1]

    engine_data = engine.processar(atual, anterior)

    vwap, banda_sup, banda_inf = vwap_engine.calcular_vwap_e_bandas()

    distancia_vwap = (
        round(abs(atual["close"] - vwap[-1]["value"]), 2)
        if vwap else 0
    )

    freq, status, intensidade = aggression_engine.calcular_frequencia(
        atual["saldo"],
        atual["delta"],
        atual["volume"]
    )

    memoria = aggression_engine.calcular_memoria_agressao(
        atual["saldo"],
        atual["delta"],
        atual["volume"]
    )

    explosao, tipo_explosao = aggression_engine.detectar_explosao_fluxo(
        atual["saldo"],
        atual["delta"],
        atual["volume"],
        memoria["score_agressao"],
        intensidade
    )

    sinal_data = gerar_sinal(
        atual["saldo"],
        atual["volume"],
        atual["delta"],
        preco=atual["close"]
    )

    payload = {
        "historico": historico,

        "engine": engine_data,

        "vwap": vwap,
        "vwap_superior": banda_sup,
        "vwap_inferior": banda_inf,
        "distancia_vwap": distancia_vwap,

        "agressao": {
            "frequencia_mercado": freq,
            "status": status,
            "intensidade_fluxo": intensidade,
            **memoria,
            "explosao_detectada": explosao,
            "tipo_explosao": tipo_explosao
        },

        **sinal_data
    }

    return payload


@app.get("/data")
async def get_data():
    atualizar_historico()
    return gerar_payload()


@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()

    print("[WS CONNECT] cliente conectado")

    try:
        while True:
            atualizar_historico()
            payload = gerar_payload()

            await ws.send_json(payload)

            await asyncio.sleep(1)

    except WebSocketDisconnect:
        print("[WS DISCONNECT] cliente desconectado")

    except Exception as erro:
        print("[WS ERRO]", erro)

    finally:
        print("[WS CLOSE] conexão finalizada")