from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta
import random
import math
import asyncio

from flow_data import gerar_sinal

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

historico = []
fluxo_recente = []
memoria_agressao = []

preco_atual = 100.0
ultimo_minuto = None


def criar_candle(time_value):
    global preco_atual

    abertura = preco_atual
    fechamento = abertura + random.uniform(-0.8, 0.8)
    maxima = max(abertura, fechamento) + random.uniform(0.1, 0.6)
    minima = min(abertura, fechamento) - random.uniform(0.1, 0.6)

    preco_atual = fechamento

    return {
        "time": int(time_value),
        "open": round(abertura, 2),
        "high": round(maxima, 2),
        "low": round(minima, 2),
        "close": round(fechamento, 2),
        "volume": random.randint(100, 900),
        "reversao_detectada": False,
        "explosao_detectada": False,
    }


def iniciar_historico(qtd=120):
    global historico

    if historico:
        return

    agora = datetime.now() - timedelta(minutes=qtd)

    for i in range(qtd):
        candle_time = agora + timedelta(minutes=i)
        historico.append(criar_candle(candle_time.timestamp()))


def atualizar_candle():
    global historico, preco_atual, ultimo_minuto

    agora = datetime.now()
    minuto_atual = agora.replace(second=0, microsecond=0)

    if ultimo_minuto is None:
        ultimo_minuto = minuto_atual

    novo_preco = preco_atual + random.uniform(-0.35, 0.35)
    preco_atual = novo_preco

    if minuto_atual == ultimo_minuto and historico:
        candle = historico[-1]
        candle["close"] = round(novo_preco, 2)
        candle["high"] = round(max(candle["high"], novo_preco), 2)
        candle["low"] = round(min(candle["low"], novo_preco), 2)
    else:
        ultimo_minuto = minuto_atual
        abertura = historico[-1]["close"]

        historico.append({
            "time": int(minuto_atual.timestamp()),
            "open": round(abertura, 2),
            "high": round(max(abertura, novo_preco), 2),
            "low": round(min(abertura, novo_preco), 2),
            "close": round(novo_preco, 2),
            "volume": random.randint(100, 900),
            "reversao_detectada": False,
            "explosao_detectada": False,
        })

        if len(historico) > 300:
            historico = historico[-300:]


def calcular_vwap_e_bandas():
    vwap = []
    vwap_superior = []
    vwap_inferior = []

    soma_preco_volume = 0
    soma_volume = 0
    precos_medios = []

    for candle in historico:
        volume_candle = candle.get("volume", 1)
        preco_medio = (candle["high"] + candle["low"] + candle["close"]) / 3

        precos_medios.append(preco_medio)

        soma_preco_volume += preco_medio * volume_candle
        soma_volume += volume_candle

        valor_vwap = soma_preco_volume / soma_volume if soma_volume else candle["close"]

        media = sum(precos_medios) / len(precos_medios)
        variancia = sum((p - media) ** 2 for p in precos_medios) / len(precos_medios)
        desvio = math.sqrt(variancia)

        vwap.append({"time": candle["time"], "value": round(valor_vwap, 2)})
        vwap_superior.append({"time": candle["time"], "value": round(valor_vwap + desvio, 2)})
        vwap_inferior.append({"time": candle["time"], "value": round(valor_vwap - desvio, 2)})

    return vwap, vwap_superior, vwap_inferior


def calcular_frequencia(saldo_agressor, delta, volume):
    global fluxo_recente

    intensidade = abs(saldo_agressor) + abs(delta) + (volume / 2)
    fluxo_recente.append(intensidade)

    if len(fluxo_recente) > 30:
        fluxo_recente = fluxo_recente[-30:]

    media = sum(fluxo_recente) / len(fluxo_recente)

    if media > 1300:
        return "FREQUÊNCIA ALTA", "MERCADO ACELERADO", round(media, 2)

    if media > 800:
        return "FREQUÊNCIA MÉDIA", "MERCADO ATIVO", round(media, 2)

    return "FREQUÊNCIA BAIXA", "MERCADO LENTO", round(media, 2)


def calcular_memoria_agressao(saldo_agressor, delta, volume):
    global memoria_agressao

    memoria_agressao.append({
        "saldo": saldo_agressor,
        "delta": delta,
        "volume": volume,
    })

    if len(memoria_agressao) > 20:
        memoria_agressao = memoria_agressao[-20:]

    compras = sum(1 for x in memoria_agressao if x["saldo"] > 0 and x["delta"] > 0)
    vendas = sum(1 for x in memoria_agressao if x["saldo"] < 0 and x["delta"] < 0)

    saldo_total = sum(x["saldo"] for x in memoria_agressao)
    delta_total = sum(x["delta"] for x in memoria_agressao)
    volume_total = sum(x["volume"] for x in memoria_agressao)

    persistencia_compra = round((compras / len(memoria_agressao)) * 100, 2)
    persistencia_venda = round((vendas / len(memoria_agressao)) * 100, 2)

    score_agressao = round(
        (saldo_total / 100)
        + (delta_total / 50)
        + (volume_total / 1000),
        2
    )

    if persistencia_compra >= 60 and score_agressao > 10:
        leitura = "PERSISTÊNCIA COMPRADORA"
    elif persistencia_venda >= 60 and score_agressao < -10:
        leitura = "PERSISTÊNCIA VENDEDORA"
    elif abs(score_agressao) < 8:
        leitura = "AGRESSÃO NEUTRA"
    else:
        leitura = "AGRESSÃO INSTÁVEL"

    return {
        "persistencia_compra": persistencia_compra,
        "persistencia_venda": persistencia_venda,
        "score_agressao": score_agressao,
        "leitura_agressao": leitura,
    }


def detectar_explosao_fluxo(saldo_agressor, delta, volume, score_agressao, intensidade_fluxo):
    if (
        saldo_agressor > 850
        and delta > 350
        and volume > 1200
        and score_agressao > 18
        and intensidade_fluxo > 1300
    ):
        return True, "BUY EXPLOSION"

    if (
        saldo_agressor < -850
        and delta < -350
        and volume > 1200
        and score_agressao < -18
        and intensidade_fluxo > 1300
    ):
        return True, "SELL EXPLOSION"

    return False, "SEM EXPLOSÃO"


def gerar_payload():
    iniciar_historico()
    atualizar_candle()

    ultimo = historico[-1]
    preco = ultimo["close"]

    saldo_agressor = random.randint(-1000, 1000)
    delta = random.randint(-500, 500)
    volume = random.randint(100, 1500)

    resultado = gerar_sinal(saldo_agressor, volume, delta, preco)

    vwap, vwap_superior, vwap_inferior = calcular_vwap_e_bandas()
    vwap_atual = vwap[-1]["value"]

    distancia_vwap = abs(preco - vwap_atual)
    movimento_candle = abs(ultimo["close"] - ultimo["open"])

    reversao_forte = (
        distancia_vwap > 1.5
        and movimento_candle > 0.8
        and abs(delta) > 180
    )

    ultimo["reversao_detectada"] = reversao_forte

    reversao = "REVERSÃO DETECTADA" if reversao_forte else "SEM REVERSÃO"

    pressao_compra = random.randint(0, 100)
    pressao_venda = 100 - pressao_compra

    frequencia_mercado, modo_mercado, intensidade_fluxo = calcular_frequencia(
        saldo_agressor,
        delta,
        volume,
    )

    memoria = calcular_memoria_agressao(
        saldo_agressor,
        delta,
        volume,
    )

    explosao_detectada, tipo_explosao = detectar_explosao_fluxo(
        saldo_agressor,
        delta,
        volume,
        memoria["score_agressao"],
        intensidade_fluxo,
    )

    ultimo["explosao_detectada"] = explosao_detectada

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

        "reversao": reversao,
        "preco_atual": preco,
        "saldo_agressor": saldo_agressor,
        "delta": delta,
        "volume": volume,
        "pressao_compra": pressao_compra,
        "pressao_venda": pressao_venda,
        "sinal": resultado["sinal"],

        "frequencia_mercado": frequencia_mercado,
        "intensidade_fluxo": intensidade_fluxo,
        "modo_mercado": modo_mercado,

        "persistencia_compra": memoria["persistencia_compra"],
        "persistencia_venda": memoria["persistencia_venda"],
        "score_agressao": memoria["score_agressao"],
        "leitura_agressao": memoria["leitura_agressao"],

        "explosao_detectada": explosao_detectada,
        "tipo_explosao": tipo_explosao,
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
            await asyncio.sleep(1.0)

    except Exception:
        pass