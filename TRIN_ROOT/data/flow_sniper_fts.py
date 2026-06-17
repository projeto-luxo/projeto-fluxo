def gerar_sniper(saldo, volume, delta):

    # =====================
    # LEITURA BASE (contexto)
    # =====================
    if abs(saldo) < 100:
        contexto = "LATERAL"
    elif saldo > 0:
        contexto = "ALTA"
    else:
        contexto = "BAIXA"

    # =====================
    # FASE DE MERCADO
    # =====================
    if volume > 700 and abs(delta) < 80:
        fase = "ACUMULAÇÃO" if saldo > 0 else "DISTRIBUIÇÃO"

    elif abs(delta) > 200:
        fase = "EXPANSÃO"

    elif abs(delta) > 120:
        fase = "TRANSIÇÃO"

    else:
        fase = "AGUARDANDO"

    # =====================
    # DECISÃO FINAL
    # =====================
    if fase == "ACUMULAÇÃO" and delta > 100:
        return {"sinal": "COMPRA SNIPER", "forca": 4}

    if fase == "DISTRIBUIÇÃO" and delta < -100:
        return {"sinal": "VENDA SNIPER", "forca": 4}

    if fase == "ACUMULAÇÃO":
        return {"sinal": "ACUMULAÇÃO", "forca": 1}

    if fase == "DISTRIBUIÇÃO":
        return {"sinal": "DISTRIBUIÇÃO", "forca": 1}

    if fase == "TRANSIÇÃO":
        return {"sinal": "TRANSIÇÃO", "forca": 2}

    if fase == "EXPANSÃO":
        return {"sinal": "EXPANSÃO", "forca": 3}

    return {"sinal": "AGUARDANDO", "forca": 0}