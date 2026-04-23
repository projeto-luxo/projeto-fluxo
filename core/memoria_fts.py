memoria = []

def atualizar_memoria(scalper, sniper):
    global memoria

    registro = f"{scalper}|{sniper}"
    memoria.insert(0, registro)

    if len(memoria) > 30:
        memoria.pop()

    return memoria