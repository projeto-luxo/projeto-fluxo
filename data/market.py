import random

def gerar_candle(base):
    open_ = base
    close = open_ + random.randint(-5, 5)

    high = max(open_, close) + random.randint(0, 4)
    low = min(open_, close) - random.randint(0, 4)

    # 🔥 AQUI FOI O AJUSTE
    delta = random.randint(-400, 400)

    return {
        "open": open_,
        "close": close,
        "high": high,
        "low": low,
        "delta": delta
    }