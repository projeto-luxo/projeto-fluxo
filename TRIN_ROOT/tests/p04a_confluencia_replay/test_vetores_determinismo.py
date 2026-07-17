from __future__ import annotations

import json
from pathlib import Path

from intelligence.confluencia_replay.canonico import sha256_canonico


def _vetores():
    trin_root = Path(__file__).resolve().parents[2]
    caminho = trin_root / "governance" / "09_PADROES" / "VETORES_DETERMINISMO_P04A_V1.json"
    return json.loads(caminho.read_text(encoding="utf-8"))


def test_vetor_01_hash_consulta() -> None:
    v = _vetores()
    assert sha256_canonico(v["query"]["documento"]) == v["query"]["sha256"]


def test_vetor_02_hash_universo() -> None:
    v = _vetores()
    assert sha256_canonico(v["universo"]["documento"]) == v["universo"]["sha256"]


def test_vetor_03_hash_particao() -> None:
    v = _vetores()
    assert sha256_canonico(v["particao"]["documento"]) == v["particao"]["sha256"]


def test_vetor_04_hash_identidade_e_id() -> None:
    v = _vetores()
    atual = sha256_canonico(v["identidade"]["payload"])
    assert atual == v["identidade"]["sha256"]
    assert "CFR-" + atual[:32].upper() == v["identidade"]["id_confluencia"]


def test_vetor_05_hash_resultado() -> None:
    v = _vetores()
    bloco = v["resultado_minimo_para_hash"]
    assert sha256_canonico(bloco["payload_sem_hash_resultado"]) == bloco["sha256_esperado"]
