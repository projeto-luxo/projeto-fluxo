from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from enum import StrEnum
from typing import Any, Iterator, Mapping

from .erros import FalhaReplay
from .util.hash_sha256 import sha256_bytes
from .util.json_canonico import json_canonico_bytes


class EstadoReplay(StrEnum):
    NAO_INICIADO = "NAO_INICIADO"
    GATE_REPROVADO = "GATE_REPROVADO"
    PRONTO = "PRONTO"
    EM_CURSO = "EM_CURSO"
    PAUSADO = "PAUSADO"
    CONCLUIDO = "CONCLUIDO"
    CONCLUIDO_PARCIAL = "CONCLUIDO_PARCIAL"
    FALHA = "FALHA"


@dataclass(frozen=True)
class FingerprintFonte:
    origem_id: str
    tamanho: int
    sha256: str
    identidade_sistema: str
    fonte_selada_id: str


@dataclass(frozen=True)
class PlanoPercursoTemporalV1:
    plano_id: str
    origem_id: str
    origem_hash: str
    fonte_selada_id: str
    contrato_temporal_id: str
    contrato_temporal_versao: str
    contrato_temporal_hash: str
    ordem_fisica: str
    estrategia_leitura: str
    periodo_solicitado: dict[str, str]
    inicio_elegivel: str
    fim_elegivel: str
    primeiro_offset: int
    ultimo_offset: int
    total_linhas_fisicas: int
    total_eventos_elegiveis: int
    primeiro_timestamp: str
    ultimo_timestamp: str
    tamanho_bloco: int
    resultado_inspecao: str
    motivo_reprovacao: str | None

    def como_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class EnvelopeExecucaoAprovada(Mapping[str, Any]):
    """Envelope imutável entre gate e núcleo.

    Os objetos contratuais são armazenados como bytes JSON canônicos. Qualquer
    alteração exige reconstruir outro envelope e será revalidada pelo núcleo.
    """

    pacote_canonico: bytes
    gate_canonico: bytes
    pacote_sha256: str
    gate_sha256: str
    solicitacao_id: str
    gate_id: str
    pacote_id: str

    @classmethod
    def criar(cls, pacote: dict[str, Any], gate: dict[str, Any]) -> "EnvelopeExecucaoAprovada":
        pacote_bytes = json_canonico_bytes(pacote)
        gate_bytes = json_canonico_bytes(gate)
        return cls(
            pacote_canonico=pacote_bytes,
            gate_canonico=gate_bytes,
            pacote_sha256=sha256_bytes(pacote_bytes),
            gate_sha256=sha256_bytes(gate_bytes),
            solicitacao_id=gate["solicitacao_id"],
            gate_id=gate["gate_id"],
            pacote_id=pacote["pacote_id"],
        )

    def verificar_integridade(self) -> None:
        if sha256_bytes(self.pacote_canonico) != self.pacote_sha256:
            raise FalhaReplay("ENVELOPE_PACOTE_HASH_DIVERGENTE")
        if sha256_bytes(self.gate_canonico) != self.gate_sha256:
            raise FalhaReplay("ENVELOPE_GATE_HASH_DIVERGENTE")
        pacote = self.pacote_dict()
        gate = self.gate_dict()
        if pacote.get("pacote_id") != self.pacote_id:
            raise FalhaReplay("ENVELOPE_PACOTE_ID_DIVERGENTE")
        if gate.get("gate_id") != self.gate_id:
            raise FalhaReplay("ENVELOPE_GATE_ID_DIVERGENTE")
        if gate.get("solicitacao_id") != self.solicitacao_id:
            raise FalhaReplay("ENVELOPE_SOLICITACAO_ID_DIVERGENTE")

    def pacote_dict(self) -> dict[str, Any]:
        return json.loads(self.pacote_canonico.decode("utf-8"))

    def gate_dict(self) -> dict[str, Any]:
        return json.loads(self.gate_canonico.decode("utf-8"))

    def __getitem__(self, key: str) -> Any:
        return self.pacote_dict()[key]

    def __iter__(self) -> Iterator[str]:
        return iter(self.pacote_dict())

    def __len__(self) -> int:
        return len(self.pacote_dict())

    def __deepcopy__(self, memo: dict[int, object]) -> "EnvelopeExecucaoAprovada":
        return self
