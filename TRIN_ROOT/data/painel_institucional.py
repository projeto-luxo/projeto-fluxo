import tkinter as tk
import random

janela = tk.Tk()
janela.title("FLOW INSTITUCIONAL PRO")
janela.geometry("1400x750")
janela.configure(bg="#070707")

# =========================
# UI
# =========================
top = tk.Frame(janela, bg="#050505")
top.pack(fill="x")

titulo = tk.Label(top, text="FLOW INSTITUCIONAL PRO",
                  fg="#00e5ff", bg="#050505",
                  font=("Segoe UI", 16, "bold"))
titulo.pack()

main = tk.Frame(janela, bg="#070707")
main.pack(fill="both", expand=True)

left = tk.Frame(main, bg="#0d0d0d", width=180)
left.pack(side="left", fill="y")

score_label = tk.Label(left, text="0", font=("Segoe UI", 40), bg="#0d0d0d")
score_label.pack(pady=10)

status = tk.Label(left, text="EVITAR", bg="#0d0d0d")
status.pack()

trade_label = tk.Label(left, text="SEM POSIÇÃO", bg="#0d0d0d")
trade_label.pack(pady=10)

# BACKTEST INFO
stats_label = tk.Label(left, text="", fg="#00e5ff", bg="#0d0d0d", justify="left")
stats_label.pack(pady=20)

center = tk.Frame(main, bg="#070707")
center.pack(side="left", fill="both", expand=True)

canvas = tk.Canvas(center, bg="#000000")
canvas.pack(side="left", fill="both", expand=True)

profile_canvas = tk.Canvas(center, bg="#050505", width=150)
profile_canvas.pack(side="right", fill="y")

# =========================
# DADOS
# =========================
candles = []
historico_delta = []

posicao = None
preco_entrada = 0

# BACKTEST
trades = 0
wins = 0
losses = 0
resultado = 0

# =========================
def detectar_zona(delta):
    historico_delta.append(delta)
    if len(historico_delta) > 10:
        historico_delta.pop(0)

    soma = sum(historico_delta)

    if soma > 800:
        return "ACUMULACAO"
    elif soma < -800:
        return "DISTRIBUICAO"

    if abs(delta) < 40:
        return "EXAUSTAO"

    return "NEUTRO"

# =========================
def calcular_score(delta, zona):
    score = 0

    if zona in ["ACUMULACAO", "DISTRIBUICAO"]:
        score += 4

    if zona == "EXAUSTAO":
        score += 2

    if abs(delta) > 200:
        score += 4

    return min(score, 10)

# =========================
def gerar_candle():
    base = candles[-1]["close"] if candles else 150

    open_ = base
    close = open_ + random.randint(-6, 6)

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
def detectar_trap(c, prev):
    if not prev:
        return None

    if c["high"] > prev["high"] and c["close"] < prev["high"]:
        return "VENDA"

    if c["low"] < prev["low"] and c["close"] > prev["low"]:
        return "COMPRA"

    return None

# =========================
def entrada(c, prev, score):
    global posicao, preco_entrada, trades

    if posicao:
        return

    trap = detectar_trap(c, prev)

    if trap == "COMPRA" and score >= 5 and c["close"] > c["open"]:
        posicao = "COMPRA"
        preco_entrada = c["close"]
        trades += 1

    elif trap == "VENDA" and score >= 5 and c["close"] < c["open"]:
        posicao = "VENDA"
        preco_entrada = c["close"]
        trades += 1

# =========================
def saida(c):
    global posicao, preco_entrada, wins, losses, resultado

    if not posicao:
        return

    alvo = 5
    stop = 5

    if posicao == "COMPRA":
        if c["close"] >= preco_entrada + alvo:
            wins += 1
            resultado += alvo
            posicao = None

        elif c["close"] <= preco_entrada - stop:
            losses += 1
            resultado -= stop
            posicao = None

    elif posicao == "VENDA":
        if c["close"] <= preco_entrada - alvo:
            wins += 1
            resultado += alvo
            posicao = None

        elif c["close"] >= preco_entrada + stop:
            losses += 1
            resultado -= stop
            posicao = None

# =========================
def desenhar():
    canvas.delete("all")

    if len(candles) < 2:
        return

    w = canvas.winfo_width()
    h = canvas.winfo_height()

    precos = [c["high"] for c in candles] + [c["low"] for c in candles]
    max_p = max(precos)
    min_p = min(precos)

    escala = h / (max_p - min_p + 1)
    largura = w / len(candles)

    for i, c in enumerate(candles):
        x = i * largura

        open_y = h - (c["open"] - min_p) * escala
        close_y = h - (c["close"] - min_p) * escala
        high_y = h - (c["high"] - min_p) * escala
        low_y = h - (c["low"] - min_p) * escala

        cor = "#00ff00" if c["close"] > c["open"] else "#ff0000"

        canvas.create_line(x+largura/2, high_y, x+largura/2, low_y, fill="#aaa")
        canvas.create_rectangle(x+largura*0.2, open_y, x+largura*0.8, close_y, fill=cor)

# =========================
def atualizar():
    global wins, losses, trades

    c = gerar_candle()
    candles.append(c)

    if len(candles) > 100:
        candles.pop(0)

    zona = detectar_zona(c["delta"])
    score = calcular_score(c["delta"], zona)

    prev = candles[-2] if len(candles) > 1 else None

    entrada(c, prev, score)
    saida(c)

    # UI
    score_label.config(text=str(score))

    if score >= 8:
        status.config(text="ENTRADA", fg="#00ff00")
    elif score >= 5:
        status.config(text="OBSERVAR", fg="#ffaa00")
    else:
        status.config(text="EVITAR", fg="#ff4444")

    if posicao:
        trade_label.config(text=f"{posicao} ATIVO", fg="#00e5ff")
    else:
        trade_label.config(text="SEM POSIÇÃO", fg="#888")

    # BACKTEST
    winrate = (wins / trades * 100) if trades > 0 else 0

    stats_label.config(
        text=f"Trades: {trades}\nWins: {wins}\nLoss: {losses}\nWinrate: {winrate:.1f}%\nPnL: {resultado}"
    )

    desenhar()

    janela.after(200, atualizar)

atualizar()
janela.mainloop()