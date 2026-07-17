from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from .canonico import sha256_canonico
from .erros import FalhaConfluenciaReplay
from .util import parse_timestamp

ORIGEM_REPLAY = "ORIGEM_REPLAY"
VERSAO_EXPERIENCIA = "1.0.0"
CONTRATO_EXPERIENCIA = "ExperienciaReplayV1"


@dataclass(frozen=True)
class ExperienciaProjetada:
    experiencia: dict[str, Any]
    experiencia_id: str
    experiencia_sha256: str
    origem_id: str
    origem_hash: str
    solicitacao_id: str
    timestamp_referencia: str
    ordinal_referencia: int

    @property
    def chave_ordenacao(self) -> tuple[Any, int, str]:
        return (
            parse_timestamp(self.timestamp_referencia, "timestamp_referencia"),
            self.ordinal_referencia,
            self.experiencia_id,
        )


def _validar_id_experiencia(valor: Any) -> str:
    if (
        not isinstance(valor, str)
        or len(valor) != 64
        or any(c not in "0123456789abcdef" for c in valor)
    ):
        raise FalhaConfluenciaReplay("EXPERIENCIA_ID_INVALIDO")
    return valor


def validar_experiencia_minima(valor: Mapping[str, Any]) -> ExperienciaProjetada:
    obrigatorios = (
        "experiencia_id",
        "contrato",
        "versao",
        "origem_tipo",
        "solicitacao_id",
        "origem_id",
        "origem_hash",
        "timestamp_referencia",
        "ordinal_referencia",
        "fato",
        "contexto",
        "hipotese",
        "resultado",
    )
    faltantes = [campo for campo in obrigatorios if campo not in valor]
    if faltantes:
        raise FalhaConfluenciaReplay(
            "EXPERIENCIA_SCHEMA_INCOMPLETO",
            ",".join(faltantes),
            experiencia_id=str(valor.get("experiencia_id") or "") or None,
        )

    experiencia_id = _validar_id_experiencia(valor["experiencia_id"])

    if valor["contrato"] != CONTRATO_EXPERIENCIA:
        raise FalhaConfluenciaReplay(
            "EXPERIENCIA_CONTRATO_DESCONHECIDO",
            str(valor["contrato"]),
            experiencia_id=experiencia_id,
        )
    if valor["versao"] != VERSAO_EXPERIENCIA:
        raise FalhaConfluenciaReplay(
            "EXPERIENCIA_VERSAO_DESCONHECIDA",
            str(valor["versao"]),
            experiencia_id=experiencia_id,
        )
    if valor["origem_tipo"] != ORIGEM_REPLAY:
        raise FalhaConfluenciaReplay(
            "EXPERIENCIA_ORIGEM_INVALIDA",
            str(valor["origem_tipo"]),
            experiencia_id=experiencia_id,
        )

    for campo in ("solicitacao_id", "origem_id"):
        if not isinstance(valor[campo], str) or not valor[campo]:
            raise FalhaConfluenciaReplay(
                "EXPERIENCIA_RASTREABILIDADE_INCOMPLETA",
                campo,
                experiencia_id=experiencia_id,
            )

    origem_hash = valor["origem_hash"]
    if (
        not isinstance(origem_hash, str)
        or len(origem_hash) != 64
        or any(c not in "0123456789abcdef" for c in origem_hash)
    ):
        raise FalhaConfluenciaReplay(
            "EXPERIENCIA_ORIGEM_HASH_INVALIDO",
            experiencia_id=experiencia_id,
        )

    ordinal = valor["ordinal_referencia"]
    if not isinstance(ordinal, int) or isinstance(ordinal, bool) or ordinal < 1:
        raise FalhaConfluenciaReplay(
            "EXPERIENCIA_ORDINAL_INVALIDO",
            experiencia_id=experiencia_id,
        )

    timestamp = valor["timestamp_referencia"]
    parse_timestamp(timestamp, "timestamp_referencia")

    for campo in ("fato", "contexto", "hipotese", "resultado"):
        if not isinstance(valor[campo], Mapping):
            raise FalhaConfluenciaReplay(
                "EXPERIENCIA_COMPARTIMENTO_INVALIDO",
                campo,
                experiencia_id=experiencia_id,
            )

    hipotese = valor["hipotese"]
    if hipotese.get("direcao") not in (None, "COMPRA", "VENDA"):
        raise FalhaConfluenciaReplay(
            "DIRECAO_INVALIDA",
            experiencia_id=experiencia_id,
        )
    if hipotese.get("direcao_inventada") is not False:
        raise FalhaConfluenciaReplay(
            "DIRECAO_INVENTADA",
            experiencia_id=experiencia_id,
        )

    corpo = dict(valor)
    corpo.pop("experiencia_id", None)
    if sha256_canonico(corpo) != experiencia_id:
        raise FalhaConfluenciaReplay(
            "EXPERIENCIA_ID_DIVERGENTE",
            experiencia_id=experiencia_id,
        )

    experiencia = dict(valor)
    return ExperienciaProjetada(
        experiencia=experiencia,
        experiencia_id=experiencia_id,
        experiencia_sha256=sha256_canonico(experiencia),
        origem_id=str(valor["origem_id"]),
        origem_hash=origem_hash,
        solicitacao_id=str(valor["solicitacao_id"]),
        timestamp_referencia=str(timestamp),
        ordinal_referencia=int(ordinal),
    )
