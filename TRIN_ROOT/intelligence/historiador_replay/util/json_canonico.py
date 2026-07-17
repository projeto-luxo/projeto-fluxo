from __future__ import annotations
import json
from typing import Any

def json_canonico_bytes(valor: Any) -> bytes:
    return json.dumps(valor, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
