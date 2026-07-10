# core/candle_engine.py
class CandleEngine:
    def __init__(self):
        self.candles = []

    def adicionar_candle(self, candle):
        self.candles.append(candle)
        if len(self.candles) > 50:
            self.candles = self.candles[-50:]

    def adicionar_ou_atualizar_candle(self, candle):
        # Adiciona novo timestamp ou substitui o candle atual em formacao.
        copia = dict(candle)
        tempo = copia.get("time")
        mesmo_timestamp = (
            tempo is not None
            and bool(self.candles)
            and self.candles[-1].get("time") == tempo
        )

        if mesmo_timestamp:
            self.candles[-1] = copia
            operacao = "ATUALIZADO"
        else:
            self.candles.append(copia)
            operacao = "ADICIONADO"

        if len(self.candles) > 50:
            self.candles = self.candles[-50:]

        return operacao

    def calcular_reversao(self):
        if len(self.candles) < 2:
            return False
        atual = self.candles[-1]
        anterior = self.candles[-2]
        if (anterior['close'] > anterior['open'] and atual['close'] < atual['open']) or \
           (anterior['close'] < anterior['open'] and atual['close'] > atual['open']):
            return True
        return False