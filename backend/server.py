from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import random
from datetime import datetime

app = FastAPI(title="TRIN Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

historico = [100.0]


def gerar_preco():
    ultimo = historico[-1]
    variacao = random.uniform(-1.5, 1.5)
    novo = round(ultimo + variacao, 2)

    historico.append(novo)

    if len(historico) > 50:
        historico.pop(0)

    return historico


def calcular_score(dados):
    if len(dados) < 2:
        return 0

    diferenca = dados[-1] - dados[0]
    score = int(abs(diferenca) * 2)
    return min(score, 10)


def calcular_direcao(dados):
    if dados[-1] > dados[0]:
        return "COMPRA"
    elif dados[-1] < dados[0]:
        return "VENDA"
    return "NEUTRO"


def calcular_fase(dados):
    if len(dados) < 3:
        return "AGUARDANDO"

    variacoes = [dados[i] - dados[i - 1] for i in range(1, len(dados))]

    positivos = sum(1 for v in variacoes if v > 0)
    negativos = sum(1 for v in variacoes if v < 0)

    if positivos > negativos * 1.5:
        return "EXPANSAO"
    elif negativos > positivos * 1.5:
        return "DISTRIBUICAO"
    return "ACUMULACAO"


def gerar_sinal(score, direcao, fase):
    if score >= 7 and direcao == "COMPRA" and fase == "EXPANSAO":
        return "COMPRA FORTE"

    if score >= 7 and direcao == "VENDA" and fase == "DISTRIBUICAO":
        return "VENDA FORTE"

    if score >= 4:
        return "ATENCAO"

    return "SEM ENTRADA"


def calcular_cor(sinal):
    if sinal == "COMPRA FORTE":
        return "verde"

    if sinal == "VENDA FORTE":
        return "vermelho"

    if sinal == "ATENCAO":
        return "amarelo"

    return "cinza"


@app.get("/")
def home():
    return {
        "status": "online",
        "sistema": "TRIN",
        "mensagem": "Backend rodando com sucesso"
    }

@app.get("/data")
def get_data():
    dados = gerar_preco()

    score = calcular_score(dados)
    direcao = calcular_direcao(dados)
    fase = calcular_fase(dados)
    sinal = gerar_sinal(score, direcao, fase)
    cor = calcular_cor(sinal)

    # 🔥 NOVO: PRESSÃO DE MERCADO
    pressao_compra = random.randint(0, 100)
    pressao_venda = 100 - pressao_compra

    return {
        "sistema": "TRIN FLOW",
        "timestamp": datetime.now().strftime("%H:%M:%S"),
        "preco_atual": dados[-1],
        "score": score,
        "direcao": direcao,
        "fase": fase,
        "sinal": sinal,
        "cor": cor,
        "pressao_compra": pressao_compra,
        "pressao_venda": pressao_venda,
        "historico": dados
    }
