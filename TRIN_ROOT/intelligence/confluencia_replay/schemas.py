from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

from .erros import FalhaConfluenciaReplay


def _contratos_dir() -> Path:
    trin_root = Path(__file__).resolve().parents[2]
    return trin_root / "governance" / "08_CONTRATOS"


@lru_cache(maxsize=2)
def carregar_schema(nome: str) -> dict[str, Any]:
    permitido = {
        "consulta": "CONSULTA_CONFLUENCIA_REPLAY_V1.schema.json",
        "saida": "CONFLUENCIA_REPLAY_V1.schema.json",
    }
    if nome not in permitido:
        raise FalhaConfluenciaReplay("SCHEMA_DESCONHECIDO", nome)
    caminho = _contratos_dir() / permitido[nome]
    try:
        schema = json.loads(caminho.read_text(encoding="utf-8"))
    except Exception as exc:
        raise FalhaConfluenciaReplay("SCHEMA_INDISPONIVEL", str(caminho)) from exc
    try:
        Draft202012Validator.check_schema(schema)
    except Exception as exc:
        raise FalhaConfluenciaReplay("SCHEMA_META_INVALIDO", nome) from exc
    return schema


@lru_cache(maxsize=2)
def _validator(nome: str) -> Draft202012Validator:
    return Draft202012Validator(
        carregar_schema(nome),
        format_checker=FormatChecker(),
    )


def erros_schema(nome: str, documento: Any) -> list[str]:
    erros = sorted(
        _validator(nome).iter_errors(documento),
        key=lambda erro: tuple(str(item) for item in erro.absolute_path),
    )
    saida: list[str] = []
    for erro in erros:
        caminho = ".".join(str(item) for item in erro.absolute_path) or "$"
        saida.append(f"{caminho}: {erro.message}")
    return saida


def validar_schema(nome: str, documento: Any) -> None:
    erros = erros_schema(nome, documento)
    if erros:
        raise FalhaConfluenciaReplay(
            f"SCHEMA_{nome.upper()}_INVALIDO",
            " | ".join(erros[:10]),
        )
