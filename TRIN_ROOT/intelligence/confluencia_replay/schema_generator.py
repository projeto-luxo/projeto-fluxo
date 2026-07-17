from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

from .canonico import sha256_bytes
from .erros import FalhaConfluenciaReplay


def _count_branch(n: int) -> dict[str, Any]:
    return {
        "properties": {
            "quantidade_experiencias": {"const": n},
            "ids_experiencias": {"minItems": n, "maxItems": n},
            "evidencias": {"minItems": n, "maxItems": n},
        }
    }


def _comparable_count_branch(n: int) -> dict[str, Any]:
    return {
        "properties": {
            "confianca_diagnostica": {
                "properties": {
                    "quantidade_comparaveis": {"const": n},
                    "ids_comparaveis": {"minItems": n, "maxItems": n},
                }
            }
        }
    }


def gerar_schema_de_base(base: dict[str, Any]) -> dict[str, Any]:
    schema = copy.deepcopy(base)
    config = schema.pop("x-trin-generated-constraints", None)
    if not isinstance(config, dict):
        raise FalhaConfluenciaReplay("SCHEMA_BASE_SEM_CONFIG_GERACAO")
    q = config.get("quantidade_experiencias")
    c = config.get("quantidade_comparaveis")
    if q != {"min": 0, "max": 1000} or c != {"min": 0, "max": 1000}:
        raise FalhaConfluenciaReplay("SCHEMA_BASE_CONFIG_GERACAO_DIVERGENTE")
    all_of = schema.get("allOf")
    if not isinstance(all_of, list):
        raise FalhaConfluenciaReplay("SCHEMA_BASE_ALLOF_INVALIDO")
    gerados = [
        {"oneOf": [_count_branch(n) for n in range(0, 1001)]},
        {"oneOf": [_comparable_count_branch(n) for n in range(0, 1001)]},
    ]
    schema["allOf"] = gerados + all_of
    return schema


def serializar_schema(schema: dict[str, Any]) -> bytes:
    return (json.dumps(schema, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def caminhos_padrao() -> tuple[Path, Path]:
    trin_root = Path(__file__).resolve().parents[2]
    contratos = trin_root / "governance" / "08_CONTRATOS"
    return (
        contratos / "CONFLUENCIA_REPLAY_V1.schema.base.json",
        contratos / "CONFLUENCIA_REPLAY_V1.schema.json",
    )


def reproduzir_schema(
    base_path: str | Path | None = None,
    destino_path: str | Path | None = None,
) -> dict[str, Any]:
    base_padrao, destino_padrao = caminhos_padrao()
    base_arquivo = Path(base_path) if base_path is not None else base_padrao
    destino_arquivo = Path(destino_path) if destino_path is not None else destino_padrao
    base = json.loads(base_arquivo.read_text(encoding="utf-8"))
    schema = gerar_schema_de_base(base)
    destino_arquivo.parent.mkdir(parents=True, exist_ok=True)
    destino_arquivo.write_bytes(serializar_schema(schema))
    return schema


def verificar_reproducao(
    base_path: str | Path | None = None,
    esperado_path: str | Path | None = None,
) -> dict[str, Any]:
    base_padrao, esperado_padrao = caminhos_padrao()
    base_arquivo = Path(base_path) if base_path is not None else base_padrao
    esperado_arquivo = Path(esperado_path) if esperado_path is not None else esperado_padrao
    base = json.loads(base_arquivo.read_text(encoding="utf-8"))
    gerado = serializar_schema(gerar_schema_de_base(base))
    esperado = esperado_arquivo.read_bytes()
    return {
        "reproduzido": gerado == esperado,
        "sha256_gerado": sha256_bytes(gerado),
        "sha256_esperado": sha256_bytes(esperado),
        "tamanho_gerado": len(gerado),
        "tamanho_esperado": len(esperado),
    }


if __name__ == "__main__":
    resultado = verificar_reproducao()
    print(json.dumps(resultado, ensure_ascii=False, indent=2))
    raise SystemExit(0 if resultado["reproduzido"] else 17)
