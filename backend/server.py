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

        vwap.append({
            "time": candle["time"],
            "value": round(valor_vwap, 2),
        })

        vwap_superior.append({
            "time": candle["time"],
            "value": round(valor_vwap + desvio, 2),
        })

        vwap_inferior.append({
            "time": candle["time"],
            "value": round(valor_vwap - desvio, 2),
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

    compras = sum(
        1 for x in memoria_agressao
        if x["saldo"] > 0 and x["delta"] > 0
    )

    vendas = sum(
        1 for x in memoria_agressao
        if x["saldo"] < 0 and x["delta"] < 0
    )

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


def detectar_ciclo_institucional(
    preco,
    vwap_atual,
    vwap_superior_atual,
    vwap_inferior_atual,
    memoria,
    frequencia_mercado,
    intensidade_fluxo,
    exaustao,
    absorcao,
):
    distancia_vwap = preco - vwap_atual

    persist_compra = memoria["persistencia_compra"]
    persist_venda = memoria["persistencia_venda"]
    score_agressao = memoria["score_agressao"]

    ciclo = "NEUTRO"
    risco = "BAIXO"
    contexto = "AGUARDAR CONFIRMAÇÃO"

    if absorcao != "SEM ABSORÇÃO" and abs(score_agressao) < 12:
        ciclo = "ACUMULAÇÃO"
        risco = "MÉDIO"
        contexto = "INSTITUCIONAL ABSORVENDO FLUXO"

    if (
        preco > vwap_atual
        and persist_compra >= 55
        and score_agressao > 12
        and frequencia_mercado in ["FREQUÊNCIA MÉDIA", "FREQUÊNCIA ALTA"]
    ):
        ciclo = "EXPANSÃO DE COMPRA"
        risco = "MÉDIO"
        contexto = "FLUXO COMPRADOR EM CONTINUIDADE"

    if (
        preco < vwap_atual
        and persist_venda >= 55
        and score_agressao < -8
        and frequencia_mercado in ["FREQUÊNCIA MÉDIA", "FREQUÊNCIA ALTA"]
    ):
        ciclo = "EXPANSÃO DE VENDA"
        risco = "MÉDIO"
        contexto = "FLUXO VENDEDOR EM CONTINUIDADE"

    if (
        preco > vwap_superior_atual
        and persist_compra < 40
        and intensidade_fluxo > 1000
    ):
        ciclo = "DISTRIBUIÇÃO"
        risco = "ALTO"
        contexto = "PREÇO ESTICADO COM COMPRA FRACA"

    if (
        preco < vwap_inferior_atual
        and persist_venda < 40
        and intensidade_fluxo > 1000
    ):
        ciclo = "ACUMULAÇÃO DEFENSIVA"
        risco = "ALTO"
        contexto = "PREÇO ESTICADO COM VENDA FRACA"

    if exaustao:
        ciclo = "EXAUSTÃO"
        risco = "ALTO"
        contexto = "RISCO DE REVERSÃO OU PAUSA FORTE"

    if (
        abs(distancia_vwap) > 2.0
        and abs(score_agressao) < 8
        and intensidade_fluxo > 1100
    ):
        ciclo = "ARMADILHA"
        risco = "ALTO"
        contexto = "MOVIMENTO FORTE SEM CONFIRMAÇÃO DE AGRESSÃO"

    return {
        "ciclo_institucional": ciclo,
        "risco_ciclo": risco,
        "contexto_ciclo": contexto,
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
    vwap_superior_atual = vwap_superior[-1]["value"]
    vwap_inferior_atual = vwap_inferior[-1]["value"]

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
        volume
    )

    memoria = calcular_memoria_agressao(
        saldo_agressor,
        delta,
        volume
    )

    ciclo = detectar_ciclo_institucional(
        preco,
        vwap_atual,
        vwap_superior_atual,
        vwap_inferior_atual,
        memoria,
        frequencia_mercado,
        intensidade_fluxo,
        resultado["exaustao"],
        resultado["absorcao"],
    )

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

        "ciclo_institucional": ciclo["ciclo_institucional"],
        "risco_ciclo": ciclo["risco_ciclo"],
        "contexto_ciclo": ciclo["contexto_ciclo"],
    }