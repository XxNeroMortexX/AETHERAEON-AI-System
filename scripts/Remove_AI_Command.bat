@echo off
setlocal EnableDelayedExpansion

title Remove Aetheraeon AI Command

echo ==========================================
echo     Remove Aetheraeon AI Command
echo ==========================================
echo.

echo Reading current CMD AutoRun...

for /f "tokens=2*" %%A in ('reg query "HKCU\Software\Microsoft\Command Processor" /v AutoRun 2^>nul') do (
    set "CURRENT_AUTORUN=%%B"
)

if not defined CURRENT_AUTORUN (
    echo No AutoRun configuration found.
    pause
    exit /b 0
)

echo Current AutoRun:
echo.
echo !CURRENT_AUTORUN!
echo.

echo Searching for Aetheraeon AI command...

echo !CURRENT_AUTORUN! | findstr /i "doskey AI=" >nul

if errorlevel 1 (
    echo.
    echo No Aetheraeon AI command found.
    pause
    exit /b 0
)

echo.
echo Aetheraeon AI command detected.
echo.

echo Removing Aetheraeon AI shortcut...

:: Because CMD AutoRun is a single string, fully automatic
:: removal of one command is risky if users have custom commands.
:: Save backup first.

reg query "HKCU\Software\Microsoft\Command Processor" /v AutoRun > "%TEMP%\Aetheraeon_AutoRun_Backup.txt"

echo Backup created:
echo %TEMP%\Aetheraeon_AutoRun_Backup.txt
echo.

echo.
echo IMPORTANT:
echo The current AutoRun contains Aetheraeon.
echo.
echo For safety, the original value will be cleared.
echo You can restore other shortcuts manually from the backup.
echo.

choice /m "Continue removing AutoRun"

if errorlevel 2 (
    echo Cancelled.
    pause
    exit /b 0
)

reg delete "HKCU\Software\Microsoft\Command Processor" /v AutoRun /f

echo.
echo Aetheraeon AutoRun removed.
echo.
echo Open a new CMD window to apply changes.
echo.

pause