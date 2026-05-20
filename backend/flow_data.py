# backend/flow_data.py

def calcular_gestao(preco, saldo, delta, volume, forca, exaustao, entrada):
    if preco is None:
        return None, None, None

    preco = float(preco)
    saldo = int(saldo or 0)
    delta = int(delta or 0)
    volume = int(volume or 0)

    intensidade = abs(saldo) + abs(delta) + (volume / 2)

    if intensidade >= 1200:
        range_base = 1.20
    elif intensidade >= 900:
        range_base = 1.00
    elif intensidade >= 650:
        range_base = 0.75
    else:
        range_base = 0.50

    if forca >= 3:
        multiplicador = 1.20
    elif forca == 2:
        multiplicador = 1.00
    else:
        multiplicador = 0.75

    if exaustao:
        multiplicador *= 0.70

    risco = round(range_base * multiplicador, 2)

    if risco < 0.35:
        risco = 0.35

    parcial_dist = round(risco * 1.20, 2)
    alvo_dist = round(risco * 2.20, 2)

    if "COMPRA" in entrada:
        stop = round(preco - risco, 2)
        parcial = round(preco + parcial_dist, 2)
        alvo = round(preco + alvo_dist, 2)

    elif "VENDA" in entrada:
        stop = round(preco + risco, 2)
        parcial = round(preco - parcial_dist, 2)
        alvo = round(preco - alvo_dist, 2)

    elif delta > 0:
        stop = round(preco - risco, 2)
        parcial = round(preco + parcial_dist, 2)
        alvo = round(preco + alvo_dist, 2)

    elif delta < 0:
        stop = round(preco + risco, 2)
        parcial = round(preco - parcial_dist, 2)
        alvo = round(preco - alvo_dist, 2)

    else:
        stop = parcial = alvo = None

    return stop, parcial, alvo


def gerar_sinal(saldo, volume, delta, preco=None):
    saldo = int(saldo or 0)
    volume = int(volume or 0)
    delta = int(delta or 0)

    if abs(saldo) < 120 or abs(delta) < 60:
        return {
            "sinal": "SEM ENTRADA",
            "forca": 0,
            "entrada": "AGUARDAR",
            "tendencia": "MERCADO LATERAL",
            "absorcao": "SEM ABSORÇÃO",
            "zona_absorcao": None,
            "zona_quente_absorcao": False,
            "exaustao": False,
            "stop": None,
            "parcial": None,
            "alvo": None,
        }

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

    exaustao = abs(delta) > 350 and volume > 1200 and abs(saldo) > 700

    if forca >= 3 and saldo > 300 and delta > 150:
        tendencia = "TENDÊNCIA FORTE DE COMPRA"
    elif forca >= 3 and saldo < -300 and delta < -150:
        tendencia = "TENDÊNCIA FORTE DE VENDA"
    elif saldo > 250 and delta > 100:
        tendencia = "TENDÊNCIA DE COMPRA"
    elif saldo < -250 and delta < -100:
        tendencia = "TENDÊNCIA DE VENDA"
    else:
        tendencia = "MERCADO LATERAL"

    absorcao = "SEM ABSORÇÃO"
    zona_absorcao = None

    if saldo > 400 and delta < -150 and volume > 700:
        absorcao = "ABSORÇÃO DE COMPRA"
    elif saldo < -400 and delta > 150 and volume > 700:
        absorcao = "ABSORÇÃO DE VENDA"

    if absorcao != "SEM ABSORÇÃO" and preco is not None:
        zona_absorcao = round(float(preco), 2)

    zona_quente_absorcao = (
        absorcao != "SEM ABSORÇÃO"
        and abs(saldo) > 500
        and volume > 900
    )

    entrada = "AGUARDAR"

    if (
        sinal == "COMPRA FORTE"
        and tendencia == "TENDÊNCIA FORTE DE COMPRA"
        and not exaustao
        and absorcao == "SEM ABSORÇÃO"
    ):
        entrada = "COMPRA CONSERVADORA"

    elif (
        sinal == "VENDA FORTE"
        and tendencia == "TENDÊNCIA FORTE DE VENDA"
        and not exaustao
        and absorcao == "SEM ABSORÇÃO"
    ):
        entrada = "VENDA CONSERVADORA"

    elif (
        abs(delta) > 220
        and abs(saldo) > 420
        and volume > 600
        and not exaustao
    ):
        entrada = "SCALPING CONTROLADO"

    stop, parcial, alvo = calcular_gestao(
        preco=preco,
        saldo=saldo,
        delta=delta,
        volume=volume,
        forca=forca,
        exaustao=exaustao,
        entrada=entrada,
    )

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
    }