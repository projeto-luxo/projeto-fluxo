def analisar_alinhamento(scalper, sniper):

    s = scalper.upper()
    n = sniper.upper()

    # =========================
    # ALINHAMENTO FORTE
    # =========================
    if "COMPRA" in s and "EXPANSÃO" in n:
        return "ALINHADO COMPRA (FORTE)", "#00ff00"

    if "VENDA" in s and "EXPANSÃO" in n:
        return "ALINHADO VENDA (FORTE)", "#ff0000"

    # =========================
    # PREPARAÇÃO
    # =========================
    if "COMPRA" in s and "ACUMULAÇÃO" in n:
        return "COMPRA EM PREPARAÇÃO", "#00ffff"

    if "VENDA" in s and "DISTRIBUIÇÃO" in n:
        return "VENDA EM PREPARAÇÃO", "#00ffff"

    # =========================
    # EXPANSÃO SEM DIREÇÃO
    # =========================
    if "EXPANSÃO" in n:
        return "EXPANSÃO EM ANDAMENTO", "#ffaa00"

    # =========================
    # TRANSIÇÃO
    # =========================
    if "TRANSIÇÃO" in n:
        return "MERCADO VIRANDO", "#9999ff"

    return "SEM ALINHAMENTO", "#555555"