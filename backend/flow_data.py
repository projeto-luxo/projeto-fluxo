# backend/flow_data.py

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

    if preco is not None:
        preco = float(preco)

        if saldo > 0:
            stop = round(preco - 0.5, 2)
            parcial = round(preco + 0.5, 2)
            alvo = round(preco + 1.0, 2)
        elif saldo < 0:
            stop = round(preco + 0.5, 2)
            parcial = round(preco - 0.5, 2)
            alvo = round(preco - 1.0, 2)
        else:
            stop = parcial = alvo = None
    else:
        stop = parcial = alvo = None

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