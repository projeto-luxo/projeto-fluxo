
from pathlib import Path

from core.caminhos_oficiais import BIBLIOTECA_HISTORICA
from datetime import datetime
import csv
import time


TRIN_ROOT_PATH = Path(__file__).resolve().parents[1]

REPLAY_CSV_PADRAO = (
    BIBLIOTECA_HISTORICA
    / "001_1_MIN"
    / "win"
    / "WINFUT_F_0_1min.csv"
)


class ReplayDiagnostico:
    def __init__(self):
        self.ativo = False
        self.csv = str(REPLAY_CSV_PADRAO)
        self.data_pregao = ""
        self.linhas = []
        self.indice = 0
        self.total = 0
        self.ultimo_erro = ""
        self.ultimo_candle_time = None
        self.intervalo_segundos = 1.5
        self.ultimo_emit_wall = 0.0
        self.bucket_replay_linhas = []
        self.bucket_replay_inicio_ts = None
        self.bucket_replay_limite_ts = None

    def status(self):
        return {
            "ok": True,
            "ativo": self.ativo,
            "modo_dados": "REPLAY" if self.ativo else "AO_VIVO",
            "csv": self.csv,
            "data_pregao": self.data_pregao,
            "indice": self.indice,
            "total": self.total,
            "ultimo_erro": self.ultimo_erro,
            "ultimo_candle_time": self.ultimo_candle_time,
            "intervalo_segundos": self.intervalo_segundos,
            "observacao": "Replay diagnostico. Nao operacional e nao certificado.",
        }

    def _num(self, valor, padrao=0.0):
        try:
            if valor is None:
                return padrao

            texto = str(valor).strip()

            if texto == "":
                return padrao

            # formato BR: 191002,68
            if "," in texto:
                texto = texto.replace(".", "").replace(",", ".")

            return float(texto)
        except Exception:
            return padrao

    def _campo(self, linha, nomes, padrao=None):
        for nome in nomes:
            if nome in linha and str(linha.get(nome, "")).strip() != "":
                return linha.get(nome)

        mapa = {str(k).strip().lower(): k for k in linha.keys()}

        for nome in nomes:
            chave = mapa.get(str(nome).strip().lower())
            if chave is not None and str(linha.get(chave, "")).strip() != "":
                return linha.get(chave)

        return padrao

    def _campo_com_origem(self, linha, nomes):
        for nome in nomes:
            if nome in linha and str(linha.get(nome, "")).strip() != "":
                return linha.get(nome), str(nome)

        mapa = {str(k).strip().lower(): k for k in linha.keys()}

        for nome in nomes:
            chave = mapa.get(str(nome).strip().lower())
            if chave is not None and str(linha.get(chave, "")).strip() != "":
                return linha.get(chave), str(chave)

        return None, None

    def _rotulo_campo_replay(self, campo, padrao):
        if not campo:
            return padrao

        texto = "".join(
            caractere if caractere.isalnum() else "_"
            for caractere in str(campo).upper().strip()
        )
        texto = "_".join(parte for parte in texto.split("_") if parte)
        return f"REPLAY_CSV_CAMPO_{texto}" if texto else padrao

    def _timestamp(self, linha, indice=0):
        bruto = self._campo(linha, ["time", "timestamp", "datahora", "datetime"], None)

        if bruto is not None:
            texto = str(bruto).strip()

            try:
                if texto.replace(".", "", 1).isdigit():
                    return int(float(texto))
            except Exception:
                pass

            for fmt in [
                "%Y-%m-%d %H:%M:%S",
                "%Y-%m-%d %H:%M",
                "%d/%m/%Y %H:%M:%S",
                "%d/%m/%Y %H:%M",
                "%d-%m-%Y %H:%M:%S",
                "%d-%m-%Y %H:%M",
            ]:
                try:
                    return int(datetime.strptime(texto, fmt).timestamp())
                except Exception:
                    pass

        data = self._campo(linha, ["data", "date"], None)
        hora = self._campo(linha, ["hora", "horario"], None)

        if data is not None and hora is not None:
            texto = f"{str(data).strip()} {str(hora).strip()}"

            for fmt in [
                "%Y-%m-%d %H:%M:%S",
                "%Y-%m-%d %H:%M",
                "%d/%m/%Y %H:%M:%S",
                "%d/%m/%Y %H:%M",
                "%d-%m-%Y %H:%M:%S",
                "%d-%m-%Y %H:%M",
            ]:
                try:
                    return int(datetime.strptime(texto, fmt).timestamp())
                except Exception:
                    pass

        return 1700000000 + int(indice) * 60

    def _normalizar_data_pregao(self, data_pregao):
        alvo = str(data_pregao or "").strip()

        if not alvo:
            return "", ""

        try:
            if "-" in alvo and len(alvo) >= 10:
                dt = datetime.strptime(alvo[:10], "%Y-%m-%d")
            else:
                dt = datetime.strptime(alvo[:10], "%d/%m/%Y")

            return dt.strftime("%Y-%m-%d"), dt.strftime("%d/%m/%Y")
        except Exception:
            return alvo, alvo

    def carregar_csv(self, caminho_csv="", data_pregao=""):
        caminho = Path(caminho_csv or self.csv or REPLAY_CSV_PADRAO)

        if not caminho.exists():
            self.ultimo_erro = f"CSV replay nao encontrado: {caminho}"
            self.linhas = []
            self.total = 0
            self.indice = 0
            return False

        try:
            amostra = caminho.read_text(encoding="utf-8-sig", errors="ignore")[:4096]
            delimitador = ";" if amostra.count(";") >= amostra.count(",") else ","

            with caminho.open("r", encoding="utf-8-sig", errors="ignore", newline="") as f:
                linhas_brutas = list(csv.reader(f, delimiter=delimitador))

            linhas_brutas = [
                linha for linha in linhas_brutas
                if linha and any(str(v).strip() for v in linha)
            ]

            if not linhas_brutas:
                self.ultimo_erro = f"CSV replay vazio: {caminho}"
                return False

            primeira = [str(v).strip().lower() for v in linhas_brutas[0]]

            tem_cabecalho = any(
                nome in primeira
                for nome in [
                    "open",
                    "high",
                    "low",
                    "close",
                    "abertura",
                    "maximo",
                    "minimo",
                    "fechamento",
                    "data",
                    "hora",
                ]
            )

            linhas = []

            if tem_cabecalho:
                with caminho.open("r", encoding="utf-8-sig", errors="ignore", newline="") as f:
                    reader = csv.DictReader(f, delimiter=delimitador)
                    linhas = [
                        dict(l) for l in reader
                        if any(str(v).strip() for v in l.values())
                    ]
            else:
                # CSV Profit sem cabecalho:
                # ativo;data;hora;open;high;low;close;volume;volume_quantidade
                colunas = [
                    "ativo",
                    "data",
                    "hora",
                    "open",
                    "high",
                    "low",
                    "close",
                    "volume",
                    "volume_quantidade",
                ]

                for linha in linhas_brutas:
                    obj = {}
                    for i, nome in enumerate(colunas):
                        obj[nome] = linha[i] if i < len(linha) else ""
                    linhas.append(obj)

            alvo_iso, alvo_br = self._normalizar_data_pregao(data_pregao)

            if data_pregao:
                linhas = [
                    linha for linha in linhas
                    if str(self._campo(linha, ["data", "date"], "")).strip() in [alvo_iso, alvo_br]
                ]

            linhas = sorted(linhas, key=lambda linha: self._timestamp(linha, 0))

            self.csv = str(caminho)
            self.data_pregao = str(data_pregao or "")
            self.linhas = linhas
            self.total = len(linhas)
            self.indice = 0
            self.ultimo_candle_time = None
            self.ultimo_erro = ""

            if not linhas:
                self.ultimo_erro = f"Nenhuma linha encontrada para data_pregao={data_pregao}"
                return False

            return True

        except Exception as e:
            self.ultimo_erro = f"Erro ao carregar CSV replay: {e}"
            self.linhas = []
            self.total = 0
            self.indice = 0
            return False

    def linha_para_candle(self, linha, indice, timeframe_painel="1_MIN"):
        abertura = self._num(self._campo(linha, ["open", "abertura", "abre", "o"], 0))
        maximo = self._num(self._campo(linha, ["high", "maximo", "máximo", "max", "h"], abertura))
        minimo = self._num(self._campo(linha, ["low", "minimo", "mínimo", "min", "l"], abertura))
        ultimo = self._num(self._campo(linha, ["close", "fechamento", "ultimo", "último", "last", "c"], abertura))

        if ultimo <= 0:
            ultimo = abertura

        volume = self._num(self._campo(linha, ["volume", "volume_quantidade", "vol"], 0))

        delta_bruto, delta_campo = self._campo_com_origem(linha, ["delta"])
        saldo_bruto, saldo_campo = self._campo_com_origem(
            linha,
            ["saldo", "agressao_saldo", "agressão_saldo"],
        )
        volume_saldo_bruto, volume_saldo_campo = self._campo_com_origem(
            linha,
            ["volume_saldo"],
        )

        delta_presente = delta_campo is not None
        saldo_presente = saldo_campo is not None
        volume_saldo_presente = volume_saldo_campo is not None

        delta = self._num(delta_bruto, 0)
        saldo_fallback_delta = bool(not saldo_presente and delta_presente)
        saldo = self._num(saldo_bruto, delta if saldo_fallback_delta else 0)
        volume_saldo = self._num(volume_saldo_bruto, 0)

        delta_fonte = self._rotulo_campo_replay(
            delta_campo,
            "REPLAY_CSV_SEM_DELTA",
        )
        saldo_fonte = (
            "REPLAY_FALLBACK_DELTA"
            if saldo_fallback_delta
            else self._rotulo_campo_replay(saldo_campo, "REPLAY_CSV_SEM_SALDO")
        )

        if not delta_presente and not saldo_presente:
            delta_saldo_relacao = "SEM_DADOS"
        elif saldo_fallback_delta:
            delta_saldo_relacao = "SALDO_DERIVADO_DELTA"
        elif delta_presente and saldo_presente:
            delta_saldo_relacao = (
                "EQUIVALENTES_OBSERVADOS"
                if abs(delta - saldo) <= 1e-9
                else "INDEPENDENTES"
            )
        else:
            delta_saldo_relacao = "INDETERMINADO"

        delta_saldo_independentes = delta_saldo_relacao == "INDEPENDENTES"

        if volume_saldo_presente:
            fluxo_agressor_canonico = volume_saldo
            fluxo_agressor_fonte = self._rotulo_campo_replay(
                volume_saldo_campo,
                "REPLAY_CSV_VOLUME_SALDO",
            )
        elif saldo_presente:
            fluxo_agressor_canonico = saldo
            fluxo_agressor_fonte = saldo_fonte
        elif delta_presente:
            fluxo_agressor_canonico = delta
            fluxo_agressor_fonte = delta_fonte
        else:
            fluxo_agressor_canonico = 0.0
            fluxo_agressor_fonte = "SEM_DADOS"

        fluxo_agressor_status = (
            "CANONICO_DISPONIVEL"
            if fluxo_agressor_fonte != "SEM_DADOS"
            else "SEM_DADOS"
        )

        vwap = self._num(self._campo(linha, ["vwap", "VWAP"], ultimo))

        t = self._timestamp(linha, indice)
        ativo = str(self._campo(linha, ["ativo", "symbol"], "WINFUT")).strip() or "WINFUT"

        candle = {
            "time": t,
            "ativo": ativo,
            "contrato": "WIN_REPLAY_F_0",
            "fonte_dados": "REPLAY_CSV",
            "modo_dados": "REPLAY",
            "open": abertura,
            "high": max(maximo, abertura, ultimo),
            "low": min(minimo, abertura, ultimo),
            "close": ultimo,
            "ultimo": ultimo,
            "volume": volume,
            "volume_real": volume,
            "volume_normalizado_capado": volume,
            "volume_delta_estimado": volume,
            "volume_candle_estimado": volume,
            "volume_tipo": "REPLAY_CSV",
            "delta": delta,
            "saldo": saldo,
            **({"volume_saldo": volume_saldo} if volume_saldo_presente else {}),
            "delta_fonte": delta_fonte,
            "saldo_fonte": saldo_fonte,
            "delta_saldo_relacao": delta_saldo_relacao,
            "delta_saldo_independentes": delta_saldo_independentes,
            "saldo_fallback_delta": saldo_fallback_delta,
            "fluxo_agressor_canonico": fluxo_agressor_canonico,
            "fluxo_agressor_fonte": fluxo_agressor_fonte,
            "fluxo_agressor_status": fluxo_agressor_status,
            "vwap": vwap,
            "status_fonte": "REPLAY_ATIVO",
            "fonte_estagnada": False,
            "status_painel": "REPLAY_OPERACIONAL_NAO_CERTIFICADO",
            "timeframe_painel": timeframe_painel,
            "regua_painel": "REPLAY_AGREGADO",
        }

        return candle



    def _limpar_estado_execucao(self):
        self.indice = 0
        self.ultimo_candle_time = None
        self.ultimo_emit_wall = 0.0
        self.bucket_replay_linhas = []
        self.bucket_replay_inicio_ts = None
        self.bucket_replay_limite_ts = None

    def start(self, csv_path="", data_pregao="", intervalo_segundos=1.5):
        self._limpar_estado_execucao()
        ok = self.carregar_csv(csv_path, data_pregao)

        try:
            self.intervalo_segundos = max(0.3, float(intervalo_segundos or 1.5))
        except Exception:
            self.intervalo_segundos = 1.5

        self.ultimo_emit_wall = 0.0

        if not ok:
            self.ativo = False
            return {
                "ok": False,
                "ativo": False,
                "modo_dados": "AO_VIVO",
                "status": "REPLAY_CSV_ERRO",
                "erro": self.ultimo_erro,
                "csv": self.csv,
                "data_pregao": data_pregao,
            }

        self.ativo = True

        return {
            "ok": True,
            "ativo": True,
            "modo_dados": "REPLAY",
            "status": "REPLAY_INICIADO",
            "csv": self.csv,
            "data_pregao": self.data_pregao,
            "total": self.total,
            "intervalo_segundos": self.intervalo_segundos,
            "observacao": "Replay diagnostico iniciado. Nao operacional e nao certificado.",
        }


    def stop(self):
        self.ativo = False
        self._limpar_estado_execucao()

        return {
            "ok": True,
            "ativo": False,
            "modo_dados": "AO_VIVO",
            "status": "REPLAY_PARADO",
            "observacao": "Replay parado. Estado interno do Replay foi limpo.",
        }

    def reset(self):
        self._limpar_estado_execucao()

        return {
            "ok": True,
            "ativo": self.ativo,
            "modo_dados": "REPLAY" if self.ativo else "AO_VIVO",
            "status": "REPLAY_RESETADO",
        }




    def _segundos_timeframe(self, timeframe_painel="1_MIN"):
        tf = str(timeframe_painel or "1_MIN").upper().strip()

        # O replay atual nasce de CSV 1_MIN.
        # Para 15s/30s, nao ha granularidade real no arquivo.
        # Portanto o menor passo real do replay historico e 1 minuto.
        if tf.endswith("S"):
            return 60

        if "_MIN" in tf:
            try:
                return max(60, int(tf.replace("_MIN", "")) * 60)
            except Exception:
                return 60

        return 60

    def _qtd_origem_por_timeframe(self, timeframe_painel="1_MIN"):
        return max(1, int(self._segundos_timeframe(timeframe_painel) / 60))

    def _montar_candle_bucket(self, timeframe_painel="1_MIN", completo=False):
        if not self.bucket_replay_linhas:
            return None

        candles = [
            self.linha_para_candle(linha, indice, timeframe_painel)
            for linha, indice in self.bucket_replay_linhas
        ]

        abertura = candles[0]["open"]
        fechamento = candles[-1]["close"]
        maximo = max(float(c["high"]) for c in candles)
        minimo = min(float(c["low"]) for c in candles)
        volume = sum(float(c.get("volume") or 0) for c in candles)
        delta = sum(float(c.get("delta") or 0) for c in candles)
        saldo = sum(float(c.get("saldo") or 0) for c in candles)
        fluxo_agressor_canonico = sum(
            float(c.get("fluxo_agressor_canonico") or 0)
            for c in candles
        )

        relacoes = {
            str(c.get("delta_saldo_relacao") or "INDETERMINADO")
            for c in candles
        }
        delta_saldo_relacao = (
            next(iter(relacoes)) if len(relacoes) == 1 else "INDETERMINADO"
        )
        delta_saldo_independentes = bool(candles) and all(
            bool(c.get("delta_saldo_independentes", False))
            for c in candles
        )
        saldo_fallback_delta = bool(candles) and all(
            bool(c.get("saldo_fallback_delta", False))
            for c in candles
        )

        delta_fontes = sorted({str(c.get("delta_fonte") or "SEM_DADOS") for c in candles})
        saldo_fontes = sorted({str(c.get("saldo_fonte") or "SEM_DADOS") for c in candles})
        fluxo_fontes = sorted({str(c.get("fluxo_agressor_fonte") or "SEM_DADOS") for c in candles})

        delta_fonte = "REPLAY_AGREGADO:" + "|".join(delta_fontes)
        saldo_fonte = "REPLAY_AGREGADO:" + "|".join(saldo_fontes)
        fluxo_agressor_fonte = "REPLAY_AGREGADO:" + "|".join(fluxo_fontes)
        fluxo_agressor_status = (
            "SEM_DADOS"
            if all(c.get("fluxo_agressor_status") == "SEM_DADOS" for c in candles)
            else "CANONICO_AGREGADO"
        )

        volume_saldo_presentes = [
            float(c.get("volume_saldo") or 0)
            for c in candles
            if "volume_saldo" in c
        ]
        volume_saldo = (
            sum(volume_saldo_presentes)
            if len(volume_saldo_presentes) == len(candles)
            else None
        )

        soma_peso = 0.0
        soma_vwap = 0.0

        for c in candles:
            vol = float(c.get("volume") or 0)
            preco_vwap = float(c.get("vwap") or c.get("close") or 0)
            peso = vol if vol > 0 else 1.0
            soma_peso += peso
            soma_vwap += preco_vwap * peso

        vwap = soma_vwap / soma_peso if soma_peso else fechamento

        status_candle = "REPLAY_COMPLETO" if completo else "REPLAY_PARCIAL"

        candle = {
            **candles[-1],
            "time": self.bucket_replay_inicio_ts,
            "open": abertura,
            "high": maximo,
            "low": minimo,
            "close": fechamento,
            "ultimo": fechamento,
            "volume": volume,
            "volume_real": volume,
            "volume_normalizado_capado": volume,
            "volume_delta_estimado": volume,
            "volume_candle_estimado": volume,
            "volume_tipo": "REPLAY_CSV_EM_FORMACAO",
            "delta": delta,
            "saldo": saldo,
            **({"volume_saldo": volume_saldo} if volume_saldo is not None else {}),
            "delta_fonte": delta_fonte,
            "saldo_fonte": saldo_fonte,
            "delta_saldo_relacao": delta_saldo_relacao,
            "delta_saldo_independentes": delta_saldo_independentes,
            "saldo_fallback_delta": saldo_fallback_delta,
            "fluxo_agressor_canonico": fluxo_agressor_canonico,
            "fluxo_agressor_fonte": fluxo_agressor_fonte,
            "fluxo_agressor_status": fluxo_agressor_status,
            "vwap": vwap,
            "timeframe_painel": timeframe_painel,
            "qtd_candles_origem": len(candles),
            "qtd_candles_esperados": self._qtd_origem_por_timeframe(timeframe_painel),
            "status_candle": status_candle,
            "candle_em_formacao": not completo,
            "regua_painel": "REPLAY_AGREGADO",
        }

        return candle

    def proximo_candle(self, timeframe_painel="1_MIN"):
        if not self.ativo:
            return None

        agora = time.time()

        if self.ultimo_emit_wall and (agora - self.ultimo_emit_wall) < self.intervalo_segundos:
            return None

        if not self.linhas:
            ok = self.carregar_csv(self.csv, self.data_pregao)
            if not ok:
                return None

        if not self.linhas:
            self.ultimo_erro = "Replay sem linhas carregadas."
            return None

        if self.indice >= len(self.linhas):
            # Se sobrou um candle parcial no final do arquivo, fecha ele antes de parar.
            if self.bucket_replay_linhas:
                candle_final = self._montar_candle_bucket(timeframe_painel, completo=True)
                self.bucket_replay_linhas = []
                self.bucket_replay_inicio_ts = None
                self.bucket_replay_limite_ts = None
                self.ultimo_emit_wall = agora
                return candle_final

            self.ativo = False
            self.ultimo_erro = "Replay finalizado."
            return None

        tf_segundos = self._segundos_timeframe(timeframe_painel)
        qtd_esperada = self._qtd_origem_por_timeframe(timeframe_painel)

        linha = self.linhas[self.indice]
        ts = self._timestamp(linha, self.indice)

        # Inicia novo candle em formacao.
        if not self.bucket_replay_linhas:
            self.bucket_replay_inicio_ts = ts
            self.bucket_replay_limite_ts = ts + tf_segundos

        self.bucket_replay_linhas.append((linha, self.indice))
        self.indice += 1

        completo = False

        if len(self.bucket_replay_linhas) >= qtd_esperada:
            completo = True

        if self.indice >= len(self.linhas):
            completo = True

        candle = self._montar_candle_bucket(timeframe_painel, completo=completo)

        if completo:
            self.bucket_replay_linhas = []
            self.bucket_replay_inicio_ts = None
            self.bucket_replay_limite_ts = None

        self.ultimo_candle_time = candle.get("time") if candle else None
        self.ultimo_emit_wall = agora
        self.ultimo_erro = ""

        return candle

    def aplicar_payload(self, payload, timeframe_painel="1_MIN"):
        if not isinstance(payload, dict):
            return payload

        payload["replay"] = self.status()

        if not self.ativo:
            return payload

        painel = payload.get("painel_temporal") or {}

        painel.update({
            "origem": "REPLAY_CSV",
            "modo": "REPLAY",
            "modo_operacional": "REPLAY",
            "fonte_operacional": "REPLAY_CSV",
            "tipo_candle": "CANDLE_REPLAY_DIAGNOSTICO",
            "regua_painel": "REPLAY_AGREGADO",
            "timeframe_painel": timeframe_painel,
            "status_painel": "REPLAY_OPERACIONAL_NAO_CERTIFICADO",
            "status_fonte": "REPLAY_ATIVO",
            "fonte_estagnada": False,
            "fractal_oficial": "NAO_APLICAVEL",
            "profit_timeframe_visual": "NAO_APLICAVEL",
            "observacao": "MODO REPLAY DIAGNOSTICO. Nao operacional, nao certificado e nao deve ser usado para decisao real.",
        })

        payload["painel_temporal"] = painel
        payload["modo"] = "REPLAY"
        payload["modo_dados"] = "REPLAY"
        payload["modo_operacional"] = "REPLAY"
        payload["modoOperacional"] = "REPLAY"
        payload["fonte_dados"] = "REPLAY_CSV"
        payload["fonteDados"] = "REPLAY_CSV"
        payload["fonte_operacional"] = "REPLAY_CSV"
        payload["contrato_ativo"] = {
            "contrato_excel_rtd": "WIN_REPLAY_F_0",
            "contrato_esperado": "WIN_REPLAY_F_0",
            "status_validacao": "REPLAY_NAO_OPERACIONAL",
            "bloqueio_operacional": True,
            "motivo": "Replay diagnostico. Nao usar para decisao real.",
        }
        payload["contrato_ativo_status"] = "REPLAY_NAO_OPERACIONAL"
        payload["contrato_ativo_bloqueio"] = True
        payload["contrato_ativo_motivo"] = "Replay diagnostico. Nao usar para decisao real."

        return payload


replay_reader = ReplayDiagnostico()
