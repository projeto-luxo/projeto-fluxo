$portas = 8001, 3000, 3001, 3002

# 1. Derrubar processos nas portas do TRIN
foreach ($porta in $portas) {
    Get-NetTCPConnection -LocalPort $porta -State Listen -ErrorAction SilentlyContinue |
    ForEach-Object {
        Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue
    }
}

Start-Sleep -Seconds 1

# 2. Derrubar backend/frontend por comando
Get-CimInstance Win32_Process |
Where-Object {
    $_.ProcessId -ne $PID -and
    $_.CommandLine -and
    (
        $_.CommandLine -like "*server_institucional_v6*" -or
        $_.CommandLine -like "*backend.server_institucional_v6*" -or
        $_.CommandLine -like "*uvicorn*" -or
        $_.CommandLine -like "*react-scripts*" -or
        $_.CommandLine -like "*npm start*" -or
        $_.CommandLine -like "*TRIN_ROOT\frontend*"
    )
} |
ForEach-Object {
    Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue
}

Start-Sleep -Seconds 1

# 3. Fechar janelas de terminal do TRIN, se existirem
Get-Process |
Where-Object {
    $_.MainWindowTitle -and
    (
        $_.MainWindowTitle -like "*TRIN BACKEND*" -or
        $_.MainWindowTitle -like "*TRIN FRONTEND*" -or
        $_.MainWindowTitle -like "*INICIAR TRIN PAINEL*" -or
        $_.MainWindowTitle -like "*TRIN PAINEL*"
    )
} |
ForEach-Object {
    Stop-Process -Id $_.Id -Force -ErrorAction SilentlyContinue
}

Start-Sleep -Seconds 1

# 4. Fechar janela do navegador usada pelo TRIN
# Observacao: se a aba TRIN estiver misturada com outras abas na mesma janela,
# o Windows pode fechar aquela janela inteira.
Get-Process |
Where-Object {
    $_.MainWindowTitle -and
    (
        $_.ProcessName -match "msedge|chrome|brave|firefox"
    ) -and
    (
        $_.MainWindowTitle -like "*React App*" -or
        $_.MainWindowTitle -like "*localhost:3000*" -or
        $_.MainWindowTitle -like "*localhost:3001*" -or
        $_.MainWindowTitle -like "*localhost:3002*" -or
        $_.MainWindowTitle -like "*TRIN FLOW*" -or
        $_.MainWindowTitle -like "*TRIN*"
    )
} |
ForEach-Object {
    try {
        $_.CloseMainWindow() | Out-Null
        Start-Sleep -Milliseconds 500
        if (-not $_.HasExited) {
            Stop-Process -Id $_.Id -Force -ErrorAction SilentlyContinue
        }
    } catch {
        Stop-Process -Id $_.Id -Force -ErrorAction SilentlyContinue
    }
}
