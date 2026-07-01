@echo off
title INICIAR TRIN PAINEL
echo ============================================
echo INICIANDO TRIN PAINEL
echo ============================================

set TRIN_ROOT=C:\Users\User\projeto_fluxo\TRIN_ROOT
set PY=C:\Users\User\AppData\Local\Python\pythoncore-3.14-64\python.exe

echo.
echo [0/3] Limpando portas antigas 8001 e 3000...

for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8001') do (
    taskkill /PID %%a /F > nul 2>&1
)

for /f "tokens=5" %%a in ('netstat -ano ^| findstr :3000') do (
    taskkill /PID %%a /F > nul 2>&1
)

timeout /t 2 /nobreak > nul

echo.
echo [1/3] Subindo BACKEND na porta 8001...
start "TRIN BACKEND 8001" powershell -NoExit -ExecutionPolicy Bypass -Command "cd '%TRIN_ROOT%'; $env:PYTHONPATH='%TRIN_ROOT%'; & '%PY%' -m uvicorn backend.server_institucional_v6:app --host 127.0.0.1 --port 8001"

timeout /t 5 /nobreak > nul

echo.
echo [2/3] Subindo FRONTEND na porta 3000...
start "TRIN FRONTEND 3000" powershell -NoExit -ExecutionPolicy Bypass -Command "cd '%TRIN_ROOT%\frontend'; $env:PORT='3000'; $env:BROWSER='none'; npm start"

timeout /t 10 /nobreak > nul

echo.
echo [3/3] Abrindo navegador...
start "" "http://localhost:3000"

echo.
echo ============================================
echo TRIN PAINEL SOLICITADO.
echo Mantenha as janelas BACKEND e FRONTEND abertas.
echo ============================================
pause
