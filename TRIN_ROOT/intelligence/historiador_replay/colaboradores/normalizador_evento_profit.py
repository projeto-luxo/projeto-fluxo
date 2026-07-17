from __future__ import annotations
import re
from datetime import datetime
from zoneinfo import ZoneInfo
from ..erros import FalhaReplay

_DECIMAL = re.compile(r"^[+-]?(?:0|[1-9]\d*)(?:[.,]\d+)?$")
_INTEIRO = re.compile(r"^(?:0|[1-9]\d*)$")

class NormalizadorEventoProfitV1:
    COLUNAS = ("ativo","data","hora","abertura","maximo","minimo","ultimo","volume","volume_quantidade")

    @staticmethod
    def decimal(valor: str, *, inteiro: bool = False, negativo: bool = True) -> str:
        text = valor.strip()
        pattern = _INTEIRO if inteiro else _DECIMAL
        if not pattern.fullmatch(text):
            raise FalhaReplay("VALOR_NUMERICO_INVALIDO", valor)
        if not negativo and text.startswith("-"):
            raise FalhaReplay("VALOR_NEGATIVO_PROIBIDO", valor)
        if text.startswith("+"):
            text = text[1:]
        text = text.replace(",", ".")
        return text

    def normalizar(self, raw: bytes) -> dict:
        try:
            text = raw.decode("utf-8-sig").rstrip("\r\n")
        except UnicodeDecodeError as exc:
            raise FalhaReplay("ENCODING_INVALIDO") from exc
        parts = text.split(";")
        if len(parts) != 9:
            raise FalhaReplay("QUANTIDADE_COLUNAS_INVALIDA", str(len(parts)))
        data = dict(zip(self.COLUNAS, parts))
        if data["ativo"] != "WINFUT":
            raise FalhaReplay("ATIVO_DIVERGENTE", data["ativo"])
        try:
            naive = datetime.strptime(f"{data['data']} {data['hora']}", "%d/%m/%Y %H:%M:%S")
        except ValueError as exc:
            raise FalhaReplay("TIMESTAMP_INVALIDO") from exc
        timestamp = naive.replace(tzinfo=ZoneInfo("America/Sao_Paulo")).isoformat()
        return {
            "ativo": data["ativo"], "data": data["data"], "hora": data["hora"], "timestamp": timestamp,
            "abertura": self.decimal(data["abertura"]), "maximo": self.decimal(data["maximo"]),
            "minimo": self.decimal(data["minimo"]), "ultimo": self.decimal(data["ultimo"]),
            "volume": self.decimal(data["volume"], negativo=False),
            "volume_quantidade": self.decimal(data["volume_quantidade"], inteiro=True, negativo=False),
        }
