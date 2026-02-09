@echo off
title Python Vavoo Player Launcher
echo Starting up...
echo.
REM Check if venv exists
if not exist ".venv\Scripts\python.exe" (
    echo [INFO] Virtual environment not found. Creating...
    python -m venv .venv
    echo [INFO] Installing dependencies...
    .\.venv\Scripts\python.exe -m pip install -r python_iptv\requirements.txt
    echo [INFO] Setup complete.
)

REM Start the application using venv interpreter
start "" ".venv\Scripts\python.exe" "python_iptv\main.py"

echo Application started.
timeout /t 3 >nul
exit
