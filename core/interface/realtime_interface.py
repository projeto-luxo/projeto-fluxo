import tkinter as tk
import random
import threading
import time
import winsound

# =========================
# ALERTA SONORO
# =========================
def tocar_alerta(tipo):
    try:
        if tipo == "COMPRA":
            winsound.Beep(1000, 200)
        elif tipo == "VENDA":
            winsound.Beep(600, 200)
    except:
        pass


# =========================
# ENGINE
# =========================
class Engine:

    def __init__(self):
        self.zona = None
        self.seq_delta = 0
        self.score = 0
        self.direcao = "NEUTRO"
        self.fase = "AGUARDANDO"

    def processar(self, c):
        if c["delta"] > 100:
            self.seq_delta += 1
        elif c["delta"] < -100:
            self.seq_delta -= 1
        else:
            self.seq_delta = 0

        if self.seq_delta >= 3:
            self.direcao = "COMPRA"
        elif self.seq_delta <= -3:
            self.direcao = "VENDA"
        else:
            self.direcao = "NEUTRO"

        self.score = abs(self.seq_delta)


# =========================
# SIMULAÇÃO
# =========================
def gerar_candle(base):
    open_ = base
    close = open_ + random.randint(-5, 5)
    high = max(open_, close) + random.randint(0, 4)
    low = min(open_, close) - random.randint(0, 4)
    delta = random.randint(-300, 300)

    return {
        "open": open_,
        "close": close,
        "high": high,
        "low": low,
        "delta": delta
    }


# =========================
# APP
# =========================
class App:

    def __init__(self, root):
        self.root = root
        self.engine = Engine()

        self.candles = []
        self.preco = 100

        self.rodando = False
        self.modo = "SIMULACAO"

        self.build_ui()

    # =========================
    # UI
    # =========================
    def build_ui(self):
        self.root.title("FLOW INSTITUCIONAL PRO")
        self.root.geometry("1400x750")
        self.root.configure(bg="#000")

        # MAIN
        main = tk.Frame(self.root, bg="#000")
        main.pack(fill="both", expand=True)

        # SIDEBAR
        sidebar = tk.Frame(main, bg="#0d0d0d", width=220)
        sidebar.pack(side="left", fill="y")

        tk.Label(sidebar, text="FLOW PRO",
                 fg="#00ffff", bg="#0d0d0d",
                 font=("Arial", 14, "bold")).pack(pady=15)

        self.status = tk.Label(sidebar, text="DESCONECTADO",
                               fg="#ff4444", bg="#0d0d0d",
                               font=("Arial", 10))
        self.status.pack(pady=5)

        tk.Button(sidebar, text="▶ Simulação",
                  command=self.iniciar_simulacao,
                  width=18).pack(pady=5)

        tk.Button(sidebar, text="⚡ Tempo Real",
                  command=self.conectar_api,
                  width=18).pack(pady=5)

        # INFO BOX
        self.info = tk.Label(sidebar,
                             text="FASE: -\nDIREÇÃO: -\nSCORE: -",
                             fg="#00ffff",
                             bg="#0d0d0d",
                             justify="left")
        self.info.pack(pady=20)

        # CANVAS AREA
        right = tk.Frame(main, bg="#000")
        right.pack(side="left", fill="both", expand=True)

        # TOP BAR
        top = tk.Frame(right, bg="#111", height=40)
        top.pack(fill="x")

        self.top_label = tk.Label(top,
                                 text="Modo: OFF",
                                 fg="#00ffff",
                                 bg="#111")
        self.top_label.pack(side="left", padx=10)

        # CANVAS
        self.canvas = tk.Canvas(right, bg="#000")
        self.canvas.pack(fill="both", expand=True)

    # =========================
    # MODOS
    # =========================
    def iniciar_simulacao(self):
        self.modo = "SIMULACAO"
        self.status.config(text="SIMULAÇÃO", fg="#00ffff")
        self.top_label.config(text="Modo: SIMULAÇÃO")
        self.start_loop()

    def conectar_api(self):
        self.status.config(text="CONECTANDO...", fg="#ffaa00")

        def fake():
            time.sleep(2)
            self.modo = "REALTIME"
            self.status.config(text="CONECTADO", fg="#00ff00")
            self.top_label.config(text="Modo: TEMPO REAL")
            self.start_loop()

        threading.Thread(target=fake).start()

    # =========================
    # DADOS
    # =========================
    def gerar_dado(self):
        # 🔥 FUTURO: trocar por API real
        return gerar_candle(self.preco)

    def update_data(self):
        c = self.gerar_dado()
        self.preco = c["close"]

        self.candles.append(c)

        if len(self.candles) > 80:
            self.candles.pop(0)

        self.engine.processar(c)

    # =========================
    # DESENHO
    # =========================
    def desenhar(self):
        self.canvas.delete("all")

        if len(self.candles) < 2:
            return

        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()

        precos = [c["high"] for c in self.candles] + [c["low"] for c in self.candles]
        max_p = max(precos)
        min_p = min(precos)

        escala = h / (max_p - min_p + 1)
        largura = w / len(self.candles)

        for i, c in enumerate(self.candles):
            x = i * largura

            open_y = h - (c["open"] - min_p) * escala
            close_y = h - (c["close"] - min_p) * escala
            high_y = h - (c["high"] - min_p) * escala
            low_y = h - (c["low"] - min_p) * escala

            cor = "#00ff00" if c["close"] > c["open"] else "#ff0000"

            self.canvas.create_line(x+largura/2, high_y, x+largura/2, low_y, fill="#aaa")
            self.canvas.create_rectangle(
                x+largura*0.2, open_y,
                x+largura*0.8, close_y,
                fill=cor, outline=""
            )

        # INFO ATUALIZADA
        self.info.config(
            text=f"FASE: {self.engine.fase}\nDIREÇÃO: {self.engine.direcao}\nSCORE: {self.engine.score}"
        )

    # =========================
    # LOOP
    # =========================
    def loop(self):
        if not self.rodando:
            return

        self.update_data()
        self.desenhar()

        self.root.after(300, self.loop)

    def start_loop(self):
        if not self.rodando:
            self.rodando = True
            self.loop()


# =========================
# RUN
# =========================
root = tk.Tk()
app = App(root)
root.mainloop()