$TRIN_ROOT = "C:\Users\User\projeto_fluxo\TRIN_ROOT"
$PY = "C:\Users\User\AppData\Local\Python\pythoncore-3.14-64\python.exe"
$LOG_DIR = "$TRIN_ROOT\TRIN_HISTORICO\00_LOGS\launcher"
$EDGE_PROFILE = "$TRIN_ROOT\TRIN_HISTORICO\00_LOGS\launcher\edge_trin_profile"

New-Item -ItemType Directory -Path $LOG_DIR -Force | Out-Null
New-Item -ItemType Directory -Path $EDGE_PROFILE -Force | Out-Null

foreach ($porta in 8001, 3000, 3001, 3002) {
    Get-NetTCPConnection -LocalPort $porta -State Listen -ErrorAction SilentlyContinue |
    ForEach-Object {
        Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue
    }
}

Start-Sleep -Seconds 2

$backendCmd = "cd /d `"$TRIN_ROOT`" && set PYTHONPATH=$TRIN_ROOT && `"$PY`" -m uvicorn backend.server_institucional_v6:app --host 127.0.0.1 --port 8001 >> `"$LOG_DIR\backend.log`" 2>>&1"
Start-Process -FilePath "cmd.exe" -ArgumentList "/c", $backendCmd -WindowStyle Hidden

Start-Sleep -Seconds 6

$frontendCmd = "cd /d `"$TRIN_ROOT\frontend`" && set PORT=3000 && set BROWSER=none && set CI=true && npm start >> `"$LOG_DIR\frontend.log`" 2>>&1"
Start-Process -FilePath "cmd.exe" -ArgumentList "/c", $frontendCmd -WindowStyle Hidden

Start-Sleep -Seconds 12

$edge = "${env:ProgramFiles(x86)}\Microsoft\Edge\Application\msedge.exe"
if (-not (Test-Path $edge)) {
    $edge = "${env:ProgramFiles}\Microsoft\Edge\Application\msedge.exe"
}

Start-Process $edge "--user-data-dir=`"$EDGE_PROFILE`" --app=http://localhost:3000 --new-window"
