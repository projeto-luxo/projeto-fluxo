from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta
import random
import math

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
preco_atual = 100.0
ultimo_minuto = None


def criar_candle(time_value):
    global preco_atual

    abertura = preco_atual
    fechamento = abertura + random.uniform(-0.8, 0.8)

    maxima = max(abertura, fechamento) + random.uniform(0.1, 0.6)
    minima = min(abertura, fechamento) - random.uniform(0.1, 0.6)

    volume_candle = random.randint(100, 900)

    preco_atual = fechamento

    return {
        "time": int(time_value),
        "open": round(abertura, 2),
        "high": round(maxima, 2),
        "low": round(minima, 2),
        "close": round(fechamento, 2),
        "volume": volume_candle,
        "reversao_detectada": abs(fechamento - abertura) > 1.2,
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
        candle["reversao_detectada"] = abs(candle["close"] - candle["open"]) > 1.2

    else:
        ultimo_minuto = minuto_atual
        abertura = historico[-1]["close"]

        novo_candle = {
            "time": int(minuto_atual.timestamp()),
            "open": round(abertura, 2),
            "high": round(max(abertura, novo_preco), 2),
            "low": round(min(abertura, novo_preco), 2),
            "close": round(novo_preco, 2),
            "volume": random.randint(100, 900),
            "reversao_detectada": abs(novo_preco - abertura) > 1.2,
        }

        historico.append(novo_candle)

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

        preco_medio = (
            candle["high"] + candle["low"] + candle["close"]
        ) / 3

        precos_medios.append(preco_medio)

        soma_preco_volume += preco_medio * volume_candle
        soma_volume += volume_candle

        valor_vwap = soma_preco_volume / soma_volume if soma_volume else candle["close"]

        media = sum(precos_medios) / len(precos_medios)
        variancia = sum((p - media) ** 2 for p in precos_medios) / len(precos_medios)
        desvio = math.sqrt(variancia)

        banda_superior = valor_vwap + desvio
        banda_inferior = valor_vwap - desvio

        vwap.append({
            "time": candle["time"],
            "value": round(valor_vwap, 2),
        })

        vwap_superior.append({
            "time": candle["time"],
            "value": round(banda_superior, 2),
        })

        vwap_inferior.append({
            "time": candle["time"],
            "value": round(banda_inferior, 2),
        })

    return vwap, vwap_superior, vwap_inferior


def calcular_frequencia(saldo_agressor, delta, volume):
    global fluxo_recente

    intensidade = abs(saldo_agressor) + abs(delta) + (volume / 2)
    fluxo_recente.append(intensidade)

    if len(fluxo_recente) > 30:
        fluxo_recente = fluxo_recente[-30:]

    media = sum(fluxo_recente) / len(fluxo_recente)

    if media > 1300:
        frequencia = "FREQUÊNCIA ALTA"
        modo = "MERCADO ACELERADO"
    elif media > 800:
        frequencia = "FREQUÊNCIA MÉDIA"
        modo = "MERCADO ATIVO"
    else:
        frequencia = "FREQUÊNCIA BAIXA"
        modo = "MERCADO LENTO"

    return {
        "frequencia_mercado": frequencia,
        "intensidade_fluxo": round(media, 2),
        "modo_mercado": modo,
    }


@app.get("/data")
def data():
    iniciar_historico()
    atualizar_candle()

    ultimo = historico[-1]
    preco = ultimo["close"]

    saldo_agressor = random.randint(-1000, 1000)
    delta = random.randint(-500, 500)
    volume = random.randint(100, 1500)

    resultado = gerar_sinal(
        saldo_agressor,
        volume,
        delta,
        preco
    )

    vwap, vwap_superior, vwap_inferior = calcular_vwap_e_bandas()
    vwap_atual = vwap[-1]["value"]

    tendencia = resultado["tendencia"]

    reversao_detectada = False

    if tendencia == "TENDÊNCIA FORTE DE COMPRA" and preco < vwap_atual:
        reversao_detectada = True

    elif tendencia == "TENDÊNCIA FORTE DE VENDA" and preco > vwap_atual:
        reversao_detectada = True

    ultimo["reversao_detectada"] = reversao_detectada or ultimo["reversao_detectada"]

    reversao = "REVERSÃO DETECTADA" if ultimo["reversao_detectada"] else "SEM REVERSÃO"

    pressao_compra = random.randint(0, 100)
    pressao_venda = 100 - pressao_compra

    frequencia = calcular_frequencia(saldo_agressor, delta, volume)

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

        "frequencia_mercado": frequencia["frequencia_mercado"],
        "intensidade_fluxo": frequencia["intensidade_fluxo"],
        "modo_mercado": frequencia["modo_mercado"],
    }