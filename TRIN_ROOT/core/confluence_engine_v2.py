# core/confluence_engine_v2.py
# ============================================================
# MOTOR DE CONFLUENCIA v2.3 — TRIN
#
# Responsabilidade unica:
# - Combinar evidencias ponderadas para medir qualidade/contexto.
#
# NAO FAZ:
# - Nao executa ordem.
# - Nao substitui operador.
# - Nao le CSV bruto diretamente.
# - Nao certifica dados.
# - Nao gera fractais.
#
# Entradas esperadas:
# - tick atual do mercado
# - evidencias operacionais ja calculadas
# - contexto historico/cognitivo vindo de Bernardo/Historiador
# - status de certificacao vindo do Fiscal
#
# Saida:
# - score_confluencia
# - direcao
# - qualidade
# - evidencias
# - justificativa
# - alerta
# ============================================================

from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Optional

try:
    from intelligence.historiador_adapter import HistoriadorAdapter
except ModuleNotFoundError:
    try:
        from historiador_adapter import HistoriadorAdapter
    except ModuleNotFoundError:
        HistoriadorAdapter = None


@dataclass
class Evidencia:
    nome: str
    valor: Any
    peso: float
    impacto: float
    direcao: str
    justificativa: str


class ConfluenceEngineV2:
    def __init__(self, janela_historico: int = 30):
        self.janela_historico = janela_historico
        self.history: List[Dict[str, Any]] = []

        self.historiador = None
        if HistoriadorAdapter is not None:
            try:
                self.historiador = HistoriadorAdapter()
            except Exception:
                self.historiador = None

    def _num(self, valor: Any, default: float = 0.0) -> float:
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

    def _clamp(self, valor: float, minimo: float, maximo: float) -> float:
        return max(minimo, min(maximo, valor))


    @staticmethod
    def _booleano(valor: Any, default: bool = True) -> bool:
        if isinstance(valor, bool):
            return valor

        if valor is None:
            return default

        texto = str(valor).strip().lower()
        if texto in {"true", "1", "sim", "yes", "verdadeiro"}:
            return True
        if texto in {"false", "0", "nao", "não", "no", "falso"}:
            return False

        return default

    def _resolver_contexto_fluxo(self, tick: Dict[str, Any]) -> Dict[str, Any]:
        delta = self._num(tick.get("delta"))
        saldo = self._num(tick.get("saldo"))
        relacao = str(
            tick.get("delta_saldo_relacao") or "INDETERMINADO"
        ).strip().upper()

        independentes = self._booleano(
            tick.get("delta_saldo_independentes"),
            default=True,
        )

        if relacao == "INDEPENDENTES":
            independentes = True
        elif relacao in {
            "EQUIVALENTES_OBSERVADOS",
            "SALDO_DERIVADO_DELTA",
            "DELTA_DERIVADO_SALDO",
            "SEM_DADOS",
        }:
            independentes = False

        fluxo_informado = tick.get("fluxo_agressor_canonico")
        if fluxo_informado is None:
            if relacao == "SEM_DADOS":
                fluxo_canonico = 0.0
            elif tick.get("saldo") is not None:
                fluxo_canonico = saldo
            else:
                fluxo_canonico = delta
        else:
            fluxo_canonico = self._num(fluxo_informado)

        if relacao == "SEM_DADOS":
            modo = "SEM_DADOS"
        elif independentes:
            modo = "DUPLA_INDEPENDENTE"
        else:
            modo = "CANONICA_UNICA"

        return {
            "delta": delta,
            "saldo": saldo,
            "fluxo_canonico": fluxo_canonico,
            "relacao": relacao,
            "independentes": independentes,
            "modo": modo,
            "fluxo_fonte": tick.get("fluxo_agressor_fonte"),
            "fluxo_status": tick.get("fluxo_agressor_status"),
        }

    def _correlacao_fluxo_agressao(
        self,
        tick: Dict[str, Any],
        agressao: Optional[Dict[str, Any]],
    ) -> Dict[str, Any]:
        contexto = self._resolver_contexto_fluxo(tick)
        agressao = agressao or {}
        modo_agressao = str(
            agressao.get("modo_evidencia_agressao") or "NAO_DECLARADO"
        ).strip().upper()

        correlacionados = (
            not contexto["independentes"]
            and modo_agressao == "CANONICA_UNICA"
        )

        return {
            "correlacionados": correlacionados,
            "classificacao": (
                "MESMA_ORIGEM_CANONICA_TRANSFORMACOES_DISTINTAS"
                if correlacionados
                else "NAO_DECLARADA_COMO_CORRELACIONADA"
            ),
            "modo_agressao": modo_agressao,
            "confirmacao_direcional_independente": not correlacionados,
        }

    def _registrar_historico(self, tick: Dict[str, Any]) -> None:
        self.history.append(tick)

        if len(self.history) > self.janela_historico:
            self.history = self.history[-self.janela_historico:]

    def _obter_contexto_historico(
        self,
        tick: Dict[str, Any],
        contexto_historico: Optional[Dict[str, Any]],
    ) -> Dict[str, Any]:
        if contexto_historico:
            return contexto_historico

        if self.historiador is None:
            return {
                "padrao": "SEM_PADRAO",
                "score_historico": 0.0,
                "confianca": 0.0,
                "frequencia": 0,
                "episodio": "HistoriadorAdapter indisponivel.",
                "contexto": tick.get("contexto", "DESCONHECIDO"),
                "direcao": "NEUTRO",
                "fonte": "ConfluenceEngineV2",
                "status": "SEM_HISTORIADOR",
            }

        try:
            return self.historiador.consultar(
                ativo=tick.get("ativo"),
                fractal=tick.get("fractal"),
                contexto=tick.get("contexto"),
            )
        except Exception as erro:
            return {
                "padrao": "ERRO_HISTORIADOR",
                "score_historico": 0.0,
                "confianca": 0.0,
                "frequencia": 0,
                "episodio": f"Erro ao consultar HistoriadorAdapter: {erro}",
                "contexto": tick.get("contexto", "DESCONHECIDO"),
                "direcao": "NEUTRO",
                "fonte": "ConfluenceEngineV2",
                "status": "ERRO_HISTORIADOR",
            }

    def _evidencia_fluxo(self, tick: Dict[str, Any]) -> Evidencia:
        contexto = self._resolver_contexto_fluxo(tick)
        delta = contexto["delta"]
        saldo = contexto["saldo"]
        fluxo_canonico = contexto["fluxo_canonico"]

        if contexto["independentes"]:
            bruto = (delta + saldo) / 20000

            if delta > 0 and saldo > 0:
                direcao = "COMPRA"
                justificativa = (
                    "Delta e saldo independentes positivos indicam fluxo comprador."
                )
            elif delta < 0 and saldo < 0:
                direcao = "VENDA"
                justificativa = (
                    "Delta e saldo independentes negativos indicam fluxo vendedor."
                )
            else:
                direcao = "NEUTRO"
                justificativa = (
                    "Delta e saldo independentes nao confirmam a mesma direcao."
                )
        else:
            # CR-03D3: uma unica grandeza canonica ocupa apenas um dos dois
            # componentes historicos da formula. O peso 2.0 permanece intacto;
            # o que deixa de existir e a confirmacao duplicada Delta + Saldo.
            bruto = fluxo_canonico / 20000

            if fluxo_canonico > 0:
                direcao = "COMPRA"
            elif fluxo_canonico < 0:
                direcao = "VENDA"
            else:
                direcao = "NEUTRO"

            justificativa = (
                "Fluxo agressor canonico consumido uma unica vez; "
                f"Delta e saldo com relacao {contexto['relacao']} nao constituem "
                "confirmacao independente."
            )

        impacto = self._clamp(bruto, -3.0, 3.0)

        return Evidencia(
            "FLUXO_DELTA_SALDO",
            {
                "delta": delta,
                "saldo": saldo,
                "fluxo_agressor_canonico": fluxo_canonico,
                "fluxo_agressor_fonte": contexto["fluxo_fonte"],
                "fluxo_agressor_status": contexto["fluxo_status"],
                "delta_saldo_relacao": contexto["relacao"],
                "delta_saldo_independentes": contexto["independentes"],
                "modo_evidencia_fluxo": contexto["modo"],
                "confirmacao_delta_saldo_independente": contexto["independentes"],
            },
            2.0,
            impacto,
            direcao,
            justificativa,
        )

    def _evidencia_agressao(
        self,
        tick: Dict[str, Any],
        agressao: Optional[Dict[str, Any]],
    ) -> Evidencia:
        compra = self._num(tick.get("agressao_compra"))
        venda = self._num(tick.get("agressao_venda"))
        saldo_agressao = compra - venda
        agressao = agressao or {}

        score_agressao = self._num(
            agressao.get("score_agressao"),
            default=saldo_agressao / 100000,
        )

        impacto = self._clamp(score_agressao / 5, -3.0, 3.0)
        leitura = str(agressao.get("leitura_agressao", "")).upper()

        if "COMPRADORA" in leitura or saldo_agressao > 0:
            direcao = "COMPRA"
        elif "VENDEDORA" in leitura or saldo_agressao < 0:
            direcao = "VENDA"
        else:
            direcao = "NEUTRO"

        correlacao = self._correlacao_fluxo_agressao(tick, agressao)

        justificativa = (
            "Agressao mede persistencia e intensidade do fluxo agressor."
        )
        if correlacao["correlacionados"]:
            justificativa = (
                "Agressao mede persistencia e intensidade derivadas do mesmo "
                "fluxo canonico; correlacao declarada e nao usada como segunda "
                "confirmacao direcional independente."
            )

        return Evidencia(
            "AGRESSAO",
            {
                "compra": compra,
                "venda": venda,
                "score_agressao": score_agressao,
                "leitura": leitura,
                "modo_evidencia_agressao": correlacao["modo_agressao"],
                "fluxo_agressor_utilizado": agressao.get(
                    "fluxo_agressor_utilizado"
                ),
                "correlacionada_fluxo_canonico": correlacao["correlacionados"],
                "correlacao_fluxo_agressao": correlacao["classificacao"],
                "confirmacao_direcional_independente": correlacao[
                    "confirmacao_direcional_independente"
                ],
            },
            1.5,
            impacto,
            direcao,
            justificativa,
        )

    def _evidencia_vwap(self, tick: Dict[str, Any]) -> Evidencia:
        ultimo = self._num(tick.get("ultimo"))
        vwap = self._num(tick.get("vwap"))

        if ultimo <= 0 or vwap <= 0:
            return Evidencia(
                "VWAP",
                {"ultimo": ultimo, "vwap": vwap},
                1.0,
                0.0,
                "NEUTRO",
                "VWAP indisponivel ou invalida.",
            )

        distancia = ultimo - vwap
        impacto = self._clamp(distancia / 1500, -2.0, 2.0)

        if distancia > 0:
            direcao = "COMPRA"
            justificativa = "Preco acima da VWAP indica pressao acima do valor medio."
        elif distancia < 0:
            direcao = "VENDA"
            justificativa = "Preco abaixo da VWAP indica pressao abaixo do valor medio."
        else:
            direcao = "NEUTRO"
            justificativa = "Preco exatamente na VWAP."

        return Evidencia(
            "VWAP",
            {"ultimo": ultimo, "vwap": vwap, "distancia": distancia},
            1.0,
            impacto,
            direcao,
            justificativa,
        )

    def _evidencia_historica(self, contexto_historico: Optional[Dict[str, Any]]) -> Evidencia:
        contexto_historico = contexto_historico or {}

        score = self._num(contexto_historico.get("score_historico"))
        confianca = self._num(contexto_historico.get("confianca"))
        frequencia = int(self._num(contexto_historico.get("frequencia"), 0))
        padrao = str(contexto_historico.get("padrao", "SEM_PADRAO"))
        episodio = str(contexto_historico.get("episodio", "SEM_EPISODIO"))
        status = str(contexto_historico.get("status", "DESCONHECIDO"))
        direcao = str(contexto_historico.get("direcao", "NEUTRO")).upper()

        impacto = self._clamp(score, -2.0, 2.0)

        return Evidencia(
            "HISTORIADOR",
            {
                "score_historico": score,
                "confianca": confianca,
                "frequencia": frequencia,
                "padrao": padrao,
                "episodio": episodio,
                "status": status,
                "direcao": direcao,
            },
            1.2,
            impacto,
            direcao if direcao in {"COMPRA", "VENDA"} else "NEUTRO",
            episodio or "Contexto historico fornecido pelo HistoriadorAdapter.",
        )

    def _evidencia_certificacao(self, certificacao: Optional[Dict[str, Any]]) -> Evidencia:
        certificacao = certificacao or {}
        status = str(certificacao.get("status", "DESCONHECIDO")).upper()

        if status in {"CERTIFICADO", "APROVADO", "OK"}:
            impacto = 1.0
            direcao = "NEUTRO"
            justificativa = "Base certificada pelo Fiscal Temporal."
        elif status in {"APROVADO_COM_RESSALVAS", "RESSALVA"}:
            impacto = -0.5
            direcao = "NEUTRO"
            justificativa = "Base com ressalvas; confluencia deve ser usada com cautela."
        elif status in {"REPROVADO", "REPROVADO_COM_PENDENCIAS"}:
            impacto = -3.0
            direcao = "BLOQUEIO_ANALITICO"
            justificativa = "Base reprovada; nao usar como conhecimento confirmado."
        else:
            impacto = 0.0
            direcao = "NEUTRO"
            justificativa = "Status de certificacao desconhecido."

        return Evidencia(
            "FISCAL_TEMPORAL",
            {"status": status},
            2.0,
            impacto,
            direcao,
            justificativa,
        )

    def _decidir_direcao(self, evidencias: List[Evidencia]) -> str:
        def voto_direcional(evidencia: Evidencia) -> bool:
            valor = evidencia.valor
            if not isinstance(valor, dict):
                return True
            return valor.get("confirmacao_direcional_independente", True) is not False

        compra = sum(
            e.peso
            for e in evidencias
            if e.direcao == "COMPRA" and voto_direcional(e)
        )
        venda = sum(
            e.peso
            for e in evidencias
            if e.direcao == "VENDA" and voto_direcional(e)
        )

        if compra > venda * 1.25:
            return "COMPRA"
        if venda > compra * 1.25:
            return "VENDA"
        return "NEUTRO"

    def _qualidade(self, score: float, certificacao: Optional[Dict[str, Any]]) -> str:
        status = str((certificacao or {}).get("status", "")).upper()

        if status in {"REPROVADO", "REPROVADO_COM_PENDENCIAS"}:
            return "BLOQUEADO_POR_CERTIFICACAO"

        abs_score = abs(score)

        if abs_score >= 8:
            return "FORTE"
        if abs_score >= 5:
            return "MEDIA"
        if abs_score >= 2:
            return "FRACA"

        return "NEUTRA"

    def process(
        self,
        tick: Dict[str, Any],
        agressao: Optional[Dict[str, Any]] = None,
        contexto_historico: Optional[Dict[str, Any]] = None,
        certificacao: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        self._registrar_historico(tick)

        contexto_historico = self._obter_contexto_historico(
            tick=tick,
            contexto_historico=contexto_historico,
        )

        evidencias = [
            self._evidencia_fluxo(tick),
            self._evidencia_agressao(tick, agressao),
            self._evidencia_vwap(tick),
            self._evidencia_historica(contexto_historico),
            self._evidencia_certificacao(certificacao),
        ]

        score = sum(e.impacto * e.peso for e in evidencias)
        score = round(self._clamp(score, -10.0, 10.0), 2)

        direcao = self._decidir_direcao(evidencias)
        qualidade = self._qualidade(score, certificacao)

        justificativas = [
            e.justificativa
            for e in evidencias
            if e.justificativa
        ]

        alerta = None

        if qualidade == "FORTE":
            alerta = (
                f"CONFLUENCIA_{direcao}_FORTE"
                if direcao != "NEUTRO"
                else "CONFLUENCIA_FORTE_NEUTRA"
            )
        elif qualidade == "BLOQUEADO_POR_CERTIFICACAO":
            alerta = "CONFLUENCIA_BLOQUEADA_PELO_FISCAL"

        contexto_fluxo = self._resolver_contexto_fluxo(tick)
        correlacao = self._correlacao_fluxo_agressao(tick, agressao)

        return {
            "score_confluencia": score,
            "direcao": direcao,
            "qualidade": qualidade,
            "alerta": alerta,
            "evidencias": [asdict(e) for e in evidencias],
            "justificativa": " | ".join(justificativas),
            "modo_evidencia_fluxo": contexto_fluxo["modo"],
            "delta_saldo_relacao": contexto_fluxo["relacao"],
            "delta_saldo_independentes": contexto_fluxo["independentes"],
            "fluxo_agressor_canonico": contexto_fluxo["fluxo_canonico"],
            "fluxo_agressao_correlacionados": correlacao["correlacionados"],
            "correlacao_fluxo_agressao": correlacao["classificacao"],
            "agressao_confirmacao_direcional_independente": correlacao[
                "confirmacao_direcional_independente"
            ],
            "motor": "ConfluenceEngineV2",
            "versao": "2.3",
        }
