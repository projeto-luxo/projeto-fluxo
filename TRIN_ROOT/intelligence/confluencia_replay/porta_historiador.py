from __future__ import annotations

import copy
from dataclasses import dataclass
from typing import Any, Iterable, Mapping, Protocol

from .erros import FalhaConfluenciaReplay


class RepositorioExperienciasProtocol(Protocol):
    def consultar_experiencias(
        self,
        origem_id: str | None = None,
        direcao: str | None = None,
    ) -> list[dict[str, Any]]:
        ...


@dataclass(frozen=True)
class ResultadoPorta:
    experiencias: tuple[dict[str, Any], ...]
    metodo: str
    origem_id: str | None
    direcao: None


class PortaHistoriadorConfluenciaV1:
    """Porta estritamente somente leitura sobre a API homologada.

    A porta não recebe caminhos, não acessa CSV e não possui métodos de escrita.
    """

    def __init__(self, repositorio: RepositorioExperienciasProtocol) -> None:
        metodo = getattr(repositorio, "consultar_experiencias", None)
        if not callable(metodo):
            raise FalhaConfluenciaReplay(
                "PORTA_HISTORIADOR_API_INCOMPATIVEL",
                "consultar_experiencias ausente",
            )
        proibidos = (
            "registrar",
            "registrar_experiencia",
            "salvar",
            "atualizar",
            "excluir",
            "compactar",
        )
        self._repositorio = repositorio
        self._metodos_escrita_detectados = tuple(
            nome for nome in proibidos if callable(getattr(repositorio, nome, None))
        )

    @property
    def metodos_escrita_detectados(self) -> tuple[str, ...]:
        # A existência de métodos no fornecedor não autoriza seu uso.
        return self._metodos_escrita_detectados

    def consultar(self, origem_id: str | None) -> ResultadoPorta:
        try:
            bruto = self._repositorio.consultar_experiencias(
                origem_id=origem_id,
                direcao=None,
            )
        except TypeError as exc:
            raise FalhaConfluenciaReplay(
                "PORTA_HISTORIADOR_ASSINATURA_INCOMPATIVEL",
                "A chamada oficial exige origem_id e direcao=None.",
            ) from exc
        except Exception as exc:
            raise FalhaConfluenciaReplay(
                "PORTA_HISTORIADOR_FALHA_CONSULTA",
                str(exc),
            ) from exc
        if not isinstance(bruto, list):
            raise FalhaConfluenciaReplay(
                "PORTA_HISTORIADOR_RETORNO_INVALIDO",
                type(bruto).__name__,
            )
        experiencias: list[dict[str, Any]] = []
        for indice, item in enumerate(bruto):
            if not isinstance(item, Mapping):
                raise FalhaConfluenciaReplay(
                    "PORTA_HISTORIADOR_ITEM_INVALIDO",
                    str(indice),
                )
            # O repositório homologado pode devolver a experiência diretamente
            # ou um envelope append-only com a chave "experiencia".
            experiencia = item.get("experiencia") if "experiencia" in item else item
            if not isinstance(experiencia, Mapping):
                raise FalhaConfluenciaReplay(
                    "PORTA_HISTORIADOR_EXPERIENCIA_INVALIDA",
                    str(indice),
                )
            experiencia_copia = copy.deepcopy(dict(experiencia))
            if origem_id is not None and experiencia_copia.get("origem_id") != origem_id:
                raise FalhaConfluenciaReplay(
                    "PORTA_HISTORIADOR_ORIGEM_DIVERGENTE",
                    f"esperada={origem_id};recebida={experiencia_copia.get('origem_id')}",
                )
            experiencias.append(experiencia_copia)
        return ResultadoPorta(
            experiencias=tuple(experiencias),
            metodo="RepositorioExperiencias.consultar_experiencias",
            origem_id=origem_id,
            direcao=None,
        )
