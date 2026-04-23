print(">>>>>>>>>> ESTE É O PAINEL NOVO <<<<<<<<<<")

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import tkinter as tk
from core.engine import Engine
from data.market import gerar_candle

# =========================
# 🎨 TEMA (BASE PRO)
# =========================
COLORS = {
    "bg": "#000000",
    "panel": "#050505",
    "accent": "#00ffcc",
    "buy": "#00ff99",
    "sell": "#ff4444",
    "warn": "#ffaa00",
    "text": "#aaaaaa",
    "soft": "#111111"
}

# =========================
# INIT
# =========================
root = tk.Tk()
root.title("TRIN FLOW PRO")
root.geometry("1400x800")
root.configure(bg=COLORS["bg"])

engine = Engine()
candles = []
preco = 100
ultimo_sinal = None

# =========================
# MAIN CONTAINER
# =========================
main = tk.Frame(root, bg=COLORS["bg"])
main.pack(fill="both", expand=True)

# =========================
# SIDEBAR (CANVAS PRO)
# =========================
sidebar = tk.Canvas(main, width=240, bg=COLORS["panel"], highlightthickness=0)
sidebar.pack(side="left", fill="y")

# =========================
# AREA DIREITA
# =========================
right = tk.Frame(main, bg=COLORS["bg"])
right.pack(side="left", fill="both", expand=True)

topbar = tk.Frame(right, bg=COLORS["bg"])
topbar.pack(fill="x")

info_lbl = tk.Label(topbar,
                    text="SCALPER | ---   SNIPER | ---",
                    fg=COLORS["accent"],
                    bg=COLORS["bg"])
info_lbl.pack(anchor="w", padx=10, pady=5)

# =========================
# HISTÓRICO
# =========================
history = tk.Listbox(right,
                     bg="#000",
                     fg=COLORS["accent"],
                     height=6,
                     border=0,
                     highlightthickness=0)
history.pack(fill="x")

# =========================
# CANVAS PRINCIPAL (GRAFICO)
# =========================
canvas = tk.Canvas(right, bg="#000", highlightthickness=0)
canvas.pack(fill="both", expand=True)

# =========================
# ✨ DRAW SIDEBAR (HUD PRO)
# =========================
def draw_sidebar():
    sidebar.delete("all")

    w = sidebar.winfo_width()

    # SCORE GRANDE
    sidebar.create_text(
        w/2, 80,
        text=str(engine.score),
        fill=COLORS["accent"],
        font=("Segoe UI", 52, "bold")
    )

    # FASE
    sidebar.create_text(
        w/2, 140,
        text=engine.fase,
        fill=COLORS["warn"],
        font=("Segoe UI", 10)
    )

    # DIREÇÃO
    cor = COLORS["text"]
    if engine.direcao == "COMPRA":
        cor = COLORS["buy"]
    elif engine.direcao == "VENDA":
        cor = COLORS["sell"]

    sidebar.create_text(
        w/2, 170,
        text=engine.direcao,
        fill=cor,
        font=("Segoe UI", 11, "bold")
    )

    # CAIXA DE STATUS
    if engine.score >= 7 and engine.direcao != "NEUTRO":
        texto = f"🔥 {engine.direcao}"
        cor = COLORS["buy"] if engine.direcao == "COMPRA" else COLORS["sell"]

    elif engine.score >= 5:
        texto = "⚠ OBSERVAR"
        cor = COLORS["warn"]
    else:
        texto = "⛔ EVITAR"
        cor = COLORS["text"]

    sidebar.create_rectangle(30, 210, w-30, 260,
                             fill=COLORS["soft"],
                             outline=cor)

    sidebar.create_text(
        w/2, 235,
        text=texto,
        fill=cor,
        font=("Segoe UI", 11, "bold")
    )

# =========================
# 📊 GRAFICO
# =========================
def draw_chart():
    canvas.delete("all")

    if len(candles) < 2:
        return

    w = canvas.winfo_width()
    h = canvas.winfo_height()

    precos = [c["high"] for c in candles] + [c["low"] for c in candles]

    max_p = max(precos)
    min_p = min(precos)

    if max_p == min_p:
        return

    escala = h / (max_p - min_p)
    largura = w / len(candles)

    # ZONA
    if engine.zona:
        try:
            z_low, z_high = engine.zona
            y1 = h - (z_high - min_p) * escala
            y2 = h - (z_low - min_p) * escala

            canvas.create_rectangle(
                0, y1, w, y2,
                fill="#003333",
                outline=""
            )
        except:
            pass

    # CANDLES
    for i, c in enumerate(candles):
        x = i * largura

        open_y = h - (c["open"] - min_p) * escala
        close_y = h - (c["close"] - min_p) * escala
        high_y = h - (c["high"] - min_p) * escala
        low_y = h - (c["low"] - min_p) * escala

        cor = COLORS["buy"] if c["close"] > c["open"] else COLORS["sell"]

        canvas.create_line(x + largura/2, high_y,
                           x + largura/2, low_y,
                           fill="#777")

        canvas.create_rectangle(
            x + largura*0.2, open_y,
            x + largura*0.8, close_y,
            fill=cor,
            outline=""
        )

# =========================
# 🔁 LOOP
# =========================
def update():
    global preco, ultimo_sinal

    c = gerar_candle(preco)
    preco = c["close"]

    candles.append(c)
    if len(candles) > 120:
        candles.pop(0)

    if len(candles) > 1:
        engine.processar(c, candles[-2])

        # TOP INFO
        info_lbl.config(
            text=f"SCALPER | F{engine.score % 4}    SNIPER | F{(engine.score+1)%4}"
        )

        # HISTÓRICO
        if engine.score >= 7 and engine.direcao != "NEUTRO":
            sinal = f"{engine.direcao}_{engine.score}"

            if sinal != ultimo_sinal:
                history.insert(0, f"{engine.direcao} | SCORE {engine.score}")
                ultimo_sinal = sinal

                if history.size() > 10:
                    history.delete(10, tk.END)

    draw_sidebar()
    draw_chart()

    root.after(200, update)

# =========================
# START
# =========================
update()
root.mainloop()