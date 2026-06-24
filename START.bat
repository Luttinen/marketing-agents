@echo off
title Marketing AI Agents - Launcher
color 0A
cls

echo.
echo  ███╗   ███╗ █████╗ ██████╗ ██╗  ██╗███████╗████████╗██╗███╗   ██╗ ██████╗
echo  ████╗ ████║██╔══██╗██╔══██╗██║ ██╔╝██╔════╝╚══██╔══╝██║████╗  ██║██╔════╝
echo  ██╔████╔██║███████║██████╔╝█████╔╝ █████╗     ██║   ██║██╔██╗ ██║██║  ███╗
echo  ██║╚██╔╝██║██╔══██║██╔══██╗██╔═██╗ ██╔══╝     ██║   ██║██║╚██╗██║██║   ██║
echo  ██║ ╚═╝ ██║██║  ██║██║  ██║██║  ██╗███████╗   ██║   ██║██║ ╚████║╚██████╔╝
echo  ╚═╝     ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝   ╚═╝   ╚═╝╚═╝  ╚═══╝ ╚═════╝
echo.
echo  AI Agents ^| 32 Specialists ^| Finnish + English
echo  ================================================
echo.

cd /d "%~dp0"

:: Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo  [ERROR] Python ei loytynyt. Asenna python.org
    pause
    exit /b 1
)

:: Create .env if missing
if not exist .env (
    echo  [SETUP] .env ei loydy - luodaan...
    echo.
    set /p APIKEY=" Anna Anthropic API key (https://console.anthropic.com): "
    echo ANTHROPIC_API_KEY=%APIKEY%> .env
    echo  [OK] .env luotu!
    echo.
)

:: Check API key is not empty placeholder
findstr /C:"your_api_key_here" .env >nul 2>&1
if not errorlevel 1 (
    echo  [SETUP] API key on placeholder - vaihdetaan...
    echo.
    set /p APIKEY=" Anna Anthropic API key: "
    echo ANTHROPIC_API_KEY=%APIKEY%> .env
    echo  [OK] API key paivitetty!
    echo.
)

:: Create venv if missing
if not exist .venv (
    echo  [SETUP] Luodaan virtuaaliymparisto...
    python -m venv .venv
    echo  [OK] .venv luotu
)

:: Activate venv
call .venv\Scripts\activate.bat

:: Install/upgrade deps
echo  [SETUP] Tarkistetaan riippuvuudet...
pip install -q -r requirements.txt
echo  [OK] Riippuvuudet kunnossa
echo.

:: Load API key from .env
for /f "tokens=2 delims==" %%A in ('findstr "ANTHROPIC_API_KEY" .env') do set ANTHROPIC_API_KEY=%%A

echo  [START] Kaynnistetaan palvelin...
echo  [INFO] Avaa selain: http://localhost:8000
echo  [INFO] Sulje: paina CTRL+C
echo.

:: Open browser after 2 seconds
start "" cmd /c "timeout /t 2 /nobreak >nul && start http://localhost:8000"

:: Start server
uvicorn app:app --host 0.0.0.0 --port 8000 --reload

pause
