from __future__ import annotations

from dataclasses import asdict, dataclass
from decimal import Decimal, InvalidOperation, ROUND_CEILING, ROUND_FLOOR
from typing import Any, Iterable, Optional, Protocol


USO_OPERACIONAL = "BLOQUEADO"
VERSAO_REGRA = "1.2"

FONTES_VWAP_OFICIAL = frozenset(
    {
        "RTD_EXCEL_VWAP_REAL",
        "RTD_EXCEL_VWAP",
        "REPLAY_CSV_VWAP",
        "REPLAY_CSV_VWAP_REAL",
    }
)


def _decimal_positivo(valor: Any) -> Optional[Decimal]:
    try:
        numero = Decimal(str(valor))
    except (InvalidOperation, TypeError, ValueError):
        return None

    if not numero.is_finite() or numero <= 0:
        return None

    return numero


def _normalizar_numero(valor: Decimal) -> str:
    return format(valor.quantize(Decimal("0.01")), "f")


@dataclass(frozen=True)
class ContextoReferencia:
    ativo: str
    contrato: str
    data_referencia: str
    sessao_referencia: str
    modo_dados: str
    timestamp_fonte: str
    timestamp_processamento: str
    qualidade_dados: str
    status_certificacao: str
    versao_regra: str = VERSAO_REGRA

    def validar(self) -> None:
        campos = asdict(self)
        ausentes = [
            nome
            for nome, valor in campos.items()
            if valor is None or not str(valor).strip()
        ]
        if ausentes:
            raise ValueError(
                "Contexto incompleto: " + ", ".join(sorted(ausentes))
            )


@dataclass(frozen=True)
class ReferenciaMercado:
    chave_referencia: str
    ativo: str
    contrato: str
    data_referencia: str
    sessao_referencia: str
    origem_tipo: str
    funcao_provavel: str
    status_funcao: str
    limite_inferior: Optional[float]
    limite_superior: Optional[float]
    fornecedor: str
    campo_origem: str
    timeframe_origem: str
    modo_dados: str
    timestamp_fonte: str
    timestamp_processamento: str
    status: str
    motivo_status: str
    qualidade_dados: str
    status_certificacao: str
    uso_operacional: str
    versao_regra: str

    def para_dict(self) -> dict[str, Any]:
        return asdict(self)


class ProvedorReferencia(Protocol):
    nome: str

    def localizar(
        self,
        payload: dict[str, Any],
        contexto: ContextoReferencia,
    ) -> Iterable[ReferenciaMercado]:
        ...


class FabricaReferencia:
    @staticmethod
    def criar(
        *,
        contexto: ContextoReferencia,
        origem_tipo: str,
        fornecedor: str,
        campo_origem: str,
        timeframe_origem: str,
        valor: Optional[Decimal],
        status: str,
        motivo_status: str = "",
    ) -> ReferenciaMercado:
        token_valor = (
            _normalizar_numero(valor)
            if valor is not None
            else "SEM_VALOR"
        )

        partes_chave = (
            "REF",
            contexto.ativo.strip().upper(),
            contexto.contrato.strip().upper(),
            contexto.data_referencia.strip(),
            contexto.sessao_referencia.strip().upper(),
            origem_tipo.strip().upper(),
            fornecedor.strip().upper(),
            campo_origem.strip().upper(),
            timeframe_origem.strip().upper(),
            token_valor,
            contexto.versao_regra.strip(),
        )

        limite = float(valor) if valor is not None else None

        return ReferenciaMercado(
            chave_referencia="|".join(partes_chave),
            ativo=contexto.ativo.strip().upper(),
            contrato=contexto.contrato.strip().upper(),
            data_referencia=contexto.data_referencia.strip(),
            sessao_referencia=contexto.sessao_referencia.strip().upper(),
            origem_tipo=origem_tipo,
            funcao_provavel="INDETERMINADA",
            status_funcao="NAO_AVALIADA",
            limite_inferior=limite,
            limite_superior=limite,
            fornecedor=fornecedor,
            campo_origem=campo_origem,
            timeframe_origem=timeframe_origem,
            modo_dados=contexto.modo_dados.strip().upper(),
            timestamp_fonte=contexto.timestamp_fonte,
            timestamp_processamento=contexto.timestamp_processamento,
            status=status,
            motivo_status=motivo_status,
            qualidade_dados=contexto.qualidade_dados,
            status_certificacao=contexto.status_certificacao,
            uso_operacional=USO_OPERACIONAL,
            versao_regra=contexto.versao_regra,
        )


class ProvedorMilhar:
    nome = "MILHAR"

    def __init__(self, passo: int = 1000) -> None:
        if passo <= 0:
            raise ValueError("O passo do milhar deve ser positivo.")
        self._passo = Decimal(str(passo))

    def localizar(
        self,
        payload: dict[str, Any],
        contexto: ContextoReferencia,
    ) -> Iterable[ReferenciaMercado]:
        preco = _decimal_positivo(payload.get("preco_atual"))
        qualificado = bool(payload.get("preco_qualificado"))

        if preco is None or not qualificado:
            motivo = (
                "PRECO_INVALIDO"
                if preco is None
                else "PRECO_NAO_QUALIFICADO"
            )
            return (
                FabricaReferencia.criar(
                    contexto=contexto,
                    origem_tipo="MILHAR",
                    fornecedor="PRECO_CANONICO_QUALIFICADO",
                    campo_origem="PRECO_ATUAL",
                    timeframe_origem="TICK",
                    valor=None,
                    status="BLOQUEADA",
                    motivo_status=motivo,
                ),
            )

        inferior = (
            (preco / self._passo)
            .to_integral_value(rounding=ROUND_FLOOR)
            * self._passo
        )
        superior = (
            (preco / self._passo)
            .to_integral_value(rounding=ROUND_CEILING)
            * self._passo
        )

        niveis = [("MILHAR_INFERIOR", inferior)]
        if superior != inferior:
            niveis.append(("MILHAR_SUPERIOR", superior))

        return tuple(
            FabricaReferencia.criar(
                contexto=contexto,
                origem_tipo="MILHAR",
                fornecedor="PRECO_CANONICO_QUALIFICADO",
                campo_origem=campo,
                timeframe_origem="TICK",
                valor=nivel,
                status="ATIVA",
            )
            for campo, nivel in niveis
        )


class ProvedorVWAPOficial:
    nome = "VWAP_OFICIAL"

    def localizar(
        self,
        payload: dict[str, Any],
        contexto: ContextoReferencia,
    ) -> Iterable[ReferenciaMercado]:
        valor = _decimal_positivo(payload.get("vwap_oficial"))
        fonte = str(payload.get("vwap_fonte") or "").strip().upper()
        origem_confirmada = bool(
            payload.get("vwap_origem_confirmada")
        )

        status = "ATIVA"
        motivo = ""

        if valor is None:
            status = "BLOQUEADA"
            motivo = "VWAP_VALOR_INVALIDO"
        elif fonte not in FONTES_VWAP_OFICIAL:
            status = "BLOQUEADA"
            motivo = "VWAP_FONTE_NAO_HOMOLOGADA"
        elif not origem_confirmada:
            status = "BLOQUEADA"
            motivo = "VWAP_ORIGEM_NAO_CONFIRMADA"

        return (
            FabricaReferencia.criar(
                contexto=contexto,
                origem_tipo="VWAP_OFICIAL",
                fornecedor=fonte or "FONTE_NAO_INFORMADA",
                campo_origem="VWAP_OFICIAL",
                timeframe_origem="SESSAO",
                valor=valor,
                status=status,
                motivo_status=motivo,
            ),
        )


class _ProvedorNivelExterno:
    nome = ""
    origem_tipo = ""
    campo_valor = ""
    campo_fonte = ""
    campo_confirmacao = ""
    campo_aplicabilidade = ""

    def localizar(
        self,
        payload: dict[str, Any],
        contexto: ContextoReferencia,
    ) -> Iterable[ReferenciaMercado]:
        valor = _decimal_positivo(payload.get(self.campo_valor))
        fonte = str(payload.get(self.campo_fonte) or "").strip().upper()
        confirmada = bool(payload.get(self.campo_confirmacao))

        aplicavel = True
        if self.campo_aplicabilidade:
            aplicavel = bool(payload.get(self.campo_aplicabilidade))

        status = "ATIVA"
        motivo = ""

        if not aplicavel:
            status = "BLOQUEADA"
            motivo = f"{self.origem_tipo}_NAO_APLICAVEL_AO_ATIVO"
        elif valor is None:
            status = "BLOQUEADA"
            motivo = f"{self.origem_tipo}_VALOR_INVALIDO"
        elif not fonte:
            status = "BLOQUEADA"
            motivo = f"{self.origem_tipo}_FONTE_NAO_INFORMADA"
        elif not confirmada:
            status = "BLOQUEADA"
            motivo = f"{self.origem_tipo}_ORIGEM_NAO_CONFIRMADA"

        return (
            FabricaReferencia.criar(
                contexto=contexto,
                origem_tipo=self.origem_tipo,
                fornecedor=fonte or "FONTE_NAO_INFORMADA",
                campo_origem=self.campo_valor.upper(),
                timeframe_origem="DIARIO",
                valor=valor,
                status=status,
                motivo_status=motivo,
            ),
        )


class ProvedorAjusteDiario(_ProvedorNivelExterno):
    nome = "AJUSTE_DIARIO"
    origem_tipo = "AJUSTE_DIARIO"
    campo_valor = "ajuste_diario"
    campo_fonte = "ajuste_fonte"
    campo_confirmacao = "ajuste_origem_confirmada"


class ProvedorPTAX(_ProvedorNivelExterno):
    nome = "PTAX"
    origem_tipo = "PTAX"
    campo_valor = "ptax"
    campo_fonte = "ptax_fonte"
    campo_confirmacao = "ptax_origem_confirmada"
    campo_aplicabilidade = "ptax_aplicavel_ao_ativo"


class _ProvedorNivelSessao:
    nome = ""
    origem_tipo = ""
    campo_valor = ""
    campo_fonte = ""
    campo_confirmacao = ""

    def localizar(
        self,
        payload: dict[str, Any],
        contexto: ContextoReferencia,
    ) -> Iterable[ReferenciaMercado]:
        valor = _decimal_positivo(payload.get(self.campo_valor))
        fonte = str(payload.get(self.campo_fonte) or "").strip().upper()
        confirmada = bool(payload.get(self.campo_confirmacao))

        status = "ATIVA"
        motivo = ""

        if valor is None:
            status = "BLOQUEADA"
            motivo = f"{self.origem_tipo}_VALOR_INVALIDO"
        elif not fonte:
            status = "BLOQUEADA"
            motivo = f"{self.origem_tipo}_FONTE_NAO_INFORMADA"
        elif not confirmada:
            status = "BLOQUEADA"
            motivo = f"{self.origem_tipo}_ORIGEM_NAO_CONFIRMADA"

        return (
            FabricaReferencia.criar(
                contexto=contexto,
                origem_tipo=self.origem_tipo,
                fornecedor=fonte or "FONTE_NAO_INFORMADA",
                campo_origem=self.campo_valor.upper(),
                timeframe_origem="SESSAO",
                valor=valor,
                status=status,
                motivo_status=motivo,
            ),
        )


class ProvedorAberturaSessao(_ProvedorNivelSessao):
    nome = "ABERTURA_SESSAO"
    origem_tipo = "ABERTURA_SESSAO"
    campo_valor = "abertura_sessao"
    campo_fonte = "abertura_fonte"
    campo_confirmacao = "abertura_origem_confirmada"


class ProvedorMaximaSessao(_ProvedorNivelSessao):
    nome = "MAXIMA_SESSAO"
    origem_tipo = "MAXIMA_SESSAO"
    campo_valor = "maxima_sessao"
    campo_fonte = "maxima_fonte"
    campo_confirmacao = "maxima_origem_confirmada"


class ProvedorMinimaSessao(_ProvedorNivelSessao):
    nome = "MINIMA_SESSAO"
    origem_tipo = "MINIMA_SESSAO"
    campo_valor = "minima_sessao"
    campo_fonte = "minima_fonte"
    campo_confirmacao = "minima_origem_confirmada"


class MotorRegioes:
    """
    Nucleo generico de referencias da RG-02A.

    O motor apenas localiza referencias. Ele nao gera entrada, stop,
    parcial, alvo, direcao, forca ou confianca.
    """

    def __init__(
        self,
        provedores: Optional[Iterable[ProvedorReferencia]] = None,
    ) -> None:
        self._provedores = tuple(
            provedores
            if provedores is not None
            else (
                ProvedorMilhar(),
                ProvedorVWAPOficial(),
                ProvedorAjusteDiario(),
                ProvedorPTAX(),
                ProvedorAberturaSessao(),
                ProvedorMaximaSessao(),
                ProvedorMinimaSessao(),
            )
        )

    def localizar(
        self,
        payload: dict[str, Any],
        contexto: ContextoReferencia,
    ) -> list[dict[str, Any]]:
        contexto.validar()

        referencias: list[dict[str, Any]] = []
        for provedor in self._provedores:
            for referencia in provedor.localizar(payload, contexto):
                referencias.append(referencia.para_dict())

        return referencias
