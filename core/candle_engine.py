# core/candle_engine.py
class CandleEngine:
    def __init__(self):
        self.candles = []

    def adicionar_candle(self, candle):
        self.candles.append(candle)
        if len(self.candles) > 50:
            self.candles = self.candles[-50:]

    def calcular_reversao(self):
        if len(self.candles) < 2:
            return False
        atual = self.candles[-1]
        anterior = self.candles[-2]
        if (anterior['close'] > anterior['open'] and atual['close'] < atual['open']) or \
           (anterior['close'] < anterior['open'] and atual['close'] > atual['open']):
            return True
        return False