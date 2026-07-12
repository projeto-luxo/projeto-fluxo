from __future__ import annotations

import csv
from dataclasses import asdict, dataclass
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any, Optional


STATUS_OFICIAIS = frozenset(
    {
        "OFICIAL",
        "REFERENCIA_OFICIAL_VALIDADA",
    }
)


def _decimal_positivo(valor: Any) -> Optional[Decimal]:
    try:
        numero = Decimal(str(valor).strip().replace(",", "."))
    except (InvalidOperation, AttributeError, TypeError, ValueError):
        return None

    if not numero.is_finite() or numero <= 0:
        return None

    return numero


def _texto(valor: Any) -> str:
    return str(valor or "").strip()


@dataclass(frozen=True)
class ReferenciasDiariasPayload:
    ajuste_diario: Optional[float]
    ajuste_fonte: str
    ajuste_origem_confirmada: bool
    ptax: Optional[float]
    ptax_fonte: str
    ptax_origem_confirmada: bool
    ptax_aplicavel_ao_ativo: bool
    referencias_diarias_status: str
    referencias_diarias_motivo: str

    def para_dict(self) -> dict[str, Any]:
        return asdict(self)


class ReferenciasMercadoConfig:
    """
    Leitor operacional de Ajuste Diário e PTAX.

    Não calcula, estima ou inventa valores. Uma referência só é confirmada
    quando existe linha da data, ativo/contrato compatíveis, fonte declarada
    e status oficial.
    """

    def __init__(self, caminho: str | Path) -> None:
        self.caminho = Path(caminho)

    @staticmethod
    def _fonte(linha: dict[str, str]) -> str:
        primaria = _texto(linha.get("fonte_primaria")).upper()
        operacional = _texto(linha.get("fonte_operacional")).upper()

        if primaria and operacional:
            return f"{primaria}|{operacional}"
        return primaria or operacional or "FONTE_NAO_INFORMADA"

    @staticmethod
    def _ptax_aplicavel(ativo: str, contrato: str) -> bool:
        codigo = f"{ativo} {contrato}".upper()
        return any(prefixo in codigo for prefixo in ("WDO", "DOL"))

    def _ler_linhas(self) -> list[dict[str, str]]:
        if not self.caminho.exists():
            return []

        with self.caminho.open(
            "r",
            encoding="utf-8-sig",
            newline="",
        ) as arquivo:
            return list(csv.DictReader(arquivo, delimiter=";"))

    def carregar(
        self,
        *,
        ativo: str,
        contrato: str,
        data_referencia: str,
    ) -> dict[str, Any]:
        ativo_norm = _texto(ativo).upper()
        contrato_norm = _texto(contrato).upper()
        data_norm = _texto(data_referencia)

        linhas = self._ler_linhas()

        candidatas = [
            linha
            for linha in linhas
            if _texto(linha.get("data_referencia")) == data_norm
            and _texto(linha.get("ativo")).upper() == ativo_norm
        ]

        linha_exata = next(
            (
                linha
                for linha in candidatas
                if _texto(linha.get("contrato")).upper() == contrato_norm
            ),
            None,
        )

        linha_ativo = next(
            (
                linha
                for linha in candidatas
                if not _texto(linha.get("contrato"))
            ),
            None,
        )

        linha_ajuste = linha_exata
        linha_ptax = linha_exata or linha_ativo

        if linha_ajuste is None and linha_ptax is None:
            return ReferenciasDiariasPayload(
                ajuste_diario=None,
                ajuste_fonte="FONTE_NAO_INFORMADA",
                ajuste_origem_confirmada=False,
                ptax=None,
                ptax_fonte="FONTE_NAO_INFORMADA",
                ptax_origem_confirmada=False,
                ptax_aplicavel_ao_ativo=self._ptax_aplicavel(
                    ativo_norm,
                    contrato_norm,
                ),
                referencias_diarias_status="BLOQUEADA",
                referencias_diarias_motivo="REFERENCIA_DIARIA_NAO_ENCONTRADA",
            ).para_dict()

        ajuste = (
            _decimal_positivo(linha_ajuste.get("preco_ajuste"))
            if linha_ajuste
            else None
        )
        ptax = (
            _decimal_positivo(linha_ptax.get("ptax_referencia"))
            if linha_ptax
            else None
        )

        status_ajuste = (
            _texto(linha_ajuste.get("status_referencia")).upper()
            if linha_ajuste
            else ""
        )
        status_ptax = (
            _texto(linha_ptax.get("status_referencia")).upper()
            if linha_ptax
            else ""
        )

        fonte_ajuste = (
            self._fonte(linha_ajuste)
            if linha_ajuste
            else "FONTE_NAO_INFORMADA"
        )
        fonte_ptax = (
            self._fonte(linha_ptax)
            if linha_ptax
            else "FONTE_NAO_INFORMADA"
        )

        ajuste_confirmado = bool(
            linha_ajuste
            and ajuste is not None
            and status_ajuste in STATUS_OFICIAIS
            and fonte_ajuste != "FONTE_NAO_INFORMADA"
        )

        ptax_aplicavel = self._ptax_aplicavel(
            ativo_norm,
            contrato_norm,
        )
        ptax_confirmada = bool(
            linha_ptax
            and ptax is not None
            and ptax_aplicavel
            and status_ptax in STATUS_OFICIAIS
            and fonte_ptax != "FONTE_NAO_INFORMADA"
        )

        motivos = []
        if not ajuste_confirmado:
            motivos.append("AJUSTE_NAO_CONFIRMADO")
        if ptax_aplicavel and not ptax_confirmada:
            motivos.append("PTAX_NAO_CONFIRMADA")

        return ReferenciasDiariasPayload(
            ajuste_diario=float(ajuste) if ajuste is not None else None,
            ajuste_fonte=fonte_ajuste,
            ajuste_origem_confirmada=ajuste_confirmado,
            ptax=float(ptax) if ptax is not None else None,
            ptax_fonte=fonte_ptax,
            ptax_origem_confirmada=ptax_confirmada,
            ptax_aplicavel_ao_ativo=ptax_aplicavel,
            referencias_diarias_status=(
                "ATIVA"
                if ajuste_confirmado or ptax_confirmada
                else "BLOQUEADA"
            ),
            referencias_diarias_motivo="|".join(motivos),
        ).para_dict()
