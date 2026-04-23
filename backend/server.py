from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import random

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

historico = [100]

def gerar_preco():
    ultimo = historico[-1]
    variacao = random.uniform(-1.5, 1.5)
    novo = ultimo + variacao
    historico.append(novo)

    if len(historico) > 50:
        historico.pop(0)

    return historico

def calcular_score(dados):
    if len(dados) < 2:
        return 0

    diferenca = dados[-1] - dados[0]
    score = int(abs(diferenca) * 2)
    score = min(score, 10)

    return score

def calcular_direcao(dados):
    if dados[-1] > dados[0]:
        return "COMPRA"
    elif dados[-1] < dados[0]:
        return "VENDA"
    else:
        return "NEUTRO"

def calcular_fase(dados):
    variacoes = [dados[i] - dados[i-1] for i in range(1, len(dados))]

    positivos = sum(1 for v in variacoes if v > 0)
    negativos = sum(1 for v in variacoes if v < 0)

    if positivos > negativos * 1.5:
        return "EXPANSAO"
    elif negativos > positivos * 1.5:
        return "DISTRIBUICAO"
    else:
        return "ACUMULACAO"

@app.get("/")
def home():
    return {"status": "online"}

@app.get("/data")
def get_data():
    dados = gerar_preco()

    score = calcular_score(dados)
    direcao = calcular_direcao(dados)
    fase = calcular_fase(dados)

    return {
        "score": score,
        "direcao": direcao,
        "fase": fase,
        "historico": dados
    }