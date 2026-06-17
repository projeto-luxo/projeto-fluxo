memoria = []

def atualizar_memoria(scalper, sniper):
    global memoria

    memoria.insert(0, sniper)

    if len(memoria) > 30:
        memoria.pop()

    return memoria


def tendencia_macro(memoria):

    if len(memoria) < 5:
        return "NEUTRO"

    compra = 0
    venda = 0

    for m in memoria:

        if "COMPRA" in m:
            compra += 2

        elif "VENDA" in m:
            venda += 2

        elif "ACUMULAÇÃO" in m:
            compra += 1

        elif "DISTRIBUIÇÃO" in m:
            venda += 1

        elif "EXPANSÃO" in m:
            compra += 1
            venda += 1  # neutro forte

    if compra > venda + 2:
        return "ALTA"

    elif venda > compra + 2:
        return "BAIXA"

    else:
        return "LATERAL"