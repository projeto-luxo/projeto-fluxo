from __future__ import annotations

from dataclasses import asdict, dataclass
from decimal import Decimal, InvalidOperation
from typing import Any, Iterable

USO_OPERACIONAL = "BLOQUEADO"
VERSAO_REGRA = "0.1"


def _decimal(valor: Any) -> Decimal | None:
    try:
        numero = Decimal(str(valor))
    except (InvalidOperation, TypeError, ValueError):
        return None
    if not numero.is_finite():
        return None
    return numero


def _normalizar(valor: Decimal) -> str:
    return format(valor.quantize(Decimal("0.01")), "f")


def _texto(valor: Any) -> str:
    return str(valor or "").strip()


@dataclass(frozen=True)
class RegiaoComposta:
    chave_regiao: str
    ativo: str
    contrato: str
    data_referencia: str
    sessao_referencia: str
    limite_inferior: float
    limite_superior: float
    classificacao: str
    status_classificacao: str
    status: str
    quantidade_origens: int
    origens: tuple[dict[str, Any], ...]
    uso_operacional: str
    versao_regra: str

    def para_dict(self) -> dict[str, Any]:
        dados = asdict(self)
        dados["origens"] = [dict(item) for item in self.origens]
        return dados


class AgregadorRegioesRG02B:
    """Agrupa apenas referências ATIVAS com limites exatamente iguais."""

    def __init__(self, versao_regra: str = VERSAO_REGRA) -> None:
        self.versao_regra = versao_regra

    @staticmethod
    def _origem(referencia: dict[str, Any]) -> dict[str, Any]:
        campos = (
            "chave_referencia",
            "origem_tipo",
            "fornecedor",
            "campo_origem",
            "timeframe_origem",
            "limite_inferior",
            "limite_superior",
            "status",
            "status_certificacao",
            "data_referencia",
            "sessao_referencia",
        )
        return {campo: referencia.get(campo) for campo in campos}

    def _chave(
        self,
        *,
        ativo: str,
        contrato: str,
        data_referencia: str,
        sessao_referencia: str,
        inferior: Decimal,
        superior: Decimal,
    ) -> str:
        return "|".join(
            (
                "REGIAO",
                ativo.upper(),
                contrato.upper(),
                data_referencia,
                sessao_referencia.upper(),
                _normalizar(inferior),
                _normalizar(superior),
                self.versao_regra,
            )
        )

    def agregar(
        self,
        referencias: Iterable[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        grupos: dict[tuple[str, ...], dict[str, Any]] = {}

        for referencia in referencias:
            if _texto(referencia.get("status")).upper() != "ATIVA":
                continue

            inferior = _decimal(referencia.get("limite_inferior"))
            superior = _decimal(referencia.get("limite_superior"))
            if inferior is None or superior is None:
                continue

            ativo = _texto(referencia.get("ativo")).upper()
            contrato = _texto(referencia.get("contrato")).upper()
            data_ref = _texto(referencia.get("data_referencia"))
            sessao = _texto(referencia.get("sessao_referencia")).upper()

            if not all((ativo, contrato, data_ref, sessao)):
                continue

            chave_grupo = (
                ativo,
                contrato,
                data_ref,
                sessao,
                _normalizar(inferior),
                _normalizar(superior),
            )

            grupo = grupos.setdefault(
                chave_grupo,
                {
                    "ativo": ativo,
                    "contrato": contrato,
                    "data_referencia": data_ref,
                    "sessao_referencia": sessao,
                    "inferior": inferior,
                    "superior": superior,
                    "origens": {},
                },
            )

            origem = self._origem(referencia)
            chave_origem = _texto(origem.get("chave_referencia")) or "|".join(
                (
                    _texto(origem.get("origem_tipo")),
                    _texto(origem.get("fornecedor")),
                    _texto(origem.get("campo_origem")),
                    _normalizar(inferior),
                    _normalizar(superior),
                )
            )
            grupo["origens"][chave_origem] = origem

        regioes: list[RegiaoComposta] = []

        for chave_grupo in sorted(grupos):
            grupo = grupos[chave_grupo]
            origens = tuple(
                grupo["origens"][chave]
                for chave in sorted(grupo["origens"])
            )
            regioes.append(
                RegiaoComposta(
                    chave_regiao=self._chave(
                        ativo=grupo["ativo"],
                        contrato=grupo["contrato"],
                        data_referencia=grupo["data_referencia"],
                        sessao_referencia=grupo["sessao_referencia"],
                        inferior=grupo["inferior"],
                        superior=grupo["superior"],
                    ),
                    ativo=grupo["ativo"],
                    contrato=grupo["contrato"],
                    data_referencia=grupo["data_referencia"],
                    sessao_referencia=grupo["sessao_referencia"],
                    limite_inferior=float(grupo["inferior"]),
                    limite_superior=float(grupo["superior"]),
                    classificacao="NAO_CLASSIFICADA",
                    status_classificacao="NAO_AVALIADA",
                    status="CANDIDATA",
                    quantidade_origens=len(origens),
                    origens=origens,
                    uso_operacional=USO_OPERACIONAL,
                    versao_regra=self.versao_regra,
                )
            )

        return [regiao.para_dict() for regiao in regioes]
