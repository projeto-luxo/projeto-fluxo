from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta
import random
import asyncio

from backend.flow_data import gerar_sinal
from core.engine import Engine
from core.vwap_engine import VWAPEngine
from core.candle_engine import CandleEngine
from core.aggression_engine import AggressionEngine


app = FastAPI(title="TRIN FLOW PRO", version="5.5 WS RESTAURADO")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


engine = Engine()
vwap_engine = VWAPEngine()
candle_engine = CandleEngine()
aggression_engine = AggressionEngine()

historico = []
preco_atual = 100.0

tempo_base = datetime.now() - timedelta(minutes=120)
contador_candle = 0


def proximo_time():
    global contador_candle

    tempo = tempo_base + timedelta(minutes=contador_candle)
    contador_candle += 1

    return int(tempo.timestamp())


def gerar_candle():
    global preco_atual

    abertura = preco_atual
    fechamento = abertura + random.uniform(-0.8, 0.8)
    maxima = max(abertura, fechamento) + random.uniform(0.1, 0.6)
    minima = min(abertura, fechamento) - random.uniform(0.1, 0.6)

    volume = random.randint(100, 1500)
    delta = random.randint(-500, 500)
    saldo_agressor = random.randint(-1000, 1000)

    preco_atual = fechamento

    return {
        "time": proximo_time(),
        "open": round(abertura, 2),
        "high": round(maxima, 2),
        "low": round(minima, 2),
        "close": round(fechamento, 2),
        "volume": volume,
        "delta": delta,
        "saldo_agressor": saldo_agressor,
        "reversao_detectada": False,
        "explosao_detectada": False,
    }


def atualizar_historico():
    candle = gerar_candle()

    historico.append(candle)

    if len(historico) > 120:
        historico.pop(0)

    candle_engine.adicionar_candle(candle)
    vwap_engine.adicionar_candle(candle)

    return candle


def garantir_historico_inicial():
    while len(historico) < 60:
        atualizar_historico()


def gerar_payload():
    garantir_historico_inicial()

    atual = atualizar_historico()
    anterior = historico[-2] if len(historico) > 1 else None

    preco = atual["close"]
    saldo_agressor = atual["saldo_agressor"]
    delta = atual["delta"]
    volume = atual["volume"]

    resultado = gerar_sinal(
        saldo_agressor,
        volume,
        delta,
        preco,
    )

    engine_data = engine.processar(
        atual,
        anterior,
    )

    vwap, vwap_superior, vwap_inferior = vwap_engine.calcular_vwap_e_bandas()

    frequencia_mercado, modo_mercado, intensidade_fluxo = (
        aggression_engine.calcular_frequencia(
            saldo_agressor,
            delta,
            volume,
        )
    )

    memoria = aggression_engine.calcular_memoria_agressao(
        saldo_agressor,
        delta,
        volume,
    )

    explosao_detectada, tipo_explosao = aggression_engine.detectar_explosao_fluxo(
        saldo_agressor,
        delta,
        volume,
        memoria["score_agressao"],
        intensidade_fluxo,
    )

    pressao_compra = random.randint(0, 100)
    pressao_venda = 100 - pressao_compra

    reversao_detectada = candle_engine.calcular_reversao()

    atual["reversao_detectada"] = reversao_detectada
    atual["explosao_detectada"] = explosao_detectada

    historico[-1] = atual

    return {
        "historico": historico,

        "vwap": vwap,
        "vwap_superior": vwap_superior,
        "vwap_inferior": vwap_inferior,

        "forca": resultado["forca"],
        "entrada": resultado["entrada"],
        "tendencia": resultado["tendencia"],
        "absorcao": resultado["absorcao"],
        "zona_absorcao": resultado["zona_absorcao"],
        "zona_quente_absorcao": resultado["zona_quente_absorcao"],
        "exaustao": resultado["exaustao"],

        "stop": resultado["stop"],
        "parcial": resultado["parcial"],
        "alvo": resultado["alvo"],

        "sinal": resultado["sinal"],

        "reversao": "REVERSÃO DETECTADA" if reversao_detectada else "SEM REVERSÃO",
        "preco_atual": preco,

        "saldo_agressor": saldo_agressor,
        "delta": delta,
        "volume": volume,

        "pressao_compra": pressao_compra,
        "pressao_venda": pressao_venda,

        "frequencia_mercado": frequencia_mercado,
        "modo_mercado": modo_mercado,
        "intensidade_fluxo": intensidade_fluxo,

        "persistencia_compra": memoria["persistencia_compra"],
        "persistencia_venda": memoria["persistencia_venda"],
        "score_agressao": memoria["score_agressao"],
        "leitura_agressao": memoria["leitura_agressao"],

        "explosao_detectada": explosao_detectada,
        "tipo_explosao": tipo_explosao,

        "engine_score": engine_data["engine_score"],
        "engine_direcao": engine_data["engine_direcao"],
        "engine_fase": engine_data["engine_fase"],
        "engine_absorcao": engine_data["engine_absorcao"],
        "engine_trap": engine_data["engine_trap"],
        "engine_seq_delta": engine_data["engine_seq_delta"],
        "engine_zona_low": engine_data["engine_zona_low"],
        "engine_zona_high": engine_data["engine_zona_high"],
    }


@app.get("/")
def home():
    return {
        "projeto": "TRIN FLOW PRO",
        "status": "ONLINE",
        "versao": "5.5 WS RESTAURADO",
    }


@app.get("/data")
def data():
    return gerar_payload()


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    try:
        while True:
            payload = gerar_payload()
            await websocket.send_json(payload)
            await asyncio.sleep(1)

    except WebSocketDisconnect:
        print("Cliente WebSocket desconectado.")

    except Exception as erro:
        print(f"Erro WebSocket TRIN: {erro}")