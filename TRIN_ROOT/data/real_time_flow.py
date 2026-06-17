import random

def gerar_candle(preco_base):

    open_ = preco_base
    close = open_ + random.randint(-5, 5)

    high = max(open_, close) + random.randint(0, 4)
    low = min(open_, close) - random.randint(0, 4)

    delta = random.randint(-300, 300)

    return {
        "open": open_,
        "close": close,
        "high": high,
        "low": low,
        "delta": delta
    }