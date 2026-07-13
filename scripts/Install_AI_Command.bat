@echo off
setlocal EnableDelayedExpansion

title Install Aetheraeon AI Command

echo ==========================================
echo     Aetheraeon AI Command Installer
echo ==========================================
echo.

:: Move to project root
cd /d "%~dp0\.."

set "AETHERAEON_ROOT=%CD%"

echo Project detected:
echo %AETHERAEON_ROOT%
echo.

:: Escape characters for registry storage
set "AI_COMMAND=doskey AI=cd /d %AETHERAEON_ROOT% ^& call env\Scripts\activate.bat ^& cls ^& python -m core.api_gateway"

echo Checking existing CMD AutoRun...

for /f "tokens=2*" %%A in ('reg query "HKCU\Software\Microsoft\Command Processor" /v AutoRun 2^>nul') do (
    set "CURRENT_AUTORUN=%%B"
)

if defined CURRENT_AUTORUN (
    echo Existing AutoRun detected:
    echo.
    echo !CURRENT_AUTORUN!
    echo.

    echo Checking for existing Aetheraeon AI command...

    echo !CURRENT_AUTORUN! | findstr /i "doskey AI=" >nul

    if not errorlevel 1 (
        echo.
        echo Aetheraeon AI command already exists.
        echo Updating it...
        echo.

        set "NEW_AUTORUN=!CURRENT_AUTORUN!"
        :: Remove old AI section is intentionally avoided because
        :: complex user AutoRun commands are hard to safely parse.
        :: User will be informed if duplicate exists.

        echo Existing AI command found.
        echo Please use Remove_AI_Command.bat first if replacement is needed.
        pause
        exit /b 0
    )

    set "NEW_AUTORUN=!CURRENT_AUTORUN! ^& !AI_COMMAND!"

) else (

    set "NEW_AUTORUN=!AI_COMMAND!"

)

echo Installing Aetheraeon AI shortcut...
echo.

reg add "HKCU\Software\Microsoft\Command Processor" ^
/v AutoRun ^
/d "!NEW_AUTORUN!" ^
/f


if errorlevel 1 (
    echo.
    echo ERROR: Failed to install command.
    pause
    exit /b 1
)

echo.
echo ==========================================
echo Installation Complete
echo ==========================================
echo.
echo Close all Command Prompt windows.
echo Open a new CMD window.
echo.
echo Type:
echo.
echo AI
echo.
echo to start Aetheraeon AI.
echo.
echo Verify with PowerShell:
echo.
echo Get-ItemProperty -Path "HKCU:\Software\Microsoft\Command Processor" -Name AutoRun
echo.

pause