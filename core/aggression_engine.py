# core/aggression_engine.py

class AggressionEngine:
    def __init__(self):
        self.fluxo_recente = []
        self.memoria_agressao = []

    def calcular_frequencia(self, saldo_agressor, delta, volume):
        intensidade = abs(saldo_agressor) + abs(delta) + (volume / 2)

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

        saldo_total = sum(item["saldo"] for item in self.memoria_agressao)
        delta_total = sum(item["delta"] for item in self.memoria_agressao)
        volume_total = sum(item["volume"] for item in self.memoria_agressao)

        persistencia_compra = round(
            (compras / len(self.memoria_agressao)) * 100,
            2
        )

        persistencia_venda = round(
            (vendas / len(self.memoria_agressao)) * 100,
            2
        )

        score_agressao = round(
            (saldo_total / 100) +
            (delta_total / 50) +
            (volume_total / 1000),
            2
        )

        if persistencia_compra >= 60 and score_agressao > 10:
            leitura = "PERSISTÊNCIA COMPRADORA"

        elif persistencia_venda >= 60 and score_agressao < -10:
            leitura = "PERSISTÊNCIA VENDEDORA"

        elif abs(score_agressao) < 8:
            leitura = "AGRESSÃO NEUTRA"

        else:
            leitura = "AGRESSÃO INSTÁVEL"

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
            score_agressao > 10 and
            intensidade_fluxo > 800
        ):
            return True, "BUY EXPLOSION"

        if (
            saldo_agressor < -400 and
            delta < -220 and
            volume > 900 and
            score_agressao < -10 and
            intensidade_fluxo > 800
        ):
            return True, "SELL EXPLOSION"

        return False, "SEM EXPLOSÃO"