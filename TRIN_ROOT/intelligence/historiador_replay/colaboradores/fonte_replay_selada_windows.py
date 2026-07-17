from __future__ import annotations
import os
from pathlib import Path
from typing import BinaryIO
from .fonte_replay_selada import FonteReplaySeladaV1
from ..erros import FalhaReplay

class FonteReplaySeladaWindowsV1(FonteReplaySeladaV1):
    """CreateFileW: leitura; compartilhamento somente leitura; escrita/exclusão negadas."""
    def _abrir_handle(self) -> BinaryIO:
        if os.name != "nt":
            return super()._abrir_handle()
        import ctypes
        import msvcrt
        from ctypes import wintypes
        GENERIC_READ = 0x80000000
        FILE_SHARE_READ = 0x00000001
        OPEN_EXISTING = 3
        FILE_ATTRIBUTE_NORMAL = 0x80
        FILE_FLAG_SEQUENTIAL_SCAN = 0x08000000
        INVALID_HANDLE_VALUE = wintypes.HANDLE(-1).value
        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        create_file = kernel32.CreateFileW
        create_file.argtypes = [wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD, wintypes.LPVOID,
                                wintypes.DWORD, wintypes.DWORD, wintypes.HANDLE]
        create_file.restype = wintypes.HANDLE
        handle = create_file(str(self.path), GENERIC_READ, FILE_SHARE_READ, None, OPEN_EXISTING,
                             FILE_ATTRIBUTE_NORMAL | FILE_FLAG_SEQUENTIAL_SCAN, None)
        if handle == INVALID_HANDLE_VALUE:
            raise FalhaReplay("FONTE_WINDOWS_ABERTURA_FALHOU", str(ctypes.get_last_error()))
        fd = msvcrt.open_osfhandle(int(handle), os.O_RDONLY | os.O_BINARY)
        return os.fdopen(fd, "rb", buffering=0)
