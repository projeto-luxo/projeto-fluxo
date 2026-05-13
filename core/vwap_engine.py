# core/vwap_engine.py
import math

class VWAPEngine:
    def __init__(self):
        self.candles = []

    def adicionar_candle(self, candle):
        self.candles.append(candle)
        if len(self.candles) > 120:
            self.candles = self.candles[-120:]

    def calcular_vwap_e_bandas(self, desvio=2):
        if not self.candles:
            return [], [], []

        vwap = []
        vwap_superior = []
        vwap_inferior = []

        soma_preco_volume = 0
        soma_volume = 0
        precos_medios = []

        for candle in self.candles:
            volume_candle = candle.get("volume", 1)
            preco_medio = (candle["high"] + candle["low"] + candle["close"]) / 3
            precos_medios.append(preco_medio)
            soma_preco_volume += preco_medio * volume_candle
            soma_volume += volume_candle
            valor_vwap = soma_preco_volume / soma_volume if soma_volume else candle["close"]
            media = sum(precos_medios) / len(precos_medios)
            variancia = sum((p - media) ** 2 for p in precos_medios) / len(precos_medios)
            desvio_padrao = math.sqrt(variancia)
            vwap.append({"time": candle["time"], "value": round(valor_vwap, 2)})
            vwap_superior.append({"time": candle["time"], "value": round(valor_vwap + desvio_padrao, 2)})
            vwap_inferior.append({"time": candle["time"], "value": round(valor_vwap - desvio_padrao, 2)})

        return vwap, vwap_superior, vwap_inferior