# core/aggression_engine.py

class AggressionEngine:
    def __init__(self):
        self.fluxo_recente = []
        self.memoria_agressao = []

    def calcular_frequencia(self, saldo_agressor, delta, volume):
        intensidade = (
            abs(saldo_agressor) / 1000 +
            abs(delta) / 1000 +
           (volume / 100)
        )

        self.fluxo_recente.append(intensidade)

        if len(self.fluxo_recente) > 30:
            self.fluxo_recente = self.fluxo_recente[-30:]

        media = sum(self.fluxo_recente) / len(self.fluxo_recente)

        if media > 1300:
            return "FREQUÊNCIA ALTA", "MERCADO ACELERADO", round(media, 2)

        if media > 800:
            return "FREQUÊNCIA MÉDIA", "MERCADO ATIVO", round(media, 2)

        return "FREQUÊNCIA BAIXA", "MERCADO LENTO", round(media, 2)

    def calcular_memoria_agressao(self, saldo_agressor, delta, volume):
        print(
            f"[TRIN DEBUG] "
            f"SALDO={saldo_agressor} "
            f"DELTA={delta} "
            f"VOLUME={volume}"
        )

        self.memoria_agressao.append({
            "saldo": saldo_agressor,
            "delta": delta,
            "volume": volume
        })

        if len(self.memoria_agressao) > 20:
            self.memoria_agressao = self.memoria_agressao[-20:]

        compras = sum(
            1 for item in self.memoria_agressao
            if item["saldo"] > 0 and item["delta"] > 0
        )

        vendas = sum(
            1 for item in self.memoria_agressao
            if item["saldo"] < 0 and item["delta"] < 0
        )

        ultimo = self.memoria_agressao[-1]

        saldo_total = ultimo["saldo"]
        delta_total = ultimo["delta"]
        volume_total = ultimo["volume"]

        print(
            f"[MEMORIA AJUSTADA] "
            f"SALDO={saldo_total} "
            f"DELTA={delta_total} "
            f"VOLUME={volume_total}"
        )

        persistencia_compra = round(
            (compras / len(self.memoria_agressao)) * 100,
            2
        )

        persistencia_venda = round(
            (vendas / len(self.memoria_agressao)) * 100,
            2
        )

        volume_medio = volume_total

        direcao_fluxo = 0

        if saldo_total > 0 and delta_total > 0:
            direcao_fluxo = 1
        elif saldo_total < 0 and delta_total < 0:
            direcao_fluxo = -1
        elif delta_total > 0:
            direcao_fluxo = 0.5
        elif delta_total < 0:
            direcao_fluxo = -0.5

        score_base = (
            (saldo_total / 10000) +
            (delta_total / 10000)
        )

        peso_volume = min(volume_medio / 800, 2)

        score_agressao = round(
            score_base * peso_volume,
            2
        )

        if direcao_fluxo == 0:
            score_agressao = round(score_agressao * 0.5, 2)

        if persistencia_compra >= 60 and score_agressao > 8:
            leitura = "PERSISTÊNCIA COMPRADORA"

        elif persistencia_venda >= 60 and score_agressao < -8:
            leitura = "PERSISTÊNCIA VENDEDORA"

        elif score_agressao > 8:
            leitura = "AGRESSÃO COMPRADORA INSTÁVEL"

        elif score_agressao < -8:
            leitura = "AGRESSÃO VENDEDORA INSTÁVEL"

        else:
            leitura = "AGRESSÃO NEUTRA"

        return {
            "persistencia_compra": persistencia_compra,
            "persistencia_venda": persistencia_venda,
            "score_agressao": score_agressao,
            "leitura_agressao": leitura,
        }

    def detectar_explosao_fluxo(
        self,
        saldo_agressor,
        delta,
        volume,
        score_agressao,
        intensidade_fluxo
    ):
        if (
            saldo_agressor > 400 and
            delta > 220 and
            volume > 900 and
            score_agressao > 8 and
            intensidade_fluxo > 800
        ):
            return True, "BUY EXPLOSION"

        if (
            saldo_agressor < -400 and
            delta < -220 and
            volume > 900 and
            score_agressao < -8 and
            intensidade_fluxo > 800
        ):
            return True, "SELL EXPLOSION"

        return False, "SEM EXPLOSÃO"