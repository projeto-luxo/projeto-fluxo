# backend/server_institucional.py
# ============================================================
# TRIN BACKEND INSTITUCIONAL — RECUPERADO DO ZIP projeto_fluxo
# Versao: server_institucional v1.0
# Base operacional: backend/server.py do ZIP projeto_fluxo
# Integracao cognitiva: ConfluenceEngine v2.2 oficial
#
# Fluxo arquitetural:
# RTD/Excel -> leitor_institucional -> gerar_candle
# -> Engine/Aggression/VWAP/Candle
# -> ConfluenceEngine v2.2
#    -> HistoriadorAdapter
#    -> BernardoAdapter
#    -> FiscalAdapter
# -> FastAPI /data e WebSocket /ws
# -> Frontend React
#
# Regra TRIN:
# - Nao substitui operador.
# - Nao executa ordem.
# - Apenas adiciona camada cognitiva explicavel ao payload.
# ============================================================

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from pathlib import Path
import asyncio

# ------------------------------------------------------------
# Imports com fallback para compatibilidade entre:
# - projeto_fluxo antigo
# - TRIN_ROOT atual
# ------------------------------------------------------------
try:
    from backend.flow_data import gerar_sinal
except ModuleNotFoundError:
    try:
        from flow_data import gerar_sinal
    except ModuleNotFoundError:
        def gerar_sinal(saldo_agressor, volume, delta, preco):
            """Fallback minimo para o backend nao morrer caso flow_data.py ainda nao tenha sido migrado."""
            return {
                "forca": 0,
                "entrada": "AGUARDAR",
                "tendencia": "AGUARDANDO CONFIRMACAO",
                "absorcao": False,
                "zona_absorcao": None,
                "zona_quente_absorcao": False,
                "exaustao": False,
                "stop": None,
                "parcial": None,
                "alvo": None,
                "sinal": "SEM SINAL",
            }

try:
    from backend.leitor_institucional import ler_dados_institucionais
except ModuleNotFoundError:
    try:
        from data.leitor_institucional import ler_dados_institucionais
    except ModuleNotFoundError:
        def ler_dados_institucionais():
            raise RuntimeError("leitor_institucional nao encontrado em backend/ nem data/")

from core.engine import TRINEngine
from core.vwap_engine import VWAPEngine
from core.candle_engine import CandleEngine
from core.aggression_engine import AggressionEngine
from core.confluence_engine import ConfluenceEngineV2

try:
    from orchestration.contrato_ativo_resolver import ContratoAtivoResolver
    from orchestration.bastiao_contrato_ativo import BastiaoContratoAtivo
except ModuleNotFoundError:
    ContratoAtivoResolver = None
    BastiaoContratoAtivo = None

app = FastAPI(
    title="TRIN FLOW PRO INSTITUCIONAL",
    version="5.9.3 + Confluence v2.2"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

engine = TRINEngine()
vwap_engine = VWAPEngine()
candle_engine = CandleEngine()
aggression_engine = AggressionEngine()
motor_confluencia = ConfluenceEngineV2()

TRIN_ROOT_DIR = Path(__file__).resolve().parents[1]
CALENDARIO_CONTRATOS_B3 = TRIN_ROOT_DIR / "config" / "calendarios" / "calendario_contratos_b3.csv"

try:
    contrato_resolver = (
        ContratoAtivoResolver(CALENDARIO_CONTRATOS_B3)
        if ContratoAtivoResolver else None
    )
    bastiao_contrato = BastiaoContratoAtivo() if BastiaoContratoAtivo else None
except Exception as erro:
    print("[BASTIAO CONTRATO INIT ERRO]", erro)
    contrato_resolver = None
    bastiao_contrato = None

historico = []
preco_atual = 100.0

ultima_explosao_tipo = "SEM EXPLOSÃO"
ultima_explosao_tempo = 0


def _num(valor, default=0.0):
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



def _ativo_base_from_ativo(ativo):
    texto = str(ativo or "WIN").upper().strip()
    if len(texto) >= 3:
        return texto[:3]
    return "WIN"


def _contrato_rtd_from_ativo(ativo):
    texto = str(ativo or "").upper().strip()

    if not texto:
        return None

    if texto.endswith("_F_0"):
        return texto

    return f"{texto}_F_0"


def _validar_contrato_ativo(atual):
    """
    Valida contrato ativo como telemetria institucional.

    Nesta fase, NAO bloqueia o painel quando calendario oficial ainda estiver vazio.
    Bloqueio operacional so deve ser aplicado depois da homologacao B3/Bastiao.
    """
    contrato_excel_visual = atual.get("ativo", "WIN")
    contrato_excel_rtd = _contrato_rtd_from_ativo(contrato_excel_visual)
    contrato_backend_rtd = contrato_excel_rtd
    ativo_base = _ativo_base_from_ativo(contrato_excel_visual)

    base = {
        "ativo_base": ativo_base,
        "contrato_excel_visual": contrato_excel_visual,
        "contrato_excel_rtd": contrato_excel_rtd,
        "contrato_backend_rtd": contrato_backend_rtd,
        "contrato_esperado_rtd": None,
        "resolver_status": "NAO_EXECUTADO",
        "status_validacao": "NAO_DISPONIVEL",
        "motivo": "Bastiao/Resolver ainda nao disponivel no backend.",
        "bloqueio_operacional": False,
    }

    if contrato_resolver is None or bastiao_contrato is None:
        return base

    try:
        resolvido = contrato_resolver.resolver(ativo_base)
    except Exception as erro:
        base.update({
            "resolver_status": "ERRO_RESOLVER",
            "status_validacao": "ERRO",
            "motivo": f"Erro ao resolver contrato ativo: {erro}",
            "bloqueio_operacional": False,
        })
        return base

    base.update({
        "contrato_esperado_rtd": resolvido.contrato_rtd_esperado,
        "contrato_esperado_visual": resolvido.contrato_visual_esperado,
        "resolver_status": resolvido.status_resolucao,
        "resolver_motivo": resolvido.motivo,
        "data_referencia": resolvido.data_referencia,
        "criterio_usado": resolvido.criterio_usado,
    })

    if resolvido.status_resolucao != "RESOLVIDO":
        base.update({
            "status_validacao": "AGUARDANDO_CALENDARIO_OFICIAL",
            "motivo": resolvido.motivo,
            "bloqueio_operacional": False,
        })
        return base

    validacao = bastiao_contrato.validar(
        contrato_esperado_rtd=resolvido.contrato_rtd_esperado,
        contrato_excel_rtd=contrato_excel_rtd,
        contrato_backend_rtd=contrato_backend_rtd,
    )

    base.update({
        "status_validacao": validacao.status_validacao,
        "motivo": validacao.motivo,
        "bloqueio_operacional": validacao.bloqueio_operacional,
    })

    return base


def gerar_candle():
    """Lê candle institucional vindo do Excel/RTD.

    Se o leitor falhar, gera candle neutro para manter o servidor vivo.
    Esse fallback NAO deve ser usado para validacao operacional.
    """
    global preco_atual

    try:
        candle = ler_dados_institucionais()

        # Normalizacao minima de contrato para engines e frontend.
        candle["time"] = int(_num(candle.get("time"), int(datetime.now().timestamp())))
        # RTD entrega snapshot de sessao:
        # abertura/maximo/minimo sao da sessao, nao do candle.
        # Para o grafico em tempo real, montamos candle por variacao do ultimo preco.
        ultimo_preco = _num(
            candle.get("ultimo", candle.get("close", preco_atual)),
            preco_atual
        )

        open_tick = (
            _num(historico[-1].get("close", ultimo_preco), ultimo_preco)
            if historico else ultimo_preco
        )

        candle["open"] = round(open_tick, 2)
        candle["high"] = round(max(open_tick, ultimo_preco), 2)
        candle["low"] = round(min(open_tick, ultimo_preco), 2)
        candle["close"] = round(ultimo_preco, 2)
        candle["volume"] = _num(candle.get("volume"), 0)
        candle["delta"] = _num(candle.get("delta"), 0)
        candle["saldo"] = _num(candle.get("saldo", candle.get("saldo_agressor")), 0)
        candle["reversao_detectada"] = bool(candle.get("reversao_detectada", False))

        preco_atual = candle["close"]
        return candle

    except Exception as erro:
        print("[LEITOR INSTITUCIONAL ERRO]", erro)

        candle = {
            "time": int(datetime.now().timestamp()),
            "open": round(preco_atual, 2),
            "high": round(preco_atual, 2),
            "low": round(preco_atual, 2),
            "close": round(preco_atual, 2),
            "volume": 0,
            "delta": 0,
            "saldo": 0,
            "reversao_detectada": False,
        }

        return candle


def atualizar_historico():
    candle = gerar_candle()

    candle_engine.adicionar_candle(candle)
    candle["reversao_detectada"] = candle_engine.calcular_reversao()

    vwap_engine.adicionar_candle(candle)
    # Regra v6.1: nao duplicar timestamp no historico do painel.
    # O painel usa snapshot RTD/Excel em tempo real; se houver nova leitura no mesmo segundo,
    # atualiza o candle atual em vez de criar outro candle com o mesmo time.
    if historico and historico[-1].get("time") == candle.get("time"):
        ultimo = historico[-1]

        ultimo["high"] = max(
            _num(ultimo.get("high"), candle.get("high")),
            _num(candle.get("high"), candle.get("high"))
        )
        ultimo["low"] = min(
            _num(ultimo.get("low"), candle.get("low")),
            _num(candle.get("low"), candle.get("low"))
        )
        ultimo["close"] = candle.get("close")
        ultimo["volume"] = candle.get("volume")

        for chave in [
            "volume_real",
            "delta",
            "saldo",
            "ativo",
            "vwap_real",
            "volume_compra",
            "volume_venda",
            "volume_saldo",
            "reversao_detectada",
            "explosao_detectada",
            "tipo_explosao",
        ]:
            if chave in candle:
                ultimo[chave] = candle[chave]

        return ultimo

    historico.append(candle)

    if len(historico) > 100:
        historico.pop(0)

    return candle


def _montar_tick_confluencia(atual, vwap_atual, memoria, engine_data):
    saldo = _num(atual.get("saldo"), 0)

    compra = _num(atual.get("agressao_compra"), 0)
    venda = _num(atual.get("agressao_venda"), 0)

    # Quando o leitor nao trouxer compra/venda separados, derivamos do saldo.
    if compra == 0 and venda == 0:
        compra = max(saldo, 0)
        venda = max(-saldo, 0)

    return {
        "ativo": atual.get("ativo", "WIN"),
        "fractal": atual.get("fractal", "1_MIN"),
        "contexto": engine_data.get("engine_fase", "TEMPO_REAL"),
        "ultimo": atual.get("close"),
        "delta": atual.get("delta"),
        "saldo": atual.get("saldo"),
        "volume": atual.get("volume"),
        "vwap": vwap_atual,
        "agressao_compra": compra,
        "agressao_venda": venda,
        "score_agressao": memoria.get("score_agressao", 0),
    }


def gerar_payload():
    if len(historico) < 2:
        atualizar_historico()
        atualizar_historico()

    anterior = historico[-2]
    atual = historico[-1]

    contrato_ativo = _validar_contrato_ativo(atual)

    try:
       engine_data = engine.processar(atual, anterior)
    except AttributeError:
        engine_data = {
            "engine_score": 0,
            "engine_fase": "SIMULADO_TRINENGINE_SEM_PROCESSAR",
            "engine_direcao": "NEUTRO",
            "engine_seq_delta": 0,
            "engine_trap": None,
            "engine_absorcao": False,
            "engine_zona_low": None,
            "engine_zona_high": None,
     }

    vwap, banda_sup, banda_inf = vwap_engine.calcular_vwap_e_bandas()
    vwap_atual = vwap[-1]["value"] if vwap else atual["close"]

    distancia_vwap = round(abs(atual["close"] - vwap_atual), 2) if vwap else 0

    freq, status, intensidade = aggression_engine.calcular_frequencia(
        atual["saldo"],
        atual["delta"],
        atual["volume"]
    )

    memoria = aggression_engine.calcular_memoria_agressao(
        atual["saldo"],
        atual["delta"],
        atual["volume"]
    )

    explosao, tipo_explosao = aggression_engine.detectar_explosao_fluxo(
        atual["saldo"],
        atual["delta"],
        atual["volume"],
        memoria["score_agressao"],
        intensidade
    )

    global ultima_explosao_tipo, ultima_explosao_tempo
    agora = int(datetime.now().timestamp())

    if explosao:
        ultima_explosao_tipo = tipo_explosao
        ultima_explosao_tempo = agora

    tipo_explosao_painel = (
        ultima_explosao_tipo
        if agora - ultima_explosao_tempo <= 8
        else "SEM EXPLOSÃO"
    )

    atual["explosao_detectada"] = explosao
    atual["tipo_explosao"] = tipo_explosao_painel

    sinal_data = gerar_sinal(
        atual["saldo"],
        atual["volume"],
        atual["delta"],
        preco=atual["close"]
    )

    # ==============================
    # ENTRADA INSTITUCIONAL TRIN
    # ==============================
    engine_score = engine_data.get("engine_score", 0)
    engine_fase = engine_data.get("engine_fase", "AGUARDANDO")
    engine_direcao = engine_data.get("engine_direcao", "NEUTRO")
    engine_seq_delta = engine_data.get("engine_seq_delta", 0)
    engine_trap = engine_data.get("engine_trap")
    engine_absorcao = engine_data.get("engine_absorcao", False)

    score_agressao = memoria.get("score_agressao", 0)
    entrada_institucional = "AGUARDAR"

    if explosao and tipo_explosao == "BUY EXPLOSION":
        entrada_institucional = "COMPRA SCALPING CONTROLADO"

    elif explosao and tipo_explosao == "SELL EXPLOSION":
        entrada_institucional = "VENDA SCALPING CONTROLADO"

    elif (
        engine_score >= 6
        and engine_fase == "ROMPIMENTO"
        and engine_direcao == "COMPRA"
        and engine_seq_delta >= 2
        and atual["delta"] > 180
        and not engine_absorcao
    ):
        entrada_institucional = "COMPRA CONSERVADORA"

    elif (
        engine_score >= 6
        and engine_fase == "ROMPIMENTO"
        and engine_direcao == "VENDA"
        and engine_seq_delta <= -2
        and atual["delta"] < -180
        and not engine_absorcao
    ):
        entrada_institucional = "VENDA CONSERVADORA"

    elif (
        engine_fase == "DISTRIBUICAO"
        and engine_direcao == "VENDA"
        and atual["delta"] < -120
        and not engine_absorcao
    ):
        entrada_institucional = "VENDA MODERADA"

    elif (
        engine_fase == "ACUMULACAO"
        and engine_direcao == "COMPRA"
        and atual["delta"] > 120
        and not engine_absorcao
    ):
        entrada_institucional = "COMPRA MODERADA"

    elif (
        engine_score >= 5
        and engine_direcao == "COMPRA"
        and score_agressao > 5
        and (engine_trap == "COMPRA" or engine_absorcao)
    ):
        entrada_institucional = "COMPRA MODERADA"

    elif (
        engine_score >= 5
        and engine_direcao == "VENDA"
        and score_agressao < -5
        and (engine_trap == "VENDA" or engine_absorcao)
    ):
        entrada_institucional = "VENDA MODERADA"

    sinal_data["entrada"] = entrada_institucional

    # ==============================
    # ALERTA OPERACIONAL TRIN
    # ==============================
    alerta_operacional = "AGUARDANDO CONFIRMAÇÃO"

    if (
        engine_fase == "COMPRESSAO"
        and atual["delta"] < -100
        and score_agressao < -5
        and not engine_absorcao
    ):
        alerta_operacional = "ALERTA: PRESSÃO VENDEDORA EM COMPRESSÃO"

    elif (
        engine_fase == "COMPRESSAO"
        and atual["delta"] > 100
        and score_agressao > 5
        and not engine_absorcao
    ):
        alerta_operacional = "ALERTA: PRESSÃO COMPRADORA EM COMPRESSÃO"

    elif engine_fase == "DISTRIBUICAO" and engine_direcao == "VENDA":
        alerta_operacional = "ALERTA: DISTRIBUIÇÃO VENDEDORA"

    elif engine_fase == "ACUMULACAO" and engine_direcao == "COMPRA":
        alerta_operacional = "ALERTA: ACUMULAÇÃO COMPRADORA"

    elif engine_fase == "ROMPIMENTO":
        alerta_operacional = "ALERTA: ROMPIMENTO EM ANDAMENTO"

    sinal_data["tendencia"] = alerta_operacional

    # ==============================
    # GESTAO INSTITUCIONAL DINAMICA
    # STOP / PARCIAL / ALVO
    # ==============================
    zona_low = engine_data.get("engine_zona_low")
    zona_high = engine_data.get("engine_zona_high")
    preco_entrada = atual["close"]

    stop = sinal_data.get("stop")
    parcial = sinal_data.get("parcial")
    alvo = sinal_data.get("alvo")

    if zona_low is not None and zona_high is not None:
        zona_low = float(zona_low)
        zona_high = float(zona_high)
        preco_entrada = float(preco_entrada)

        range_zona = max(zona_high - zona_low, 0.5)
        buffer = max(range_zona * 0.20, 0.15)

        if entrada_institucional in ["COMPRA MODERADA", "COMPRA CONSERVADORA"]:
            stop = round(zona_low - buffer, 2)
            parcial = round(preco_entrada + range_zona, 2)
            alvo = round(preco_entrada + (range_zona * 2), 2)

        elif entrada_institucional in ["VENDA MODERADA", "VENDA CONSERVADORA"]:
            stop = round(zona_high + buffer, 2)
            parcial = round(preco_entrada - range_zona, 2)
            alvo = round(preco_entrada - (range_zona * 2), 2)

        elif entrada_institucional == "COMPRA SCALPING CONTROLADO":
            stop = round(preco_entrada - 0.60, 2)
            parcial = round(preco_entrada + 0.90, 2)
            alvo = round(preco_entrada + 1.60, 2)

        elif entrada_institucional == "VENDA SCALPING CONTROLADO":
            stop = round(preco_entrada + 0.60, 2)
            parcial = round(preco_entrada - 0.90, 2)
            alvo = round(preco_entrada - 1.60, 2)

    sinal_data["stop"] = stop
    sinal_data["parcial"] = parcial
    sinal_data["alvo"] = alvo

    # ==============================
    # MOTOR COGNITIVO TRIN v2.2
    # ==============================
    tick_confluencia = _montar_tick_confluencia(
        atual=atual,
        vwap_atual=vwap_atual,
        memoria=memoria,
        engine_data=engine_data,
    )

    resultado_confluencia = motor_confluencia.process(
        tick=tick_confluencia,
        agressao=memoria,
    )

    payload = {
        "historico": historico,
        "engine": engine_data,

        "vwap": vwap,
        "vwap_superior": banda_sup,
        "vwap_inferior": banda_inf,
        "distancia_vwap": distancia_vwap,

        "agressao": {
            "frequencia_mercado": freq,
            "status": status,
            "intensidade_fluxo": intensidade,
            **memoria,
            "explosao_detectada": explosao,
            "tipo_explosao": tipo_explosao_painel,
        },

        "confluencia": resultado_confluencia,
        "score_confluencia": resultado_confluencia.get("score_confluencia"),
        "direcao_confluencia": resultado_confluencia.get("direcao"),
        "qualidade_confluencia": resultado_confluencia.get("qualidade"),
        "alerta_confluencia": resultado_confluencia.get("alerta"),
        "justificativa_confluencia": resultado_confluencia.get("justificativa"),
        "evidencias_confluencia": resultado_confluencia.get("evidencias", []),
        "bloqueio_cognitivo": resultado_confluencia.get("qualidade") == "BLOQUEADO_POR_CERTIFICACAO",

        "painel_temporal": {
            "origem": "RTD_EXCEL_SNAPSHOT",
            "tipo_candle": "CANDLE_OPERACIONAL_TEMPO_REAL",
            "regua_painel": "SNAPSHOT_RTD",
            "timeframe_painel": "TEMPO_REAL_NAO_HOMOLOGADO",
            "fractal_oficial": "NAO_APLICAVEL",
            "profit_timeframe_visual": "NAO_INTEGRADO",
            "observacao": "Painel TRIN usa snapshot RTD/Excel em tempo real; nao representa automaticamente o timeframe visual do Profit nem fractal certificado do Ze."
        },

        "contrato_ativo": contrato_ativo,
        "contrato_ativo_status": contrato_ativo.get("status_validacao"),
        "contrato_ativo_motivo": contrato_ativo.get("motivo"),
        "contrato_ativo_bloqueio": contrato_ativo.get("bloqueio_operacional", False),

        **sinal_data,
    }

    return payload


@app.get("/data")
async def get_data():
    atualizar_historico()
    return gerar_payload()


@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    print("[WS CONNECT] cliente conectado")

    try:
        while True:
            atualizar_historico()
            payload = gerar_payload()
            await ws.send_json(payload)
            await asyncio.sleep(1)

    except WebSocketDisconnect:
        print("[WS DISCONNECT] cliente desconectado")

    except Exception as erro:
        print("[WS ERRO]", erro)

    finally:
        print("[WS CLOSE] conexao finalizada")
