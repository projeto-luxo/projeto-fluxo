# core/aggression_engine.py


class AggressionEngine:
    """Interpreta intensidade, persistencia e explosao do fluxo agressor.

    CR-03D2:
    - preserva o comportamento legado quando Delta e Saldo sao independentes;
    - usa uma unica evidencia canonica quando os campos sao equivalentes,
      derivados ou semanticamente nao independentes;
    - nao recalibra limites, pesos de volume ou classificacoes.
    """

    RELACOES_NAO_INDEPENDENTES = {
        "EQUIVALENTES_OBSERVADOS",
        "SALDO_DERIVADO_DELTA",
        "DELTA_DERIVADO_SALDO",
        "SEM_DADOS",
    }

    def __init__(self):
        self.fluxo_recente = []
        self.memoria_agressao = []

    @staticmethod
    def _numero(valor, default=0.0):
        try:
            if valor is None:
                return default

            texto = str(valor).strip()
            if texto == "" or texto.lower() in {"none", "nan", "n/d"}:
                return default

            if "," in texto and "." in texto:
                texto = texto.replace(".", "").replace(",", ".")
            elif "," in texto:
                texto = texto.replace(",", ".")

            return float(texto)
        except Exception:
            return default

    @staticmethod
    def _booleano(valor, default=True):
        if isinstance(valor, bool):
            return valor

        if valor is None:
            return default

        texto = str(valor).strip().lower()
        if texto in {"true", "1", "sim", "yes", "verdadeiro"}:
            return True
        if texto in {"false", "0", "nao", "não", "no", "falso"}:
            return False

        return default

    def _resolver_contexto_fluxo(
        self,
        saldo_agressor,
        delta,
        fluxo_agressor_canonico=None,
        delta_saldo_independentes=True,
        delta_saldo_relacao="INDETERMINADO",
    ):
        saldo = self._numero(saldo_agressor, 0.0)
        delta_num = self._numero(delta, 0.0)
        relacao = str(delta_saldo_relacao or "INDETERMINADO").strip().upper()

        independentes = self._booleano(
            delta_saldo_independentes,
            default=True,
        )

        if relacao == "INDEPENDENTES":
            independentes = True
        elif relacao in self.RELACOES_NAO_INDEPENDENTES:
            independentes = False

        if fluxo_agressor_canonico is None:
            if relacao == "SEM_DADOS":
                fluxo_canonico = 0.0
            elif saldo_agressor is not None:
                fluxo_canonico = saldo
            else:
                fluxo_canonico = delta_num
        else:
            fluxo_canonico = self._numero(fluxo_agressor_canonico, 0.0)

        return {
            "saldo": saldo,
            "delta": delta_num,
            "fluxo_canonico": fluxo_canonico,
            "relacao": relacao,
            "independentes": independentes,
            "modo_evidencia": (
                "DUPLA_INDEPENDENTE"
                if independentes
                else "CANONICA_UNICA"
            ),
        }

    @staticmethod
    def _direcao_fluxo_contexto(contexto):
        if contexto["independentes"]:
            saldo = contexto["saldo"]
            delta = contexto["delta"]

            if saldo > 0 and delta > 0:
                return 1
            if saldo < 0 and delta < 0:
                return -1
            if delta > 0:
                return 0.5
            if delta < 0:
                return -0.5
            return 0

        fluxo = contexto["fluxo_canonico"]
        if fluxo > 0:
            return 1
        if fluxo < 0:
            return -1
        return 0

    def calcular_frequencia(
        self,
        saldo_agressor,
        delta,
        volume,
        fluxo_agressor_canonico=None,
        delta_saldo_independentes=True,
        delta_saldo_relacao="INDETERMINADO",
    ):
        contexto = self._resolver_contexto_fluxo(
            saldo_agressor=saldo_agressor,
            delta=delta,
            fluxo_agressor_canonico=fluxo_agressor_canonico,
            delta_saldo_independentes=delta_saldo_independentes,
            delta_saldo_relacao=delta_saldo_relacao,
        )
        volume_num = self._numero(volume, 0.0)

        if contexto["independentes"]:
            componente_fluxo = (
                abs(contexto["saldo"]) / 1000
                + abs(contexto["delta"]) / 1000
            )
        else:
            componente_fluxo = abs(contexto["fluxo_canonico"]) / 1000

        intensidade = componente_fluxo + (volume_num / 100)

        self.fluxo_recente.append(intensidade)

        if len(self.fluxo_recente) > 30:
            self.fluxo_recente = self.fluxo_recente[-30:]

        media = sum(self.fluxo_recente) / len(self.fluxo_recente)

        if media > 1300:
            return "FREQUÊNCIA ALTA", "MERCADO ACELERADO", round(media, 2)

        if media > 800:
            return "FREQUÊNCIA MÉDIA", "MERCADO ATIVO", round(media, 2)

        return "FREQUÊNCIA BAIXA", "MERCADO LENTO", round(media, 2)

    def calcular_memoria_agressao(
        self,
        saldo_agressor,
        delta,
        volume,
        fluxo_agressor_canonico=None,
        delta_saldo_independentes=True,
        delta_saldo_relacao="INDETERMINADO",
    ):
        contexto = self._resolver_contexto_fluxo(
            saldo_agressor=saldo_agressor,
            delta=delta,
            fluxo_agressor_canonico=fluxo_agressor_canonico,
            delta_saldo_independentes=delta_saldo_independentes,
            delta_saldo_relacao=delta_saldo_relacao,
        )
        volume_num = self._numero(volume, 0.0)

        self.memoria_agressao.append({
            "saldo": contexto["saldo"],
            "delta": contexto["delta"],
            "volume": volume_num,
            "fluxo_canonico": contexto["fluxo_canonico"],
            "delta_saldo_relacao": contexto["relacao"],
            "delta_saldo_independentes": contexto["independentes"],
            "modo_evidencia": contexto["modo_evidencia"],
        })

        if len(self.memoria_agressao) > 20:
            self.memoria_agressao = self.memoria_agressao[-20:]

        compras = sum(
            1
            for item in self.memoria_agressao
            if self._direcao_fluxo_contexto({
                "saldo": item["saldo"],
                "delta": item["delta"],
                "fluxo_canonico": item["fluxo_canonico"],
                "independentes": item["delta_saldo_independentes"],
            }) == 1
        )

        vendas = sum(
            1
            for item in self.memoria_agressao
            if self._direcao_fluxo_contexto({
                "saldo": item["saldo"],
                "delta": item["delta"],
                "fluxo_canonico": item["fluxo_canonico"],
                "independentes": item["delta_saldo_independentes"],
            }) == -1
        )

        ultimo = self.memoria_agressao[-1]
        contexto_ultimo = {
            "saldo": ultimo["saldo"],
            "delta": ultimo["delta"],
            "fluxo_canonico": ultimo["fluxo_canonico"],
            "independentes": ultimo["delta_saldo_independentes"],
        }

        persistencia_compra = round(
            (compras / len(self.memoria_agressao)) * 100,
            2,
        )
        persistencia_venda = round(
            (vendas / len(self.memoria_agressao)) * 100,
            2,
        )

        direcao_fluxo = self._direcao_fluxo_contexto(contexto_ultimo)

        if ultimo["delta_saldo_independentes"]:
            score_base = (
                (ultimo["saldo"] / 10000)
                + (ultimo["delta"] / 10000)
            )
        else:
            score_base = ultimo["fluxo_canonico"] / 10000

        peso_volume = min(ultimo["volume"] / 800, 2)
        score_agressao = round(score_base * peso_volume, 2)

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
            "score_base_agressao": round(score_base, 6),
            "fluxo_agressor_utilizado": ultimo["fluxo_canonico"],
            "modo_evidencia_agressao": ultimo["modo_evidencia"],
            "delta_saldo_relacao": ultimo["delta_saldo_relacao"],
            "delta_saldo_independentes": ultimo["delta_saldo_independentes"],
        }

    def detectar_explosao_fluxo(
        self,
        saldo_agressor,
        delta,
        volume,
        score_agressao,
        intensidade_fluxo,
        fluxo_agressor_canonico=None,
        delta_saldo_independentes=True,
        delta_saldo_relacao="INDETERMINADO",
    ):
        contexto = self._resolver_contexto_fluxo(
            saldo_agressor=saldo_agressor,
            delta=delta,
            fluxo_agressor_canonico=fluxo_agressor_canonico,
            delta_saldo_independentes=delta_saldo_independentes,
            delta_saldo_relacao=delta_saldo_relacao,
        )

        volume_num = self._numero(volume, 0.0)
        score_num = self._numero(score_agressao, 0.0)
        intensidade_num = self._numero(intensidade_fluxo, 0.0)

        if contexto["independentes"]:
            compra_confirmada = (
                contexto["saldo"] > 400
                and contexto["delta"] > 220
            )
            venda_confirmada = (
                contexto["saldo"] < -400
                and contexto["delta"] < -220
            )
        else:
            # Mantem o limite efetivo mais restritivo do contrato legado
            # (saldo > 400) sem transformar a mesma evidencia em duas provas.
            compra_confirmada = contexto["fluxo_canonico"] > 400
            venda_confirmada = contexto["fluxo_canonico"] < -400

        if (
            compra_confirmada
            and volume_num > 900
            and score_num > 8
            and intensidade_num > 800
        ):
            return True, "BUY EXPLOSION"

        if (
            venda_confirmada
            and volume_num > 900
            and score_num < -8
            and intensidade_num > 800
        ):
            return True, "SELL EXPLOSION"

        return False, "SEM EXPLOSÃO"
