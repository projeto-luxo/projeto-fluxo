from __future__ import annotations

import hashlib
import json
import math
from decimal import Decimal, InvalidOperation
from typing import Any

from .erros import FalhaConfluenciaReplay


def _validar_texto(texto: str) -> None:
    for char in texto:
        codigo = ord(char)
        if 0xD800 <= codigo <= 0xDFFF:
            raise FalhaConfluenciaReplay("JCS_SURROGATE_INVALIDO")


def _serializar_string(texto: str) -> str:
    _validar_texto(texto)
    return json.dumps(texto, ensure_ascii=False, separators=(",", ":"))


def _normalizar_expoente(texto: str) -> str:
    mantissa, expoente = texto.lower().split("e", 1)
    sinal = ""
    if expoente.startswith(("+", "-")):
        sinal, expoente = expoente[0], expoente[1:]
    expoente = expoente.lstrip("0") or "0"
    if sinal == "+":
        return f"{mantissa}e+{expoente}"
    if sinal == "-":
        return f"{mantissa}e-{expoente}"
    return f"{mantissa}e{expoente}"


def _serializar_float(valor: float) -> str:
    if not math.isfinite(valor):
        raise FalhaConfluenciaReplay("JCS_NUMERO_NAO_FINITO")
    if valor == 0:
        return "0"
    absoluto = abs(valor)
    texto = repr(valor)
    if 1e-6 <= absoluto < 1e21:
        decimal = Decimal(texto)
        fixo = format(decimal, "f")
        if "." in fixo:
            fixo = fixo.rstrip("0").rstrip(".")
        return fixo
    if "e" not in texto.lower():
        texto = format(Decimal(texto).normalize(), "e")
    mantissa, expoente = texto.lower().split("e", 1)
    if "." in mantissa:
        mantissa = mantissa.rstrip("0").rstrip(".")
    return _normalizar_expoente(f"{mantissa}e{expoente}")


def _serializar(valor: Any) -> str:
    if valor is None:
        return "null"
    if valor is True:
        return "true"
    if valor is False:
        return "false"
    if isinstance(valor, int) and not isinstance(valor, bool):
        return str(valor)
    if isinstance(valor, float):
        return _serializar_float(valor)
    if isinstance(valor, str):
        return _serializar_string(valor)
    if isinstance(valor, (list, tuple)):
        return "[" + ",".join(_serializar(item) for item in valor) + "]"
    if isinstance(valor, dict):
        for chave in valor:
            if not isinstance(chave, str):
                raise FalhaConfluenciaReplay("JCS_CHAVE_NAO_STRING")
            if not chave.isascii():
                raise FalhaConfluenciaReplay(
                    "JCS_CHAVE_NAO_ASCII",
                    "O contrato V1 restringe chaves a ASCII para ordenacao estavel.",
                )
        partes = []
        for chave in sorted(valor):
            partes.append(f"{_serializar_string(chave)}:{_serializar(valor[chave])}")
        return "{" + ",".join(partes) + "}"
    raise FalhaConfluenciaReplay(
        "JCS_TIPO_NAO_SUPORTADO",
        type(valor).__name__,
    )


def json_canonico_bytes(valor: Any) -> bytes:
    return _serializar(valor).encode("utf-8")


def sha256_canonico(valor: Any) -> str:
    return hashlib.sha256(json_canonico_bytes(valor)).hexdigest()


def sha256_bytes(valor: bytes) -> str:
    return hashlib.sha256(valor).hexdigest()
