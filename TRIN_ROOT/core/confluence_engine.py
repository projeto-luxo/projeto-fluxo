# core/confluence_engine.py

class ConfluenceEngine:
    def __init__(self):
        self.history = []

    def _num(self, valor, default=0.0):
        try:
            if valor is None:
                return default

            texto = str(valor).strip()

            if texto == "" or texto.lower() in ["none", "nan"]:
                return default

            texto = texto.replace(".", "")
            texto = texto.replace(",", ".")

            return float(texto)

        except Exception:
            return default

    def process(self, tick: dict):
        ultimo = self._num(tick.get("ultimo"))
        delta = self._num(tick.get("delta"))
        saldo = self._num(tick.get("saldo"))
        volume = self._num(tick.get("volume"))
        vwap = self._num(tick.get("vwap"))
        compra = self._num(tick.get("agressao_compra"))
        venda = self._num(tick.get("agressao_venda"))

        self.history.append({
            "saldo": saldo,
            "delta": delta,
            "volume": volume,
            "compra": compra,
            "venda": venda,
            "ultimo": ultimo,
            "vwap": vwap,
        })

        if len(self.history) > 20:
            self.history = self.history[-20:]

        compras = sum(
            1 for item in self.history
            if item["saldo"] > 0 and item["delta"] > 0
        )

        vendas = sum(
            1 for item in self.history
            if item["saldo"] < 0 and item["delta"] < 0
        )

        persistencia_compra = round((compras / len(self.history)) * 100, 2)
        persistencia_venda = round((vendas / len(self.history)) * 100, 2)

        direcao_fluxo = 0

        if saldo > 0 and delta > 0:
            direcao_fluxo = 1
        elif saldo < 0 and delta < 0:
            direcao_fluxo = -1
        elif delta > 0:
            direcao_fluxo = 0.5
        elif delta < 0:
            direcao_fluxo = -0.5

        score_base = (saldo / 10000) + (delta / 10000)

        peso_volume = min(volume / 800, 2) if volume > 0 else 1

        score_agressao = round(score_base * peso_volume, 2)

        if direcao_fluxo == 0:
            score_agressao = round(score_agressao * 0.5, 2)

        score_agressao += (compra - venda) / 100000

        if ultimo > 0 and vwap > 0:
            distancia_vwap = ultimo - vwap

            if abs(distancia_vwap) < 3000:
                score_agressao += distancia_vwap / 1000

        score_agressao = round(score_agressao, 2)

        if persistencia_compra >= 60 and score_agressao > 8:
            estado = "COMPRA_FORTE"
            forca = "PERSISTENCIA_COMPRADORA"
            pressao = "COMPRADORA"
            alerta = "🔥 PERSISTÊNCIA COMPRADORA"

        elif persistencia_venda >= 60 and score_agressao < -8:
            estado = "VENDA_FORTE"
            forca = "PERSISTENCIA_VENDEDORA"
            pressao = "VENDORA"
            alerta = "⚠ PERSISTÊNCIA VENDEDORA"

        elif score_agressao > 8:
            estado = "COMPRA_LEVE"
            forca = "AGRESSAO_COMPRADORA_INSTAVEL"
            pressao = "LEVEMENTE_COMPRADORA"
            alerta = None

        elif score_agressao < -8:
            estado = "VENDA_LEVE"
            forca = "AGRESSAO_VENDEDORA_INSTAVEL"
            pressao = "LEVEMENTE_VENDEDORA"
            alerta = None

        else:
            estado = "NEUTRO"
            forca = "BAIXA"
            pressao = "SEM_PRESSAO"
            alerta = None

        return {
            "score": score_agressao,
            "estado": estado,
            "forca": forca,
            "pressao": pressao,
            "alerta": alerta,
            "persistencia_compra": persistencia_compra,
            "persistencia_venda": persistencia_venda,
        }