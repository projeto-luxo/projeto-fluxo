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
        "reversao_detectada": False,
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

    atual["explosao_detectada"] = explosao
    atual["tipo_explosao"] = tipo_explosao

    sinal_data = gerar_sinal(
        atual["saldo"],
        atual["volume"],
        atual["delta"],
        preco=atual["close"]
    )

    # ==============================
    # ENTRADA INSTITUCIONAL TRIN 5.8.1
    # ==============================
    engine_score = engine_data.get("engine_score", 0)
    engine_fase = engine_data.get("engine_fase", "AGUARDANDO")
    engine_direcao = engine_data.get("engine_direcao", "NEUTRO")
    engine_seq_delta = engine_data.get("engine_seq_delta", 0)
    engine_trap = engine_data.get("engine_trap")
    engine_absorcao = engine_data.get("engine_absorcao", False)

    score_agressao = memoria.get("score_agressao", 0)

    entrada_institucional = "AGUARDAR"

    if explosao and tipo_explosao == "BUY EXPLOSION":
        entrada_institucional = "COMPRA SCALPING CONTROLADO"

    elif explosao and tipo_explosao == "SELL EXPLOSION":
        entrada_institucional = "VENDA SCALPING CONTROLADO"

    elif (
        engine_score >= 6
        and engine_fase == "ROMPIMENTO"
        and engine_direcao == "COMPRA"
        and engine_seq_delta >= 2
        and atual["delta"] > 180
        and not engine_absorcao
    ):
        entrada_institucional = "COMPRA CONSERVADORA"

    elif (
        engine_score >= 6
        and engine_fase == "ROMPIMENTO"
        and engine_direcao == "VENDA"
        and engine_seq_delta <= -2
        and atual["delta"] < -180
        and not engine_absorcao
    ):
        entrada_institucional = "VENDA CONSERVADORA"

    elif (
        engine_fase == "DISTRIBUICAO"
        and engine_direcao == "VENDA"
        and atual["delta"] < -120
        and not engine_absorcao
    ):
        entrada_institucional = "VENDA MODERADA"

    elif (
        engine_fase == "ACUMULACAO"
        and engine_direcao == "COMPRA"
        and atual["delta"] > 120
        and not engine_absorcao
    ):
        entrada_institucional = "COMPRA MODERADA"

    elif (
        engine_score >= 5
        and engine_direcao == "COMPRA"
        and score_agressao > 5
        and (engine_trap == "COMPRA" or engine_absorcao)
    ):
        entrada_institucional = "COMPRA MODERADA"

    elif (
        engine_score >= 5
        and engine_direcao == "VENDA"
        and score_agressao < -5
        and (engine_trap == "VENDA" or engine_absorcao)
    ):
        entrada_institucional = "VENDA MODERADA"

    sinal_data["entrada"] = entrada_institucional

    # ==============================
    # ALERTA OPERACIONAL TRIN
    # ==============================
    alerta_operacional = "AGUARDANDO CONFIRMAÇÃO"

    if (
        engine_fase == "COMPRESSAO"
        and atual["delta"] < -100
        and score_agressao < -5
        and not engine_absorcao
    ):
        alerta_operacional = "ALERTA: PRESSÃO VENDEDORA EM COMPRESSÃO"

    elif (
        engine_fase == "COMPRESSAO"
        and atual["delta"] > 100
        and score_agressao > 5
        and not engine_absorcao
    ):
        alerta_operacional = "ALERTA: PRESSÃO COMPRADORA EM COMPRESSÃO"

    elif (
        engine_fase == "DISTRIBUICAO"
        and engine_direcao == "VENDA"
    ):
        alerta_operacional = "ALERTA: DISTRIBUIÇÃO VENDEDORA"

    elif (
        engine_fase == "ACUMULACAO"
        and engine_direcao == "COMPRA"
    ):
        alerta_operacional = "ALERTA: ACUMULAÇÃO COMPRADORA"

    elif engine_fase == "ROMPIMENTO":
        alerta_operacional = "ALERTA: ROMPIMENTO EM ANDAMENTO"

    sinal_data["tendencia"] = alerta_operacional
    # ==============================
    # GESTÃO INSTITUCIONAL DINÂMICA
    # STOP / PARCIAL / ALVO
    # ==============================
    zona_low = engine_data.get("engine_zona_low")
    zona_high = engine_data.get("engine_zona_high")
    preco_entrada = atual["close"]

    stop = sinal_data.get("stop")
    parcial = sinal_data.get("parcial")
    alvo = sinal_data.get("alvo")

    if zona_low is not None and zona_high is not None:
        zona_low = float(zona_low)
        zona_high = float(zona_high)
        preco_entrada = float(preco_entrada)

        range_zona = max(zona_high - zona_low, 0.5)
        buffer = max(range_zona * 0.20, 0.15)

        if entrada_institucional in [
           "COMPRA MODERADA",
           "COMPRA CONSERVADORA",
           "COMPRA SCALPING CONTROLADO",
        ] and engine_direcao == "COMPRA":
            stop = round(zona_low - buffer, 2)
            parcial = round(preco_entrada + range_zona, 2)
            alvo = round(preco_entrada + (range_zona * 2), 2)

        elif entrada_institucional in [
            "VENDA MODERADA",
            "VENDA CONSERVADORA",
            "VENDA SCALPING CONTROLADO",
        ] and engine_direcao == "VENDA":
            stop = round(zona_high + buffer, 2)
            parcial = round(preco_entrada - range_zona, 2)
            alvo = round(preco_entrada - (range_zona * 2), 2)

    sinal_data["stop"] = stop
    sinal_data["parcial"] = parcial
    sinal_data["alvo"] = alvo

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
            "tipo_explosao": tipo_explosao,
        },

        **sinal_data,
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