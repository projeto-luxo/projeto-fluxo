from __future__ import annotations
import json
from pathlib import Path
from typing import Any
from jsonschema import Draft202012Validator, FormatChecker
from referencing import Registry, Resource
from .erros import GateReprovado, FalhaReplay

class ValidadorEstrutural:
    def __init__(self, schema_dir: Path) -> None:
        self.schema_dir = Path(schema_dir)
        schemas = {}
        registry = Registry()
        for path in sorted(self.schema_dir.glob("*.schema.json")):
            schema = json.loads(path.read_text(encoding="utf-8-sig"))
            Draft202012Validator.check_schema(schema)
            schemas[path.name] = schema
            registry = registry.with_resource(schema["$id"], Resource.from_contents(schema))
        esperados = {
            "CERTIFICACAO_FISCAL_REPLAY_V2_1.schema.json",
            "CONTEXTO_HISTORIADOR_REPLAY_V2_2.schema.json",
            "EVENTO_HISTORICO_PROFIT_9_COLUNAS_V1.schema.json",
            "EXPERIENCIA_REPLAY_V1.schema.json",
            "PACOTE_ENTRADA_HISTORIADOR_REPLAY_V2_1.schema.json",
            "RESPOSTA_GATE_HISTORIADOR_REPLAY_V1_2.schema.json",
            "TOKEN_RETOMADA_HISTORIADOR_REPLAY_V1.schema.json",
        }
        encontrados = set(schemas)
        if encontrados != esperados:
            ausentes = sorted(esperados - encontrados)
            extras = sorted(encontrados - esperados)
            raise ValueError(f"SCHEMAS_DIVERGENTES:ausentes={ausentes}:extras={extras}")
        self.validators = {name: Draft202012Validator(schema, registry=registry, format_checker=FormatChecker()) for name, schema in schemas.items()}
    def validar_gate(self, schema: str, valor: Any) -> None:
        try: self.validators[schema].validate(valor)
        except Exception as exc: raise GateReprovado("ESTRUTURA_INVALIDA", str(exc)) from exc
    def validar_replay(self, schema: str, valor: Any) -> None:
        try: self.validators[schema].validate(valor)
        except Exception as exc: raise FalhaReplay("ESTRUTURA_INVALIDA", str(exc)) from exc
    def validar_bruto(self, schema: str, valor: Any) -> None:
        self.validators[schema].validate(valor)
