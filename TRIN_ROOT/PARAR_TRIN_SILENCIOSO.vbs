Set WshShell = CreateObject("WScript.Shell")
WshShell.Run "powershell.exe -NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File ""C:\Users\User\projeto_fluxo\TRIN_ROOT\PARAR_TRIN_SILENCIOSO.ps1""", 0, False
