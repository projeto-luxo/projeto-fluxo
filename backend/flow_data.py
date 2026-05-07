# flow_data.py
from datetime import datetime, timedelta
import random

def gerar_sinal(saldo, volume, delta):
    """
    Função completa do TRIN:
    Retorna sinal, força, entrada, tendência, absorção, zona quente, exaustão,
    stop, parcial, alvo e vwap
    """

    # 🔹 BLOQUEIO RUÍDO
    if abs(saldo) < 120 or abs(delta) < 60:
        return {
            "sinal": "SEM ENTRADA",
            "forca": 0,
            "entrada": "AGUARDAR",
            "tendencia": "MERCADO LATERAL",
            "absorcao": "SEM ABSORÇÃO",
            "zona_quente_absorcao": False,
            "exaustao": False,
            "stop": None,
            "parcial": None,
            "alvo": None,
            "vwap": None
        }

    # 🔹 FORÇA
    if saldo > 400 and delta > 200:
        sinal = "COMPRA FORTE"
        forca = 3
    elif saldo < -400 and delta < -200:
        sinal = "VENDA FORTE"
        forca = 3
    elif saldo > 250 and delta > 120:
        sinal = "COMPRA MÉDIA"
        forca = 2
    elif saldo < -250 and delta < -120:
        sinal = "VENDA MÉDIA"
        forca = 2
    elif abs(saldo) > 200 and abs(delta) > 80:
        sinal = "ATENÇÃO"
        forca = 1
    else:
        sinal = "SEM ENTRADA"
        forca = 0

    # 🔹 ENTRADAS
    confirmado = forca >= 2
    persistencia = random.randint(0, 10)
    entrada_conservadora = confirmado and persistencia >= 5
    entrada_scalping = abs(delta) > 200 and abs(saldo) > 400

    if entrada_conservadora:
        entrada = "EXECUTAR CONSERVADOR"
    elif entrada_scalping:
        entrada = "EXECUTAR SCALPING"
    else:
        entrada = "AGUARDAR"

    # 🔹 EXAUSTÃO
    exaustao = abs(delta) > 350 and volume > 1200 and abs(saldo) > 700

    # 🔹 TENDÊNCIA INSTITUCIONAL
    if forca >= 3 and saldo > 300:
        tendencia = "TENDÊNCIA FORTE DE COMPRA"
    elif forca >= 3 and saldo < -300:
        tendencia = "TENDÊNCIA FORTE DE VENDA"
    else:
        tendencia = "MERCADO LATERAL"

    # 🔹 HISTÓRICO PARA VWAP E CANDLES
    historico = []
    vwap = []
    hora = datetime.now() - timedelta(minutes=50)
    p = 100.0
    soma_preco_volume = 0
    soma_volume = 0

    for _ in range(50):
        open_p = p
        movimento = random.uniform(-1.0, 1.0)
        close_p = max(open_p + movimento, 1)
        high_p = max(open_p, close_p) + random.uniform(0.1, 1.2)
        low_p = min(open_p, close_p) - random.uniform(0.1, 1.2)
        volume_candle = random.randint(100, 1500)
        preco_medio = (high_p + low_p + close_p) / 3

        soma_preco_volume += preco_medio * volume_candle
        soma_volume += volume_candle
        vwap_valor = soma_preco_volume / soma_volume

        historico.append({
            "time": int(hora.timestamp()),
            "open": round(open_p, 2),
            "high": round(high_p, 2),
            "low": round(low_p, 2),
            "close": round(close_p, 2),
            "volume": volume_candle
        })

        vwap.append({
            "time": int(hora.timestamp()),
            "value": round(vwap_valor, 2)
        })

        p = close_p
        hora += timedelta(minutes=1)

    ultimo = historico[-1]

    # 🔹 ABSORÇÃO E ZONA QUENTE
    absorcao = "SEM ABSORÇÃO"
    zona_absorcao = None
    zona_quente_absorcao = False

    absorcao_compra = delta > 150 and saldo > 300
    absorcao_venda = delta < -150 and saldo < -300

    if absorcao_compra:
        absorcao = "ABSORÇÃO DE COMPRA"
        zona_absorcao = round(ultimo["low"], 2)
    elif absorcao_venda:
        absorcao = "ABSORÇÃO DE VENDA"
        zona_absorcao = round(ultimo["high"], 2)

    if absorcao != "SEM ABSORÇÃO" and abs(saldo) > 500 and volume > 900:
        zona_quente_absorcao = True

    # 🔹 STOP, PARCIAL, ALVO
    if saldo > 0:
        stop = round(ultimo["close"] - 0.5, 2)
        parcial = round(ultimo["close"] + 0.5, 2)
        alvo = round(ultimo["close"] + 1.0, 2)
    else:
        stop = round(ultimo["close"] + 0.5, 2)
        parcial = round(ultimo["close"] - 0.5, 2)
        alvo = round(ultimo["close"] - 1.0, 2)

    return {
        "sinal": sinal,
        "forca": forca,
        "entrada": entrada,
        "tendencia": tendencia,
        "absorcao": absorcao,
        "zona_absorcao": zona_absorcao,
        "zona_quente_absorcao": zona_quente_absorcao,
        "exaustao": exaustao,
        "stop": stop,
        "parcial": parcial,
        "alvo": alvo,
        "historico": historico,
        "vwap": vwap
    }