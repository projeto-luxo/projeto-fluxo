def gerar_sinal(saldo, volume, delta):

    # BLOQUEIO RUÍDO
    if abs(saldo) < 120 or abs(delta) < 60:
        return {"sinal": "SEM ENTRADA", "forca": 0}

    # FORTE
    if saldo > 400 and delta > 200:
        return {"sinal": "COMPRA FORTE", "forca": 3}

    if saldo < -400 and delta < -200:
        return {"sinal": "VENDA FORTE", "forca": 3}

    # MÉDIA
    if saldo > 250 and delta > 120:
        return {"sinal": "COMPRA MÉDIA", "forca": 2}

    if saldo < -250 and delta < -120:
        return {"sinal": "VENDA MÉDIA", "forca": 2}

    # ATENÇÃO
    if abs(saldo) > 200 and abs(delta) > 80:
        return {"sinal": "ATENÇÃO", "forca": 1}

    return {"sinal": "SEM ENTRADA", "forca": 0}