# core/engine.py

class Engine:
    def __init__(self):
        self.zona = None
        self.zona_tempo = 0

        self.trap = None
        self.trap_tempo = 0
        self.trap_detectado = None

        self.seq_delta = 0
        self.score = 0

        self.direcao = "NEUTRO"
        self.fase = "AGUARDANDO"

        self.absorcao = False
        self.tipo_absorcao = None

    def detectar_absorcao(self, c):
        delta = c.get("delta", 0) / 1000
        volume = c.get("volume", 0)

        abertura = c["open"]
        fechamento = c["close"]
        maxima = c["high"]
        minima = c["low"]

        corpo = abs(fechamento - abertura)
        range_total = maxima - minima

        if range_total <= 0:
            self.tipo_absorcao = None
            return False

        corpo_ratio = corpo / range_total
        pavio_superior = maxima - max(abertura, fechamento)
        pavio_inferior = min(abertura, fechamento) - minima

        if (
            delta < -150
            and volume > 700
            and corpo_ratio < 0.35
            and pavio_inferior > corpo
        ):
            self.tipo_absorcao = "COMPRA"
            return True

        if (
            delta > 150
            and volume > 700
            and corpo_ratio < 0.35
            and pavio_superior > corpo
        ):
            self.tipo_absorcao = "VENDA"
            return True

        if (
            abs(delta) > 220
            and volume > 850
            and corpo_ratio < 0.28
        ):
            self.tipo_absorcao = "NEUTRA"
            return True

        self.tipo_absorcao = None
        return False

    def detectar_trap(self, atual, anterior):
        if anterior is None:
            return None

        delta = atual.get("delta", 0) / 1000

        if (
            atual["high"] > anterior["high"]
            and atual["close"] < anterior["high"]
            and delta < -120
        ):
            return "VENDA"

        if (
            atual["low"] < anterior["low"]
            and atual["close"] > anterior["low"]
            and delta > 120
        ):
            return "COMPRA"

        return None

    def atualizar_fluxo(self, c):
        delta = c.get("delta", 0) / 1000

        if delta > 120:
            if self.seq_delta >= 0:
                self.seq_delta += 1
            else:
                self.seq_delta = 1

        elif delta < -120:
            if self.seq_delta <= 0:
                self.seq_delta -= 1
            else:
                self.seq_delta = -1

        else:
            if self.seq_delta > 0:
                self.seq_delta -= 1
            elif self.seq_delta < 0:
                self.seq_delta += 1

        if self.seq_delta > 10:
            self.seq_delta = 10

        if self.seq_delta < -10:
            self.seq_delta = -10

    def atualizar_zona(self, c, absorcao):
        if absorcao:
            self.zona = (c["low"], c["high"])
            self.zona_tempo = 0

        if self.zona:
            self.zona_tempo += 1

            z_low, z_high = self.zona

            if self.zona_tempo > 20:
                self.zona = None
                return

            if c["close"] > z_high + 10:
                self.zona = None
                return

            if c["close"] < z_low - 10:
                self.zona = None
                return

    def atualizar_trap(self, trap, candle):
        if trap:
            self.trap = (trap, candle)
            self.trap_tempo = 0

        if self.trap:
            self.trap_tempo += 1

            if self.trap_tempo > 4:
                self.trap = None

    def atualizar_fase(self, c):
        delta = c.get("delta", 0) / 1000
        volume = c.get("volume", 0)

        if abs(delta) > 280 and volume > 1000:
            self.fase = "EXAUSTAO"
            self.direcao = "NEUTRO"
            return

        if self.absorcao and self.zona:
            self.fase = "COMPRESSAO"
            self.direcao = "NEUTRO"
            return

        if self.seq_delta >= 2:
            self.fase = "ROMPIMENTO"
            self.direcao = "COMPRA"
            return

        if self.seq_delta <= -2:
            self.fase = "ROMPIMENTO"
            self.direcao = "VENDA"
            return

        if self.zona:
            if self.seq_delta > 0:
                self.fase = "ACUMULACAO"
                self.direcao = "COMPRA"
                return

            if self.seq_delta < 0:
                self.fase = "DISTRIBUICAO"
                self.direcao = "VENDA"
                return

            self.fase = "COMPRESSAO"
            self.direcao = "NEUTRO"
            return

        self.fase = "AGUARDANDO"
        self.direcao = "NEUTRO"

    def atualizar_score(self, c):
        score = 0

        delta = abs(c.get("delta", 0)) / 1000
        volume = c.get("volume", 0)

        if self.zona:
            score += 2

        if self.absorcao:
            score += 3

        if self.trap_detectado:
            score += 3

        if abs(self.seq_delta) >= 2:
            score += 2

        if abs(self.seq_delta) >= 4:
            score += 2

        if delta > 180:
            score += 2

        if volume > 850:
            score += 1

        self.score = min(score, 10)

    def processar(self, atual, anterior=None):
        self.absorcao = self.detectar_absorcao(atual)
        self.trap_detectado = self.detectar_trap(atual, anterior)

        self.atualizar_fluxo(atual)
        self.atualizar_zona(atual, self.absorcao)
        self.atualizar_trap(self.trap_detectado, atual)

        self.atualizar_fase(atual)
        self.atualizar_score(atual)

        return self.resultado()

    def resultado(self):
        zona_low = None
        zona_high = None

        if self.zona:
            zona_low, zona_high = self.zona

        trap_tipo = None

        if self.trap:
            trap_tipo, _ = self.trap

        return {
            "engine_score": self.score,
            "engine_direcao": self.direcao,
            "engine_fase": self.fase,
            "engine_absorcao": self.absorcao,
            "engine_trap": trap_tipo,
            "engine_seq_delta": self.seq_delta,
            "engine_zona_low": zona_low,
            "engine_zona_high": zona_high,
        }