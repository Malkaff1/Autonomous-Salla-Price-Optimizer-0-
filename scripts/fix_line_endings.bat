@echo off
echo ========================================
echo FIX LINE ENDINGS - entrypoint.sh
echo ========================================
echo.
echo This script converts CRLF (Windows) to LF (Linux)
echo line endings in entrypoint.sh
echo.

if not exist "entrypoint.sh" (
    echo [ERROR] entrypoint.sh not found!
    pause
    exit /b 1
)

echo Converting line endings...

:: Use PowerShell to convert CRLF to LF
powershell -Command "(Get-Content entrypoint.sh -Raw) -replace \"`r`n\", \"`n\" | Set-Content -NoNewline entrypoint.sh"

if errorlevel 1 (
    echo [ERROR] Conversion failed!
    pause
    exit /b 1
)

echo [OK] Line endings converted successfully!
echo.
echo The entrypoint.sh file now has Unix (LF) line endings.
echo.
echo Next steps:
echo 1. Rebuild Docker images: docker-compose build --no-cache
echo 2. Start containers: docker-compose up -d
echo.
echo Or simply run: rebuild.bat
echo.
pause
