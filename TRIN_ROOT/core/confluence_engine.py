# core/confluence_engine_v2.py
# ============================================================
# MOTOR DE CONFLUENCIA v2.2 — TRIN
#
# Responsabilidade unica:
# - Combinar evidencias ponderadas para medir qualidade/contexto.
#
# Integracoes v2.2:
# - HistoriadorAdapter
# - FiscalAdapter
# - BernardoAdapter
#
# NAO FAZ:
# - Nao executa ordem.
# - Nao substitui operador.
# - Nao le CSV bruto diretamente.
# - Nao certifica dados.
# - Nao gera fractais.
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

try:
    from intelligence.fiscal_adapter import FiscalAdapter
except ModuleNotFoundError:
    try:
        from fiscal_adapter import FiscalAdapter
    except ModuleNotFoundError:
        FiscalAdapter = None

try:
    from intelligence.bernardo_adapter import BernardoAdapter
except ModuleNotFoundError:
    try:
        from bernardo_adapter import BernardoAdapter
    except ModuleNotFoundError:
        BernardoAdapter = None


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

        self.historiador = self._iniciar_adapter(HistoriadorAdapter)
        self.fiscal = self._iniciar_adapter(FiscalAdapter)
        self.bernardo = self._iniciar_adapter(BernardoAdapter)

    def _iniciar_adapter(self, classe):
        if classe is None:
            return None

        try:
            return classe()
        except Exception:
            return None

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

    def _obter_certificacao(
        self,
        certificacao: Optional[Dict[str, Any]],
    ) -> Dict[str, Any]:
        if certificacao:
            return certificacao

        if self.fiscal is None:
            return {"status": "DESCONHECIDO"}

        try:
            return self.fiscal.consultar()
        except Exception as erro:
            return {
                "status": "ERRO_FISCAL",
                "erro": str(erro),
            }

    def _obter_memoria_bernardo(
        self,
        tick: Dict[str, Any],
        memoria_bernardo: Optional[Dict[str, Any]],
        contexto_historico: Dict[str, Any],
    ) -> Dict[str, Any]:
        if memoria_bernardo:
            return memoria_bernardo

        if self.bernardo is None:
            return {
                "episodio_semelhante": False,
                "similaridade": 0.0,
                "ocorrencias": 0,
                "resultado_medio": "DESCONHECIDO",
                "confianca": 0.0,
                "direcao": "NEUTRO",
                "status": "SEM_BERNARDO",
            }

        try:
            return self.bernardo.consultar(
                ativo=tick.get("ativo"),
                fractal=tick.get("fractal"),
                contexto=tick.get("contexto"),
                padrao=contexto_historico.get("padrao"),
            )
        except Exception as erro:
            return {
                "episodio_semelhante": False,
                "similaridade": 0.0,
                "ocorrencias": 0,
                "resultado_medio": "ERRO_BERNARDO",
                "confianca": 0.0,
                "direcao": "NEUTRO",
                "status": "ERRO_BERNARDO",
                "erro": str(erro),
            }

    def _evidencia_fluxo(self, tick: Dict[str, Any]) -> Evidencia:
        delta = self._num(tick.get("delta"))
        saldo = self._num(tick.get("saldo"))

        bruto = (delta + saldo) / 20000
        impacto = self._clamp(bruto, -3.0, 3.0)

        if delta > 0 and saldo > 0:
            direcao = "COMPRA"
            justificativa = "Delta e saldo positivos indicam fluxo comprador."
        elif delta < 0 and saldo < 0:
            direcao = "VENDA"
            justificativa = "Delta e saldo negativos indicam fluxo vendedor."
        else:
            direcao = "NEUTRO"
            justificativa = "Delta e saldo nao confirmam a mesma direcao."

        return Evidencia(
            "FLUXO_DELTA_SALDO",
            {"delta": delta, "saldo": saldo},
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

        score_agressao = self._num(
            (agressao or {}).get("score_agressao"),
            default=saldo_agressao / 100000,
        )

        impacto = self._clamp(score_agressao / 5, -3.0, 3.0)
        leitura = str((agressao or {}).get("leitura_agressao", "")).upper()

        if "COMPRADORA" in leitura or saldo_agressao > 0:
            direcao = "COMPRA"
        elif "VENDEDORA" in leitura or saldo_agressao < 0:
            direcao = "VENDA"
        else:
            direcao = "NEUTRO"

        return Evidencia(
            "AGRESSAO",
            {
                "compra": compra,
                "venda": venda,
                "score_agressao": score_agressao,
                "leitura": leitura,
            },
            1.5,
            impacto,
            direcao,
            "Agressao mede persistencia e intensidade do fluxo agressor.",
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

    def _evidencia_historica(self, contexto_historico: Dict[str, Any]) -> Evidencia:
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

    def _evidencia_bernardo(self, memoria_bernardo: Dict[str, Any]) -> Evidencia:
        similaridade = self._num(memoria_bernardo.get("similaridade"))
        confianca = self._num(memoria_bernardo.get("confianca"))
        ocorrencias = int(self._num(memoria_bernardo.get("ocorrencias"), 0))
        direcao = str(memoria_bernardo.get("direcao", "NEUTRO")).upper()
        status = str(memoria_bernardo.get("status", "DESCONHECIDO"))
        resultado_medio = str(memoria_bernardo.get("resultado_medio", "DESCONHECIDO"))

        impacto = self._clamp((similaridade + confianca) / 2, -2.0, 2.0)

        return Evidencia(
            "BERNARDO",
            {
                "episodio_semelhante": bool(memoria_bernardo.get("episodio_semelhante")),
                "similaridade": similaridade,
                "confianca": confianca,
                "ocorrencias": ocorrencias,
                "resultado_medio": resultado_medio,
                "status": status,
                "direcao": direcao,
            },
            1.6,
            impacto,
            direcao if direcao in {"COMPRA", "VENDA"} else "NEUTRO",
            "Memoria cognitiva fornecida pelo BernardoAdapter.",
        )

    def _evidencia_certificacao(self, certificacao: Dict[str, Any]) -> Evidencia:
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
        compra = sum(e.peso for e in evidencias if e.direcao == "COMPRA")
        venda = sum(e.peso for e in evidencias if e.direcao == "VENDA")

        if compra > venda * 1.25:
            return "COMPRA"
        if venda > compra * 1.25:
            return "VENDA"

        return "NEUTRO"

    def _qualidade(self, score: float, certificacao: Dict[str, Any]) -> str:
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
        memoria_bernardo: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        self._registrar_historico(tick)

        contexto_historico = self._obter_contexto_historico(
            tick=tick,
            contexto_historico=contexto_historico,
        )

        certificacao = self._obter_certificacao(certificacao)

        memoria_bernardo = self._obter_memoria_bernardo(
            tick=tick,
            memoria_bernardo=memoria_bernardo,
            contexto_historico=contexto_historico,
        )

        evidencias = [
            self._evidencia_fluxo(tick),
            self._evidencia_agressao(tick, agressao),
            self._evidencia_vwap(tick),
            self._evidencia_historica(contexto_historico),
            self._evidencia_bernardo(memoria_bernardo),
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

        return {
            "score_confluencia": score,
            "direcao": direcao,
            "qualidade": qualidade,
            "alerta": alerta,
            "evidencias": [asdict(e) for e in evidencias],
            "justificativa": " | ".join(justificativas),
            "motor": "ConfluenceEngineV2",
            "versao": "2.2",
        }
