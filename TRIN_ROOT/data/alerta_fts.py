import winsound
import time

ultimo_alerta = ""
ultimo_tempo = 0

COOLDOWN = 5  # segundos

def alerta_sonoro(score, alinhamento, tendencia):
    global ultimo_alerta, ultimo_tempo

    agora = time.time()

    # Evita spam por tempo
    if agora - ultimo_tempo < COOLDOWN:
        return

    tipo = None

    # =========================
    # REGRAS
    # =========================
    if score >= 9 and "ALINHADO COMPRA" in alinhamento and tendencia == "ALTA":
        tipo = "COMPRA"

    elif score >= 9 and "ALINHADO VENDA" in alinhamento and tendencia == "BAIXA":
        tipo = "VENDA"

    elif score >= 7:
        tipo = "ATENCAO"

    elif score <= 3:
        tipo = "EVITAR"

    # Evita repetir alerta
    if tipo == ultimo_alerta:
        return

    # =========================
    # SOM
    # =========================
    try:
        if tipo == "COMPRA":
            winsound.Beep(1200, 200)
            winsound.Beep(1500, 200)

        elif tipo == "VENDA":
            winsound.Beep(800, 200)
            winsound.Beep(600, 200)

        elif tipo == "ATENCAO":
            winsound.Beep(1000, 150)

        elif tipo == "EVITAR":
            winsound.Beep(400, 200)

    except:
        pass

    # Atualiza estado
    ultimo_alerta = tipo
    ultimo_tempo = agora