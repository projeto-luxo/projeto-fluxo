class CandleEngine:
    def __init__(self):
        self.candles = []

    def adicionar_candle(self, candle):
        self.candles.append(candle)
        if len(self.candles) > 120:
            self.candles = self.candles[-120:]
    def calcular_reversao(self):
        if len(self.candles) < 4:
            return False

        atual = self.candles[-1]
        anterior = self.candles[-2]
        antes = self.candles[-3]

        corpo_atual = abs(atual["close"] - atual["open"])
        range_atual = atual["high"] - atual["low"]

        if range_atual <= 0:
            return False

        candle_forte = corpo_atual >= range_atual * 0.45
        delta_forte = abs(atual.get("delta", 0)) >= 220
        volume_forte = atual.get("volume", 0) >= 600

        virou_para_cima = (
            antes["close"] < anterior["close"]
            and atual["close"] > anterior["open"]
            and atual["close"] > atual["open"]
        )

        virou_para_baixo = (
            antes["close"] > anterior["close"]
            and atual["close"] < anterior["open"]
            and atual["close"] < atual["open"]
        )

        rejeicao_fundo = (
            atual["low"] < anterior["low"]
            and atual["close"] > anterior["low"]
        )

        rejeicao_topo = (
            atual["high"] > anterior["high"]
            and atual["close"] < anterior["high"]
        )

        reversao_compra = virou_para_cima and rejeicao_fundo
        reversao_venda = virou_para_baixo and rejeicao_topo

        return (
            (reversao_compra or reversao_venda)
            and candle_forte
            and delta_forte
            and volume_forte
        )