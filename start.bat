@echo off
echo ====================================
echo   Vavoo Playlist Generator
echo ====================================
echo.

cd /d "%~dp0"

if not exist "python_iptv\.venv" (
    echo Creating virtual environment...
    python -m venv python_iptv\.venv
    echo Installing dependencies...
    python_iptv\.venv\Scripts\pip.exe install -r python_iptv\requirements.txt
)

echo.
echo Generating playlist...
python_iptv\.venv\Scripts\python.exe python_iptv\generate_playlist_cli.py --output playlist.m3u8
echo.
echo Done! Playlist saved to playlist.m3u8
pause
