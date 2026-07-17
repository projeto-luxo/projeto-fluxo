from __future__ import annotations
from pathlib import Path
from .erros import FalhaReplay
from .util.hash_sha256 import sha256_arquivo

class ProvaNaoMutacao:
    @staticmethod
    def snapshot(root: Path) -> dict:
        base = Path(root); result = {}
        for path in sorted(p for p in base.rglob("*") if p.is_file()):
            result[path.relative_to(base).as_posix()] = {"bytes":path.stat().st_size,"sha256":sha256_arquivo(path)}
        return result
    @staticmethod
    def delta(before: dict, after: dict) -> dict:
        b,a=set(before),set(after)
        return {"criados":sorted(a-b),"removidos":sorted(b-a),"modificados":sorted(k for k in a&b if before[k]!=after[k])}
    @classmethod
    def exigir_zero(cls, before: dict, after: dict) -> None:
        delta=cls.delta(before,after)
        if any(delta.values()): raise FalhaReplay("MUTACAO_DETECTADA", str(delta))
