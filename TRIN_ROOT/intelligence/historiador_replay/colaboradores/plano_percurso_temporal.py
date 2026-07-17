from __future__ import annotations
from dataclasses import replace
from ..modelos_internos import PlanoPercursoTemporalV1
from ..util.hash_sha256 import sha256_bytes
from ..util.json_canonico import json_canonico_bytes

def calcular_plano_id(campos_sem_id: dict) -> str:
    return sha256_bytes(json_canonico_bytes(campos_sem_id))

def validar_plano_id(plano: PlanoPercursoTemporalV1) -> None:
    data = plano.como_dict(); recebido = data.pop("plano_id")
    if recebido != calcular_plano_id(data):
        from ..erros import FalhaReplay
        raise FalhaReplay("PLANO_ID_DIVERGENTE")
