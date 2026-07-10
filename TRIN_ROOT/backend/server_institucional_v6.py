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
from backend.replay_diagnostico import replay_reader
import asyncio
import json

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

# ============================================================
# CONFIGURACAO DE TIMEFRAME DO PAINEL
# Etapa 1: apenas registra opcoes e endpoint.
# Ainda nao altera o historico do grafico.
# Uso atual previsto: 15s ate 60_MIN.
# DIARIO e SEMANAL reservados por governanca.
# ============================================================

painel_timeframe_atual = "2_MIN"

TIMEFRAMES_PAINEL_SEGUNDOS = {
    "15s": 15,
    "30s": 30,
    "1_MIN": 60,
    "2_MIN": 120,
    "5_MIN": 300,
    "10_MIN": 600,
    "15_MIN": 900,
    "30_MIN": 1800,
    "60_MIN": 3600,
}

TIMEFRAMES_PAINEL_RESERVADOS = ["DIARIO", "SEMANAL"]

MAX_HISTORICO_RAW = 7200
MAX_HISTORICO_PAINEL = 300

preco_atual = 100.0

ultima_explosao_tipo = "SEM EXPLOSÃO"
ultima_explosao_tempo = 0

ultimo_reset_estado_operacional = {
    "executado": False,
    "sequencia": 0,
    "timestamp": None,
    "motivo": "INICIALIZACAO_BACKEND",
    "modo_destino": "AO_VIVO",
    "estado_anterior": {},
    "estado_posterior": {},
}


# CR-02A - cache idempotente do processamento operacional.
ultima_assinatura_evento_processado = None
ultimo_calculo_operacional = None
sequencia_processamento_operacional = 0
reutilizacoes_cache_operacional = 0


def _tamanho_lista_interna(objeto, atributo):
    valor = getattr(objeto, atributo, None)
    return len(valor) if isinstance(valor, list) else 0


def resetar_estado_operacional(motivo, modo_destino):
    """Recria todas as memorias mutaveis do cockpit de forma auditavel.

    Escopo CR-01A: impede que memoria AO VIVO atravesse para o Replay
    diagnostico e que memoria do Replay retorne ao modo AO VIVO.
    """
    global engine, vwap_engine, candle_engine, aggression_engine, motor_confluencia
    global historico, ultima_explosao_tipo, ultima_explosao_tempo
    global ultimo_reset_estado_operacional
    global ultima_assinatura_evento_processado, ultimo_calculo_operacional
    global sequencia_processamento_operacional, reutilizacoes_cache_operacional

    estado_anterior = {
        "historico": len(historico),
        "vwap_candles": _tamanho_lista_interna(vwap_engine, "candles"),
        "candle_engine_candles": _tamanho_lista_interna(candle_engine, "candles"),
        "agressao_fluxo_recente": _tamanho_lista_interna(aggression_engine, "fluxo_recente"),
        "agressao_memoria": _tamanho_lista_interna(aggression_engine, "memoria_agressao"),
        "confluencia_history": _tamanho_lista_interna(motor_confluencia, "history"),
        "cache_operacional_presente": ultimo_calculo_operacional is not None,
        "sequencia_processamento_operacional": sequencia_processamento_operacional,
        "reutilizacoes_cache_operacional": reutilizacoes_cache_operacional,
    }

    engine = TRINEngine()
    vwap_engine = VWAPEngine()
    candle_engine = CandleEngine()
    aggression_engine = AggressionEngine()
    motor_confluencia = ConfluenceEngineV2()

    historico = []
    ultima_explosao_tipo = "SEM EXPLOSÃO"
    ultima_explosao_tempo = 0
    ultima_assinatura_evento_processado = None
    ultimo_calculo_operacional = None
    sequencia_processamento_operacional = 0
    reutilizacoes_cache_operacional = 0

    sequencia = int(ultimo_reset_estado_operacional.get("sequencia", 0)) + 1
    estado_posterior = {
        "historico": len(historico),
        "vwap_candles": _tamanho_lista_interna(vwap_engine, "candles"),
        "candle_engine_candles": _tamanho_lista_interna(candle_engine, "candles"),
        "agressao_fluxo_recente": _tamanho_lista_interna(aggression_engine, "fluxo_recente"),
        "agressao_memoria": _tamanho_lista_interna(aggression_engine, "memoria_agressao"),
        "confluencia_history": _tamanho_lista_interna(motor_confluencia, "history"),
        "cache_operacional_presente": ultimo_calculo_operacional is not None,
        "sequencia_processamento_operacional": sequencia_processamento_operacional,
        "reutilizacoes_cache_operacional": reutilizacoes_cache_operacional,
    }

    ultimo_reset_estado_operacional = {
        "executado": True,
        "sequencia": sequencia,
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "motivo": str(motivo),
        "modo_destino": str(modo_destino),
        "estado_anterior": estado_anterior,
        "estado_posterior": estado_posterior,
    }

    print(
        "[CR-01 RESET ESTADO]",
        json.dumps(ultimo_reset_estado_operacional, ensure_ascii=False),
    )

    return dict(ultimo_reset_estado_operacional)


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


def normalizar_timeframe_painel(valor):
    texto = str(valor or "").strip().upper().replace(" ", "").replace("-", "_")

    aliases = {
        "15S": "15s",
        "30S": "30s",
        "1M": "1_MIN",
        "1MIN": "1_MIN",
        "1_MIN": "1_MIN",
        "2M": "2_MIN",
        "2MIN": "2_MIN",
        "2_MIN": "2_MIN",
        "5M": "5_MIN",
        "5MIN": "5_MIN",
        "5_MIN": "5_MIN",
        "10M": "10_MIN",
        "10MIN": "10_MIN",
        "10_MIN": "10_MIN",
        "15M": "15_MIN",
        "15MIN": "15_MIN",
        "15_MIN": "15_MIN",
        "30M": "30_MIN",
        "30MIN": "30_MIN",
        "30_MIN": "30_MIN",
        "60M": "60_MIN",
        "60MIN": "60_MIN",
        "60_MIN": "60_MIN",
        "DIARIO": "DIARIO",
        "D": "DIARIO",
        "SEMANAL": "SEMANAL",
        "W": "SEMANAL",
    }

    return aliases.get(texto)


def _bucket_time_painel(timestamp, timeframe):
    segundos = TIMEFRAMES_PAINEL_SEGUNDOS.get(timeframe)
    if not segundos:
        return None

    try:
        t = int(float(timestamp))
    except Exception:
        return None

    return int(t // segundos) * segundos


def agregar_historico_painel(historico_raw, timeframe):
    """
    Agrega snapshots RTD/Excel em candles operacionais para visualizacao do painel.
    Nao substitui o historico raw usado pelo motor.
    Nao gera fractal oficial.
    Nao certifica candle.
    """
    if timeframe in TIMEFRAMES_PAINEL_RESERVADOS:
        return []

    if timeframe not in TIMEFRAMES_PAINEL_SEGUNDOS:
        return []

    agregados = {}

    for candle in historico_raw:
        bucket = _bucket_time_painel(candle.get("time"), timeframe)
        if bucket is None:
            continue

        if bucket not in agregados:
            novo = dict(candle)
            novo["time"] = bucket
            novo["volume_normalizado_capado"] = candle.get("volume_normalizado_capado", candle.get("volume"))
            novo["volume_candle_estimado"] = _num(
                candle.get("volume_delta_estimado", candle.get("volume_candle_estimado")),
                0
            )
            novo["volume_delta_estimado"] = novo["volume_candle_estimado"]
            novo["volume_tipo"] = "REAL_DELTA_ESTIMADO"
            novo["timeframe_painel"] = timeframe
            novo["regua_painel"] = "RTD_AGREGADO"
            novo["status_painel"] = "OPERACIONAL_NAO_CERTIFICADO"
            agregados[bucket] = novo
            continue

        atual = agregados[bucket]

        atual["high"] = max(
            _num(atual.get("high"), candle.get("high")),
            _num(candle.get("high"), candle.get("high")),
        )
        atual["low"] = min(
            _num(atual.get("low"), candle.get("low")),
            _num(candle.get("low"), candle.get("low")),
        )
        atual["close"] = candle.get("close")
        atual["volume"] = candle.get("volume")
        atual["volume_normalizado_capado"] = candle.get("volume_normalizado_capado", candle.get("volume"))
        atual["volume_candle_estimado"] = _num(atual.get("volume_candle_estimado"), 0) + _num(
            candle.get("volume_delta_estimado", candle.get("volume_candle_estimado")),
            0
        )
        atual["volume_delta_estimado"] = atual["volume_candle_estimado"]
        atual["volume_tipo"] = "REAL_DELTA_ESTIMADO"
        atual["timeframe_painel"] = timeframe
        atual["regua_painel"] = "RTD_AGREGADO"
        atual["status_painel"] = "OPERACIONAL_NAO_CERTIFICADO"

        for chave in [
            "volume_real",
            "volume_normalizado_capado",
            "volume_tipo",
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
                atual[chave] = candle[chave]

    return list(agregados.values())[-MAX_HISTORICO_PAINEL:]


def calcular_volume_delta_estimado(candle, referencia=None):
    """
    Calcula volume estimado por diferenca de volume_real acumulado.
    Nao altera o campo legado `volume`, que permanece normalizado/capado.
    """
    try:
        volume_atual = _num(candle.get("volume_real"), 0)

        if referencia is None:
            return 0

        if candle.get("ativo") != referencia.get("ativo"):
            return 0

        if candle.get("data_excel") and referencia.get("data_excel"):
            if candle.get("data_excel") != referencia.get("data_excel"):
                return 0

        volume_anterior = _num(referencia.get("volume_real"), 0)
        delta = volume_atual - volume_anterior

        if delta < 0:
            return 0

        return round(delta, 2)
    except Exception:
        return 0


def enriquecer_volume_estimado(candle, referencia=None):
    """
    Preserva volume normalizado/capado e adiciona campos novos para auditoria/painel.
    """
    volume_delta = calcular_volume_delta_estimado(candle, referencia)

    candle["volume_normalizado_capado"] = candle.get("volume")
    candle["volume_delta_estimado"] = volume_delta
    candle["volume_candle_estimado"] = volume_delta
    candle["volume_tipo"] = "REAL_DELTA_ESTIMADO"

    return candle



def assinatura_fonte_rtd(candle):
    """
    Assinatura operacional da fonte RTD/Excel.
    Ignora o campo `time`, porque ele vem do relogio do backend.
    Se esta assinatura nao muda, a fonte nao entregou novo dado real.
    """
    if not candle:
        return None

    campos = [
        "ativo",
        "open",
        "high",
        "low",
        "close",
        "ultimo",
        "volume_real",
        "delta",
        "saldo",
        "vwap",
        "vwap_real",
        "volume_compra",
        "volume_venda",
        "volume_saldo",
    ]

    assinatura = []

    for campo in campos:
        valor = candle.get(campo)

        if isinstance(valor, float):
            valor = round(valor, 6)

        assinatura.append((campo, valor))

    return tuple(assinatura)


def fonte_rtd_estagnada(candle, referencia):
    """
    Detecta se a nova leitura RTD/Excel e identica a ultima leitura efetiva.
    Nao usa timestamp, pois timestamp e gerado pelo backend.
    """
    if not candle or not referencia:
        return False

    if candle.get("fonte_dados") != "RTD_EXCEL_PLAN1":
        return False

    if referencia.get("fonte_dados") != "RTD_EXCEL_PLAN1":
        return False

    return assinatura_fonte_rtd(candle) == assinatura_fonte_rtd(referencia)


def atualizar_historico():

    global historico

    if replay_reader.ativo:
        candle_replay = replay_reader.proximo_candle(painel_timeframe_atual)

        if candle_replay:
            if historico and historico[-1].get("time") == candle_replay.get("time"):
                historico[-1] = candle_replay
            else:
                historico.append(candle_replay)

            if len(historico) > MAX_HISTORICO_RAW:
                historico = historico[-MAX_HISTORICO_RAW:]

        return

    candle = gerar_candle()
    referencia_volume = historico[-1] if historico else None
    candle = enriquecer_volume_estimado(candle, referencia_volume)

    # Regra PATCH_CANDLEBUILDER_02:
    # nao cria candle novo quando o RTD/Excel esta parado.
    # O campo `time` muda pelo relogio do backend, portanto nao pode ser
    # usado sozinho como prova de novo candle operacional.
    if referencia_volume is not None and fonte_rtd_estagnada(candle, referencia_volume):
        referencia_volume["fonte_estagnada"] = True
        referencia_volume["status_fonte"] = "RTD_ESTAGNADO"
        referencia_volume["status_painel"] = "OPERACIONAL_NAO_CERTIFICADO_FONTE_ESTAGNADA"
        referencia_volume["observacao_fonte"] = (
            "Leitura RTD/Excel identica a anterior; candle novo nao foi criado."
        )
        return referencia_volume

    candle["fonte_estagnada"] = False
    candle["status_fonte"] = "RTD_ATUALIZANDO"

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
        ultimo["volume_normalizado_capado"] = candle.get("volume_normalizado_capado", candle.get("volume"))

        delta_volume_estimado = _num(candle.get("volume_delta_estimado"), 0)
        ultimo["volume_delta_estimado"] = _num(ultimo.get("volume_delta_estimado"), 0) + delta_volume_estimado
        ultimo["volume_candle_estimado"] = _num(ultimo.get("volume_candle_estimado"), 0) + delta_volume_estimado
        ultimo["volume_tipo"] = "REAL_DELTA_ESTIMADO"

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

    if len(historico) > MAX_HISTORICO_RAW:
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


def _valor_assinatura_evento(valor):
    if isinstance(valor, float):
        return round(valor, 6)
    return valor


def assinatura_evento_operacional(atual):
    """Identifica o fato de mercado sem usar resultados derivados dos motores."""
    modo_dados = "REPLAY" if replay_reader.ativo else "AO_VIVO"
    campos = [
        "ativo",
        "time",
        "close",
        "ultimo",
        "volume",
        "volume_real",
        "volume_candle_estimado",
        "delta",
        "saldo",
        "vwap_real",
    ]

    assinatura = [("modo_dados", modo_dados)]
    for campo in campos:
        assinatura.append((campo, _valor_assinatura_evento(atual.get(campo))))
    return tuple(assinatura)


def _copiar_calculo_operacional(calculo):
    """Entrega referencias de leitura do cache sem reprocessar os motores."""
    return {
        "engine_data": calculo["engine_data"],
        "vwap": calculo["vwap"],
        "banda_sup": calculo["banda_sup"],
        "banda_inf": calculo["banda_inf"],
        "vwap_atual": calculo["vwap_atual"],
        "distancia_vwap": calculo["distancia_vwap"],
        "freq": calculo["freq"],
        "status": calculo["status"],
        "intensidade": calculo["intensidade"],
        "memoria": calculo["memoria"],
        "explosao": calculo["explosao"],
        "tipo_explosao": calculo["tipo_explosao"],
        "sinal_data": dict(calculo["sinal_data"]),
        "resultado_confluencia": calculo["resultado_confluencia"],
    }


def gerar_payload():
    global ultima_explosao_tipo, ultima_explosao_tempo
    global ultima_assinatura_evento_processado, ultimo_calculo_operacional
    global sequencia_processamento_operacional, reutilizacoes_cache_operacional

    if len(historico) < 2:
        atualizar_historico()
        atualizar_historico()

    # Se houver 1 candle real, o payload pode continuar.
    # Isso acontece quando duas leituras caem no mesmo segundo e a regra
    # de nao duplicar timestamp atualiza o candle atual em vez de criar outro.
    if len(historico) == 0:
        agora = int(datetime.now().timestamp())

        candle_fallback = historico[-1] if historico else {
            "time": agora,
            "open": preco_atual,
            "high": preco_atual,
            "low": preco_atual,
            "close": preco_atual,
            "ultimo": preco_atual,
            "volume": 0,
            "volume_real": 0,
            "delta": 0,
            "saldo": 0,
            "ativo": "WIN",
            "vwap": preco_atual,
            "vwap_real": preco_atual,
            "fonte_dados": "RTD_EXCEL_INDISPONIVEL",
            "status_candle": "FALLBACK_SEM_HISTORICO_SUFICIENTE",
        }

        return {
            "historico": historico,
            "engine": {},
            "vwap": candle_fallback.get("vwap", preco_atual),
            "vwap_superior": candle_fallback.get("vwap", preco_atual),
            "vwap_inferior": candle_fallback.get("vwap", preco_atual),
            "distancia_vwap": 0,
            "ultimo": candle_fallback.get("ultimo", candle_fallback.get("close", preco_atual)),
            "volume": candle_fallback.get("volume", 0),
            "delta": candle_fallback.get("delta", 0),
            "saldo": candle_fallback.get("saldo", 0),
            "fonte_dados": "RTD_EXCEL_INDISPONIVEL",
            "modo_replay": False,
            "status_backend": "SEM_HISTORICO_SUFICIENTE",
            "erro_operacional": "historico com menos de 2 candles apos atualizar_historico",
            "painel_temporal": {
                "origem": "RTD_EXCEL_INDISPONIVEL",
                "tipo_candle": "FALLBACK_OPERACIONAL",
                "regua_painel": "SEM_REGUA",
                "timeframe_painel": painel_timeframe_atual,
                "status_painel": "SEM_HISTORICO_SUFICIENTE",
                "fractal_oficial": "NAO_APLICAVEL",
                "profit_timeframe_visual": "NAO_INTEGRADO",
                "timeframes_operacionais": list(TIMEFRAMES_PAINEL_SEGUNDOS.keys()),
                "timeframes_reservados": TIMEFRAMES_PAINEL_RESERVADOS,
                "timeframes_disponiveis": list(TIMEFRAMES_PAINEL_SEGUNDOS.keys()) + TIMEFRAMES_PAINEL_RESERVADOS,
                "observacao": "Backend preservado. Monitor RTD/Excel nao entregou historico suficiente para gerar payload operacional."
            },
            "contrato_ativo": {},
            "contrato_ativo_status": "NAO_VALIDADO",
            "contrato_ativo_motivo": "Sem candle atual suficiente.",
            "contrato_ativo_bloqueio": True,
            "sinal": "SEM SINAL",
            "entrada": "AGUARDAR",
            "score": 0,
        }

    anterior = historico[-2] if len(historico) >= 2 else historico[-1]
    atual = historico[-1]

    contrato_ativo = _validar_contrato_ativo(atual)
    assinatura_evento = assinatura_evento_operacional(atual)

    cache_reutilizado = (
        assinatura_evento == ultima_assinatura_evento_processado
        and isinstance(ultimo_calculo_operacional, dict)
    )

    if cache_reutilizado:
        reutilizacoes_cache_operacional += 1
        calculo = _copiar_calculo_operacional(ultimo_calculo_operacional)

        engine_data = calculo["engine_data"]
        vwap = calculo["vwap"]
        banda_sup = calculo["banda_sup"]
        banda_inf = calculo["banda_inf"]
        vwap_atual = calculo["vwap_atual"]
        distancia_vwap = calculo["distancia_vwap"]
        freq = calculo["freq"]
        status = calculo["status"]
        intensidade = calculo["intensidade"]
        memoria = calculo["memoria"]
        explosao = calculo["explosao"]
        tipo_explosao = calculo["tipo_explosao"]
        sinal_data = calculo["sinal_data"]
        resultado_confluencia = calculo["resultado_confluencia"]

        agora = int(datetime.now().timestamp())
        tipo_explosao_painel = (
            ultima_explosao_tipo
            if agora - ultima_explosao_tempo <= 8
            else "SEM EXPLOSÃO"
        )

        atual["explosao_detectada"] = explosao
        atual["tipo_explosao"] = tipo_explosao_painel

    else:
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

        sequencia_processamento_operacional += 1
        ultima_assinatura_evento_processado = assinatura_evento
        ultimo_calculo_operacional = {
            "engine_data": engine_data,
            "vwap": vwap,
            "banda_sup": banda_sup,
            "banda_inf": banda_inf,
            "vwap_atual": vwap_atual,
            "distancia_vwap": distancia_vwap,
            "freq": freq,
            "status": status,
            "intensidade": intensidade,
            "memoria": memoria,
            "explosao": explosao,
            "tipo_explosao": tipo_explosao,
            "sinal_data": dict(sinal_data),
            "resultado_confluencia": resultado_confluencia,
        }

    payload = {
        "historico": agregar_historico_painel(historico, painel_timeframe_atual) or historico,
        "engine": engine_data,
        "processamento_operacional": {
            "status": "CACHE_REUTILIZADO" if cache_reutilizado else "NOVO_EVENTO_PROCESSADO",
            "cache_reutilizado": cache_reutilizado,
            "sequencia": sequencia_processamento_operacional,
            "reutilizacoes_cache": reutilizacoes_cache_operacional,
            "modo_dados": "REPLAY" if replay_reader.ativo else "AO_VIVO",
            "assinatura_evento": [list(item) for item in assinatura_evento],
        },

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
            "origem": "RTD_EXCEL_AGREGADO",
            "tipo_candle": "CANDLE_OPERACIONAL_INTRADAY",
            "regua_painel": "RTD_AGREGADO",
            "timeframe_painel": painel_timeframe_atual,
            "status_painel": atual.get("status_painel", "OPERACIONAL_NAO_CERTIFICADO"),
            "status_fonte": atual.get("status_fonte", "RTD_ATUALIZANDO"),
            "fonte_estagnada": atual.get("fonte_estagnada", False),
            "fractal_oficial": "NAO_APLICAVEL",
            "profit_timeframe_visual": "NAO_INTEGRADO",
            "timeframes_operacionais": list(TIMEFRAMES_PAINEL_SEGUNDOS.keys()),
            "timeframes_reservados": TIMEFRAMES_PAINEL_RESERVADOS,
            "timeframes_disponiveis": list(TIMEFRAMES_PAINEL_SEGUNDOS.keys()) + TIMEFRAMES_PAINEL_RESERVADOS,
            "observacao": "Painel TRIN agrega snapshot RTD/Excel para visualizacao. Uso atual liberado ate 60_MIN. DIARIO e SEMANAL permanecem reservados por governanca."
        },

        "contrato_ativo": contrato_ativo,
        "contrato_ativo_status": contrato_ativo.get("status_validacao"),
        "contrato_ativo_motivo": contrato_ativo.get("motivo"),
        "contrato_ativo_bloqueio": contrato_ativo.get("bloqueio_operacional", False),

        **sinal_data,
    }

    payload = replay_reader.aplicar_payload(payload, painel_timeframe_atual)
    return payload



@app.get("/painel/timeframes")
async def painel_timeframes():
    return {
        "timeframe_atual": painel_timeframe_atual,
        "operacionais": list(TIMEFRAMES_PAINEL_SEGUNDOS.keys()),
        "reservados": TIMEFRAMES_PAINEL_RESERVADOS,
        "disponiveis": list(TIMEFRAMES_PAINEL_SEGUNDOS.keys()) + TIMEFRAMES_PAINEL_RESERVADOS,
        "status": "OPERACIONAL_ATE_60_MIN",
    }


@app.get("/painel/timeframe/{timeframe}")
async def alterar_timeframe_painel(timeframe: str):
    global painel_timeframe_atual

    normalizado = normalizar_timeframe_painel(timeframe)

    if normalizado in TIMEFRAMES_PAINEL_RESERVADOS:
        return {
            "ok": False,
            "timeframe_solicitado": timeframe,
            "timeframe_normalizado": normalizado,
            "status": "BLOQUEADO_POR_GOVERNANCA",
            "motivo": "DIARIO e SEMANAL estao planejados, mas ainda nao homologados para uso atual.",
        }

    if normalizado not in TIMEFRAMES_PAINEL_SEGUNDOS:
        return {
            "ok": False,
            "timeframe_solicitado": timeframe,
            "status": "TIMEFRAME_INVALIDO",
            "permitidos": list(TIMEFRAMES_PAINEL_SEGUNDOS.keys()) + TIMEFRAMES_PAINEL_RESERVADOS,
        }

    painel_timeframe_atual = normalizado

    return {
        "ok": True,
        "timeframe_painel_configurado": painel_timeframe_atual,
        "status": "OPERACIONAL_NAO_CERTIFICADO",
        "observacao": "Timeframe configurado. Grafico passa a usar agregacao operacional nao certificada.",
    }


# ============================================================
# TT RAW - DIAGNOSTICO EXPERIMENTAL
# Le apenas o status organizado da captura Times & Trades RTD.
# Nao alimenta CandleBuilder.
# Nao altera fluxo operacional.
# Nao certifica dados.
# ============================================================

@app.get("/tt/raw/status")
async def tt_raw_status():
    caminho = (
        Path(__file__).resolve().parents[1]
        / "TRIN_HISTORICO"
        / "00_PROCESSAMENTO_TT"
        / "painel_tt_raw_status.json"
    )

    if not caminho.exists():
        return {
            "status": "TT_RAW_STATUS_NAO_ENCONTRADO",
            "arquivo": str(caminho),
            "arquivo_existe": False,
            "observacao": "Diagnostico TT RAW ainda nao foi gerado."
        }

    try:
        with open(caminho, "r", encoding="utf-8") as f:
            dados = json.load(f)

        dados["arquivo"] = str(caminho)
        dados["arquivo_existe"] = True
        dados["endpoint"] = "/tt/raw/status"
        dados["uso_operacional"] = "DIAGNOSTICO_APENAS"
        dados["candle_oficial"] = False

        return dados

    except Exception as erro:
        return {
            "status": "ERRO_LEITURA_TT_RAW_STATUS",
            "arquivo": str(caminho),
            "arquivo_existe": True,
            "erro": str(erro),
            "uso_operacional": "DIAGNOSTICO_APENAS",
            "candle_oficial": False
        }



@app.get("/painel/replay/status")
async def replay_status():
    resultado = replay_reader.status()
    resultado["estado_operacional_reset"] = dict(ultimo_reset_estado_operacional)
    return resultado


@app.get("/painel/replay/start")
async def replay_start(csv_path: str = "", data_pregao: str = "", intervalo_segundos: float = 1.5):
    estava_em_replay = bool(replay_reader.ativo)

    resultado = replay_reader.start(
        csv_path=csv_path,
        data_pregao=data_pregao,
        intervalo_segundos=intervalo_segundos,
    )

    if resultado.get("ok"):
        motivo = "REPLAY_RESTART" if estava_em_replay else "REPLAY_START"
        resultado["estado_operacional_reset"] = resetar_estado_operacional(
            motivo=motivo,
            modo_destino="REPLAY_DIAGNOSTICO",
        )
        resultado["reset_executado_nesta_chamada"] = True

    elif estava_em_replay and not replay_reader.ativo:
        resultado["estado_operacional_reset"] = resetar_estado_operacional(
            motivo="REPLAY_START_FALHOU_RETORNO_AO_VIVO",
            modo_destino="AO_VIVO",
        )
        resultado["reset_executado_nesta_chamada"] = True

    else:
        resultado["reset_executado_nesta_chamada"] = False

    return resultado


@app.get("/painel/replay/stop")
async def replay_stop():
    estava_em_replay = bool(replay_reader.ativo)
    resultado = replay_reader.stop()

    if estava_em_replay:
        resultado["estado_operacional_reset"] = resetar_estado_operacional(
            motivo="REPLAY_STOP",
            modo_destino="AO_VIVO",
        )
        resultado["reset_executado_nesta_chamada"] = True
    else:
        resultado["reset_executado_nesta_chamada"] = False
        resultado["observacao"] = (
            "Replay ja estava parado. Estado operacional AO VIVO preservado."
        )

    return resultado


@app.get("/painel/replay/reset")
async def replay_reset():
    estava_em_replay = bool(replay_reader.ativo)
    resultado = replay_reader.reset()

    if estava_em_replay:
        resultado["estado_operacional_reset"] = resetar_estado_operacional(
            motivo="REPLAY_RESET",
            modo_destino="REPLAY_DIAGNOSTICO",
        )
        resultado["reset_executado_nesta_chamada"] = True
    else:
        resultado["reset_executado_nesta_chamada"] = False
        resultado["observacao"] = (
            "Replay esta parado. Estado operacional AO VIVO preservado."
        )

    return resultado


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
