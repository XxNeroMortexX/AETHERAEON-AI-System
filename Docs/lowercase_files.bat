@echo off
setlocal EnableDelayedExpansion

echo ==========================================
echo AETHERAEON FILE LOWERCASE DEBUG RENAMER
echo ==========================================

REM Move to the folder where this BAT file is located
cd /d "%~dp0"

echo Current Folder:
echo %CD%

echo.
echo Scanning files...
echo.

for %%F in (*) do (

    echo Found:
    echo %%F

    set "oldname=%%F"

    REM Convert filename to lowercase using PowerShell
    for /f "delims=" %%A in ('powershell -NoProfile -Command "'%%F'.ToLower()"') do (
        set "newname=%%A"
    )

    echo New Name:
    echo !newname!

    if not "%%F"=="!newname!" (

		echo RENAMING:
		echo %%F ^> !newname!

		set "tempname=__temp_lowercase_%%~nxF"

		echo Temporary:
		echo %%F ^> !tempname!

		ren "%%F" "!tempname!"

		echo Final:
		echo !tempname! ^> !newname!

		ren "!tempname!" "!newname!"

	) else (
		echo Already lowercase
	)

    echo ------------------------------------------
)

echo.
echo DONE
pause