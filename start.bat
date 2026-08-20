@echo off
title Conversor de Videos para TV
cd /d "%~dp0"

where python >nul 2>&1
if errorlevel 1 (
    echo.
    echo Python nao foi encontrado.
    echo Instale o Python e tente novamente.
    pause
    exit /b 1
)

if not exist ".venv\Scripts\python.exe" (
    echo Criando ambiente virtual...
    python -m venv .venv
    if errorlevel 1 (
        echo Nao foi possivel criar o ambiente virtual.
        pause
        exit /b 1
    )
)

echo Instalando/verificando dependencias...
.venv\Scripts\python.exe -m pip install -r requirements.txt

echo.
echo Iniciando o Conversor de Videos para TV...
echo O navegador sera aberto automaticamente.

start "" http://127.0.0.1:5000
.venv\Scripts\python.exe app.py

pause
