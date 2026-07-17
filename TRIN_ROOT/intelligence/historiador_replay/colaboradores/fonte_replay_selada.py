from __future__ import annotations
import os
from pathlib import Path
from typing import BinaryIO
from ..erros import FalhaReplay
from ..modelos_internos import FingerprintFonte
from ..util.guardas_de_caminho import validar_caminho_controlado
from ..util.hash_sha256 import sha256_bytes, sha256_handle

class FonteReplaySeladaV1:
    def __init__(self, origem_id: str, path: Path) -> None:
        self.origem_id = origem_id
        self.path = validar_caminho_controlado(path)
        self.handle: BinaryIO | None = None
        self.fingerprint_inicial: FingerprintFonte | None = None
        self.aberturas = 0
        self.fechada = True

    def _abrir_handle(self) -> BinaryIO:
        return self.path.open("rb", buffering=0)

    def __enter__(self):
        if self.handle is not None:
            raise FalhaReplay("FONTE_REABERTA")
        self.handle = self._abrir_handle()
        self.aberturas += 1
        self.fechada = False
        self.fingerprint_inicial = self.fingerprint()
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.fechar()

    def fechar(self) -> None:
        if self.handle is not None and not self.handle.closed:
            self.handle.close()
        self.fechada = True

    def fingerprint(self) -> FingerprintFonte:
        if self.handle is None or self.handle.closed:
            raise FalhaReplay("FONTE_NAO_ABERTA")
        stat = os.fstat(self.handle.fileno())
        identity = f"{getattr(stat, 'st_dev', 0)}:{getattr(stat, 'st_ino', 0)}"
        digest = sha256_handle(self.handle)
        sealed = sha256_bytes(f"{self.origem_id}|{identity}|{stat.st_size}|{digest}".encode("utf-8"))
        return FingerprintFonte(self.origem_id, stat.st_size, digest, identity, sealed)

    def verificar(self, origem_hash: str, tamanho: int, fonte_selada_id: str | None = None) -> FingerprintFonte:
        atual = self.fingerprint()
        inicial = self.fingerprint_inicial
        if inicial is None:
            raise FalhaReplay("FONTE_SEM_IDENTIDADE_INICIAL")
        if atual.sha256 != origem_hash:
            raise FalhaReplay("FONTE_HASH_DIVERGENTE")
        if atual.tamanho != tamanho:
            raise FalhaReplay("FONTE_TAMANHO_DIVERGENTE")
        if atual.identidade_sistema != inicial.identidade_sistema:
            raise FalhaReplay("FONTE_IDENTIDADE_DIVERGENTE")
        if fonte_selada_id is not None and atual.fonte_selada_id != fonte_selada_id:
            raise FalhaReplay("FONTE_SELADA_ID_DIVERGENTE")
        return atual
