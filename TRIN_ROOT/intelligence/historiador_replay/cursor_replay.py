from __future__ import annotations

from copy import deepcopy

from .erros import FalhaReplay
from .util.hash_sha256 import sha256_bytes
from .util.json_canonico import json_canonico_bytes


class CursorReplay:
    VERSAO_TOKEN = "2.0.0"
    TOKEN_SCHEMA = "TOKEN_RETOMADA_HISTORIADOR_REPLAY_V1.schema.json"

    def __init__(self, origem_hash: str, periodo: dict, politica: str, tamanho_janela: int, total_eventos: int, estrutural=None) -> None:
        self.origem_hash = origem_hash
        self.periodo = deepcopy(periodo)
        self.politica = politica
        self.tamanho_janela = tamanho_janela
        self.total_eventos = total_eventos
        self.estrutural = estrutural

    def cursor(self, ordinal: int) -> str:
        if ordinal < 1 or ordinal > self.total_eventos:
            raise FalhaReplay("ORDINAL_FORA_DA_FAIXA")
        return f"{self.origem_hash}:{ordinal}"

    def proximo(self, ordinal: int) -> str | None:
        return None if ordinal >= self.total_eventos else self.cursor(ordinal + 1)

    @staticmethod
    def calcular_token_id(body: dict) -> str:
        return sha256_bytes(json_canonico_bytes(body))

    def criar_token(self, proximo_ordinal: int, ultimo_timestamp: str) -> dict:
        if proximo_ordinal < 2 or proximo_ordinal > self.total_eventos:
            raise FalhaReplay("PROXIMO_ORDINAL_INVALIDO")
        body = {
            "origem_hash": self.origem_hash,
            "periodo_solicitado": deepcopy(self.periodo),
            "politica_cobertura": self.politica,
            "tamanho_janela": self.tamanho_janela,
            "proximo_ordinal": proximo_ordinal,
            "ultimo_timestamp_entregue": ultimo_timestamp,
            "versao_contrato": self.VERSAO_TOKEN,
        }
        return {"token_id": self.calcular_token_id(body), **body}

    def validar_token(self, token: dict) -> int:
        if self.estrutural is None:
            raise FalhaReplay("VALIDADOR_TOKEN_AUSENTE")
        self.estrutural.validar_replay(self.TOKEN_SCHEMA, token)
        body = {key: deepcopy(value) for key, value in token.items() if key != "token_id"}
        if token["token_id"] != self.calcular_token_id(body):
            raise FalhaReplay("TOKEN_ID_DIVERGENTE")
        expected = {
            "origem_hash": self.origem_hash,
            "periodo_solicitado": self.periodo,
            "politica_cobertura": self.politica,
            "tamanho_janela": self.tamanho_janela,
            "versao_contrato": self.VERSAO_TOKEN,
        }
        for key, value in expected.items():
            if token[key] != value:
                raise FalhaReplay(f"TOKEN_{key.upper()}_DIVERGENTE")
        ordinal = token["proximo_ordinal"]
        if not (2 <= ordinal <= self.total_eventos):
            raise FalhaReplay("TOKEN_ORDINAL_INVALIDO")
        return ordinal

    @staticmethod
    def validar_timestamp_anterior(token: dict, timestamp_anterior: str | None) -> None:
        if timestamp_anterior is None:
            raise FalhaReplay("TOKEN_SEM_EVENTO_ANTERIOR")
        if token["ultimo_timestamp_entregue"] != timestamp_anterior:
            raise FalhaReplay("TOKEN_ULTIMO_TIMESTAMP_DIVERGENTE")
