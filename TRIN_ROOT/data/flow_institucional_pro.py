# ============================================
# ENGINE INSTITUCIONAL PRO (LÓGICA LIMPA)
# ============================================

class Engine:

    def __init__(self):
        self.zona = None
        self.zona_tempo = 0

        self.trap = None
        self.trap_tempo = 0

        self.seq_delta = 0

        self.score = 0
        self.direcao = "NEUTRO"
        self.fase = "AGUARDANDO"

    def detectar_absorcao(self, c):
        corpo = abs(c["close"] - c["open"])
        range_total = c["high"] - c["low"]

        if range_total == 0:
            return False

        return abs(c["delta"]) > 200 and corpo < range_total * 0.3

    def detectar_trap(self, atual, anterior):
        if atual["high"] > anterior["high"] and atual["close"] < anterior["high"]:
            if atual["delta"] < -120:
                return "VENDA"

        if atual["low"] < anterior["low"] and atual["close"] > anterior["low"]:
            if atual["delta"] > 120:
                return "COMPRA"

        return None

    def atualizar_fluxo(self, c):
        if c["delta"] > 120:
            self.seq_delta += 1
        elif c["delta"] < -120:
            self.seq_delta -= 1
        else:
            self.seq_delta = 0

    def atualizar_zona(self, c, absorcao):
        if absorcao:
            self.zona = (c["low"], c["high"])
            self.zona_tempo = 0

        if self.zona:
            self.zona_tempo += 1

            if self.zona_tempo > 25:
                self.zona = None
            else:
                z_low, z_high = self.zona

                if c["close"] > z_high + 10 or c["close"] < z_low - 10:
                    self.zona = None

    def atualizar_trap(self, trap, candle):
        if trap:
            self.trap = (trap, candle)
            self.trap_tempo = 0

        if self.trap:
            self.trap_tempo += 1
            if self.trap_tempo > 10:
                self.trap = None

    def atualizar_fase(self):
        if self.seq_delta >= 3:
            self.fase = "ROMPIMENTO"
            self.direcao = "COMPRA"
            return

        if self.seq_delta <= -3:
            self.fase = "ROMPIMENTO"
            self.direcao = "VENDA"
            return

        if self.zona:
            self.fase = "ACUMULACAO"
        else:
            self.fase = "DISTRIBUICAO"

        self.direcao = "NEUTRO"

    def atualizar_score(self):
        score = 0

        if self.zona:
            score += 2

        if self.trap:
            tipo, _ = self.trap

            if (tipo == "COMPRA" and self.seq_delta > 0) or \
               (tipo == "VENDA" and self.seq_delta < 0):
                score += 4

        if abs(self.seq_delta) >= 2:
            score += 3

        self.score = score

    def processar(self, atual, anterior):
        absorcao = self.detectar_absorcao(atual)
        trap = self.detectar_trap(atual, anterior)

        self.atualizar_fluxo(atual)
        self.atualizar_zona(atual, absorcao)
        self.atualizar_trap(trap, atual)

        self.atualizar_fase()
        self.atualizar_score()