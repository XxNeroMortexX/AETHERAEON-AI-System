@echo off
title Aetheraeon AI Launcher

cd /d "%~dp0"

echo ==========================================
echo        Aetheraeon AI Starting
echo ==========================================
echo.

if not exist "env\Scripts\activate.bat" (
    echo ERROR:
    echo Python environment not found.
    echo Expected:
    echo %~dp0env
    echo.
    pause
    exit /b 1
)

call env\Scripts\activate.bat

echo Environment activated.
echo Starting Aetheraeon AI...
echo.

python -m core.api_gateway

pause