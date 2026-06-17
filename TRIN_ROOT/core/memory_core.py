from pathlib import Path

class TRINMemoryCore:
    def __init__(self):
        # FORÇA subir até encontrar TRIN_ROOT
        self.root = self._find_trin_root()
        self.memory = self.root / "data" / "memoria"
        self.memory.mkdir(parents=True, exist_ok=True)

    def _find_trin_root(self):
        current = Path(__file__).resolve()

        for parent in current.parents:
            if (parent / "data").exists() and (parent / "core").exists():
                return parent

        # fallback seguro
        return Path.cwd()

    def path(self):
        return str(self.memory)