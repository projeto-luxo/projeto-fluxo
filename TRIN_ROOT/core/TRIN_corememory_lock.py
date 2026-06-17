import os
from pathlib import Path

class TRINMemoryLock:
    """
    Sistema único de memória do TRIN
    - impede múltiplos caminhos
    - força uma única raiz
    """

    def __init__(self):
        self.root = Path(__file__).resolve().parents[1]
        self.memory_path = self._resolve_memory_path()

    def _resolve_memory_path(self):
        possiveis = [
            self.root / "data" / "memoria",
            self.root / "TRIN_HISTORICO",
            self.root / "memoria",
        ]

        for p in possiveis:
            if p.exists():
                return p

        # se não existir, cria automaticamente
        default = self.root / "data" / "memoria"
        default.mkdir(parents=True, exist_ok=True)
        return default

    def listar_arquivos(self):
        return list(self.memory_path.glob("*.csv"))

    def existe_memoria(self):
        return len(self.listar_arquivos()) > 0

    def caminho(self):
        return str(self.memory_path)
