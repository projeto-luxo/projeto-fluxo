from __future__ import annotations
from pathlib import Path
from ..erros import ViolacaoEscopo

TRIN_ROOT_PROIBIDO = Path(r"C:\Users\User\projeto_fluxo\TRIN_ROOT")
TRIN_HISTORICO_PROIBIDO = Path(r"C:\Users\User\projeto_fluxo\TRIN_HISTORICO")

def _normalizar(path: Path) -> str:
    return str(Path(path).resolve()).replace("/", "\\").casefold().rstrip("\\")

def esta_dentro(path: Path, root: Path) -> bool:
    p, r = _normalizar(path), _normalizar(root)
    return p == r or p.startswith(r + "\\")

def validar_caminho_controlado(path: Path) -> Path:
    resolved = Path(path).resolve()
    for forbidden in (TRIN_ROOT_PROIBIDO, TRIN_HISTORICO_PROIBIDO):
        if esta_dentro(resolved, forbidden):
            raise ViolacaoEscopo("CAMINHO_REAL_PROIBIDO", str(resolved))
    return resolved
