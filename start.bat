@echo off
cd /d "%~dp0"
title Conversor de Videos

echo.
echo ==========================================
echo   Conversor de Videos para TV
echo ==========================================
echo.

REM --- Verifica se o FFmpeg existe ---
if not exist "ffmpeg\ffmpeg.exe" (
    echo [!] FFmpeg nao encontrado.
    echo [i] Baixando automaticamente pela primeira vez...
    echo [i] Isso pode levar alguns minutos. Aguarde.
    echo.

    powershell -NoProfile -Command "Invoke-WebRequest -Uri 'https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip' -OutFile 'ffmpeg.zip'"

    if not exist "ffmpeg.zip" (
        echo.
        echo [X] Falha ao baixar o FFmpeg.
        echo [i] Verifique sua conexao com a internet.
        pause
        exit /b 1
    )

    echo [i] Extraindo...
    powershell -NoProfile -Command "Expand-Archive -Path 'ffmpeg.zip' -DestinationPath 'ffmpeg_temp' -Force"

    if not exist "ffmpeg" mkdir ffmpeg

    for /d %%d in ("ffmpeg_temp\*") do (
        if exist "%%d\bin\ffmpeg.exe" (
            copy /y "%%d\bin\*.exe" "ffmpeg\" >nul
        )
    )

    rmdir /s /q "ffmpeg_temp" 2>nul
    del /q "ffmpeg.zip" 2>nul

    if not exist "ffmpeg\ffmpeg.exe" (
        echo.
        echo [X] Nao foi possivel instalar o FFmpeg automaticamente.
        echo [i] Baixe manualmente em: https://www.gyan.dev/ffmpeg/builds/
        echo [i] Extraia e coloque ffmpeg.exe dentro da pasta 'ffmpeg\'
        pause
        exit /b 1
    )

    echo.
    echo [OK] FFmpeg instalado com sucesso!
    echo.
)

REM --- Verifica Python ---
where python >nul 2>nul
if errorlevel 1 (
    echo [X] Python nao encontrado.
    echo [i] Instale em https://www.python.org/downloads/
    echo [i] Marque "Add Python to PATH" na instalacao.
    pause
    exit /b 1
)

REM --- Cria ambiente virtual se nao existir ---
if not exist ".venv\Scripts\python.exe" (
    echo [i] Criando ambiente virtual...
    python -m venv .venv
    if errorlevel 1 (
        echo [X] Falha ao criar ambiente virtual.
        pause
        exit /b 1
    )
)

REM --- Instala dependencias se necessario ---
if not exist ".venv\.deps_ok" (
    echo [i] Instalando dependencias...
    ".venv\Scripts\python.exe" -m pip install --upgrade pip >nul
    ".venv\Scripts\python.exe" -m pip install -r requirements.txt
    if errorlevel 1 (
        echo [X] Falha ao instalar dependencias.
        pause
        exit /b 1
    )
    echo ok > ".venv\.deps_ok"
)

echo.
echo [i] Iniciando servidor...
echo.
".venv\Scripts\python.exe" app.py

pause