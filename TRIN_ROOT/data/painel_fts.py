import tkinter as tk
import random

# =========================
# JANELA
# =========================
janela = tk.Tk()
janela.title("FLOW INSTITUCIONAL PRO")
janela.geometry("1200x700")
janela.configure(bg="#070707")

tk.Label(
    janela,
    text="FLOW INSTITUCIONAL",
    fg="#00e5ff",
    bg="#050505",
    font=("Segoe UI", 18, "bold")
).pack(fill="x")

main = tk.Frame(janela, bg="#070707")
main.pack(fill="both", expand=True)

# =========================
# ESQUERDA (SCORE)
# =========================
left = tk.Frame(main, bg="#0d0d0d", width=80)
left.pack(side="left", fill="y")

score_label = tk.Label(left, text="0", font=("Segoe UI", 40), bg="#0d0d0d")
score_label.pack(pady=20)

status = tk.Label(left, text="EVITAR", bg="#0d0d0d")
status.pack()

# =========================
# DIREITA
# =========================
right = tk.Frame(main, bg="#070707")
right.pack(side="left", fill="both", expand=True)

canvas = tk.Canvas(right, bg="#000000")
canvas.pack(fill="both", expand=True)

# =========================
# DADOS
# =========================
precos = [150]
deltas = [0]
entradas = []

# =========================
# FUNÇÃO ZONAS
# =========================
def detectar_zona(delta):
    if delta > 200:
        return "COMPRA FORTE"
    elif delta < -200:
        return "VENDA FORTE"
    elif abs(delta) < 50:
        return "EXAUSTAO"
    return "NORMAL"

# =========================
# DESENHO
# =========================
def desenhar():
    canvas.delete("all")

    w = canvas.winfo_width()
    h = canvas.winfo_height()

    if len(precos) < 2:
        return

    max_p = max(precos)
    min_p = min(precos)
    escala = h / (max_p - min_p + 1)

    largura_barra = w / len(precos)

    for i in range(len(precos)):
        x = i * largura_barra

        # =====================
        # ZONA DE FUNDO
        # =====================
        zona = detectar_zona(deltas[i])

        if zona == "COMPRA FORTE":
            canvas.create_rectangle(x, 0, x+largura_barra, h,
                                    fill="#002200", outline="")
        elif zona == "VENDA FORTE":
            canvas.create_rectangle(x, 0, x+largura_barra, h,
                                    fill="#220000", outline="")
        elif zona == "EXAUSTAO":
            canvas.create_rectangle(x, 0, x+largura_barra, h,
                                    fill="#222200", outline="")

        # =====================
        # DELTA (BARRA)
        # =====================
        delta = deltas[i]
        altura_delta = abs(delta) * 0.2

        if delta > 0:
            canvas.create_rectangle(
                x, h, x+largura_barra/2, h-altura_delta,
                fill="#00ff00", outline=""
            )
        else:
            canvas.create_rectangle(
                x, h, x+largura_barra/2, h-altura_delta,
                fill="#ff0000", outline=""
            )

    # =====================
    # LINHA DE PREÇO
    # =====================
    for i in range(len(precos)-1):
        x1 = i * largura_barra
        x2 = (i+1) * largura_barra

        y1 = h - (precos[i] - min_p) * escala
        y2 = h - (precos[i+1] - min_p) * escala

        canvas.create_line(x1, y1, x2, y2,
                           fill="#00e5ff", width=2)

    # =====================
    # ENTRADAS
    # =====================
    for e in entradas:
        x = e["x"]
        y = e["y"]

        cor = "#00ff00" if e["tipo"] == "COMPRA" else "#ff0000"

        canvas.create_text(x, y, text="▲", fill=cor, font=("Arial", 12))

# =========================
# LOOP
# =========================
def atualizar():
    # PREÇO
    novo_preco = precos[-1] + random.randint(-5, 5)
    precos.append(novo_preco)

    # DELTA
    delta = random.randint(-300, 300)
    deltas.append(delta)

    # LIMITA TAMANHO
    if len(precos) > 60:
        precos.pop(0)
        deltas.pop(0)

    # SCORE SIMPLES
    score = 0
    if abs(delta) > 200:
        score = 8
    elif abs(delta) > 100:
        score = 5

    # DECISÃO
    if score >= 8:
        status_text = "ENTRADA"
        cor = "#00ff00"

        entradas.append({
            "x": len(precos) * 15,
            "y": 100,
            "tipo": "COMPRA" if delta > 0 else "VENDA"
        })

    elif score >= 5:
        status_text = "OBSERVAR"
        cor = "#ffaa00"
    else:
        status_text = "EVITAR"
        cor = "#ff4444"

    score_label.config(text=str(score), fg=cor)
    status.config(text=status_text, fg=cor)

    desenhar()

    janela.after(800, atualizar)

# START
atualizar()
janela.mainloop()