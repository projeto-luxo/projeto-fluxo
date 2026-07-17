from __future__ import annotations
import hashlib
from pathlib import Path
from typing import BinaryIO

BLOCO_HASH = 65536

def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def sha256_arquivo(path: Path) -> str:
    h = hashlib.sha256()
    with Path(path).open("rb") as handle:
        while True:
            chunk = handle.read(BLOCO_HASH)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()

def sha256_handle(handle: BinaryIO) -> str:
    pos = handle.tell()
    handle.seek(0)
    h = hashlib.sha256()
    while True:
        chunk = handle.read(BLOCO_HASH)
        if not chunk:
            break
        h.update(chunk)
    handle.seek(pos)
    return h.hexdigest()
