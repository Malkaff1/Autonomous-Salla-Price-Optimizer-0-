@echo off
setlocal enabledelayedexpansion

echo ========================================
echo SALLA PRICE OPTIMIZER - DIAGNOSTIC TOOL
echo ========================================
echo.

:: Check Docker
echo [1/8] Checking Docker...
docker --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker is not installed or not running!
    echo Please start Docker Desktop first.
    pause
    exit /b 1
)
echo [OK] Docker is installed
docker info >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker daemon is not running!
    echo Please start Docker Desktop.
    pause
    exit /b 1
)
echo [OK] Docker daemon is running
echo.

:: Check Docker Compose
echo [2/8] Checking Docker Compose...
docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker Compose is not installed!
    pause
    exit /b 1
)
echo [OK] Docker Compose is installed
echo.

:: Check .env file
echo [3/8] Checking .env file...
if not exist ".env" (
    echo [WARNING] .env file not found!
    echo Creating from .env.example...
    if exist ".env.example" (
        copy ".env.example" ".env" >nul
        echo [OK] .env file created
    ) else (
        echo [ERROR] .env.example not found!
    )
) else (
    echo [OK] .env file exists
)
echo.

:: Check port conflicts
echo [4/8] Checking for port conflicts...
set PORTS=5432 6379 8000 8501 5555

for %%P in (%PORTS%) do (
    netstat -ano | findstr ":%%P " | findstr "LISTENING" >nul 2>&1
    if not errorlevel 1 (
        echo [WARNING] Port %%P is already in use!
        netstat -ano | findstr ":%%P " | findstr "LISTENING"
    ) else (
        echo [OK] Port %%P is available
    )
)
echo.

:: Check entrypoint.sh line endings
echo [5/8] Checking entrypoint.sh...
if exist "entrypoint.sh" (
    echo [OK] entrypoint.sh exists
    :: Check for CRLF (Windows line endings)
    findstr /R /C:".*" entrypoint.sh >nul 2>&1
    if errorlevel 1 (
        echo [WARNING] entrypoint.sh may have line ending issues
    ) else (
        echo [OK] entrypoint.sh format looks good
    )
) else (
    echo [ERROR] entrypoint.sh not found!
)
echo.

:: Check container status
echo [6/8] Checking container status...
docker-compose ps
echo.

:: Check Docker volumes
echo [7/8] Checking Docker volumes...
docker volume ls | findstr "salla"
echo.

:: Check Docker networks
echo [8/8] Checking Docker networks...
docker network ls | findstr "salla"
echo.

echo ========================================
echo DIAGNOSTIC COMPLETE
echo ========================================
echo.

:: Offer to view logs
echo Would you like to view container logs?
echo 1. Yes - View all logs
echo 2. Yes - View specific service
echo 3. No - Exit
echo.
set /p choice="Enter choice (1-3): "

if "%choice%"=="1" (
    echo.
    echo Showing last 50 lines of all logs...
    docker-compose logs --tail=50
) else if "%choice%"=="2" (
    echo.
    echo Available services: db, redis, web, celery_worker, celery_beat, flower, dashboard
    set /p service="Enter service name: "
    echo.
    echo Showing logs for !service!...
    docker-compose logs --tail=100 !service!
)

echo.
echo ========================================
echo TROUBLESHOOTING TIPS
echo ========================================
echo.
echo If containers are not starting:
echo 1. Check logs: docker-compose logs -f
echo 2. Rebuild: docker-compose build --no-cache
echo 3. Clean start: docker-compose down -v ^&^& docker-compose up -d
echo.
echo If ports are in use:
echo 1. Stop conflicting services
echo 2. Or change ports in docker-compose.yml
echo.
echo If database fails:
echo 1. Check logs: docker-compose logs db
echo 2. Reset: docker-compose down -v
echo 3. Restart: docker-compose up -d db
echo.
pause
