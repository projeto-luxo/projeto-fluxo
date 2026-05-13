# backend/flow_data.py
import random

def gerar_sinal(saldo, volume, delta, preco=None):
    if abs(saldo) < 120 or abs(delta) < 60:
        return {"sinal": "SEM ENTRADA", "forca": 0, "entrada": "AGUARDAR", "tendencia": "MERCADO LATERAL",
                "absorcao": "SEM ABSORÇÃO", "zona_absorcao": None, "zona_quente_absorcao": False,
                "exaustao": False, "stop": None, "parcial": None, "alvo": None}

    if saldo > 400 and delta > 200:
        sinal = "COMPRA FORTE"; forca = 3
    elif saldo < -400 and delta < -200:
        sinal = "VENDA FORTE"; forca = 3
    elif saldo > 250 and delta > 120:
        sinal = "COMPRA MÉDIA"; forca = 2
    elif saldo < -250 and delta < -120:
        sinal = "VENDA MÉDIA"; forca = 2
    elif abs(saldo) > 200 and abs(delta) > 80:
        sinal = "ATENÇÃO"; forca = 1
    else:
        sinal = "SEM ENTRADA"; forca = 0

    confirmado = forca >= 2
    persistencia = random.randint(0, 10)
    if confirmado and persistencia >= 5:
        entrada = "EXECUTAR CONSERVADOR"
    elif abs(delta) > 200 and abs(saldo) > 400:
        entrada = "EXECUTAR SCALPING"
    else:
        entrada = "AGUARDAR"

    exaustao = abs(delta) > 350 and volume > 1200 and abs(saldo) > 700
    if forca >= 3 and saldo > 300:
        tendencia = "TENDÊNCIA FORTE DE COMPRA"
    elif forca >= 3 and saldo < -300:
        tendencia = "TENDÊNCIA FORTE DE VENDA"
    else:
        tendencia = "MERCADO LATERAL"

    absorcao = "SEM ABSORÇÃO"
    zona_absorcao = None
    if saldo > 400 and delta < -150:
        absorcao = "ABSORÇÃO DE COMPRA"
    elif saldo < -400 and delta > 150:
        absorcao = "ABSORÇÃO DE VENDA"
    if absorcao != "SEM ABSORÇÃO" and preco is not None:
        zona_absorcao = round(preco, 2)
    zona_quente_absorcao = absorcao != "SEM ABSORÇÃO" and abs(saldo) > 500 and volume > 900

    if preco is not None:
        if saldo > 0:
            stop = round(preco - 0.5, 2); parcial = round(preco + 0.5, 2); alvo = round(preco + 1.0, 2)
        else:
            stop = round(preco + 0.5, 2); parcial = round(preco - 0.5, 2); alvo = round(preco - 1.0, 2)
    else:
        stop = parcial = alvo = None

    return {"sinal": sinal, "forca": forca, "entrada": entrada, "tendencia": tendencia,
            "absorcao": absorcao, "zona_absorcao": zona_absorcao,
            "zona_quente_absorcao": zona_quente_absorcao, "exaustao": exaustao,
            "stop": stop, "parcial": parcial, "alvo": alvo}