@echo off
echo ========================================
echo FORCE REBUILD - Salla Price Optimizer
echo ========================================
echo.
echo This will:
echo 1. Stop all containers
echo 2. Remove all containers and volumes
echo 3. Rebuild images from scratch
echo 4. Start fresh containers
echo.
echo WARNING: This will delete all data in the database!
echo.
set /p confirm="Are you sure? (yes/no): "

if /i not "%confirm%"=="yes" (
    echo Cancelled.
    pause
    exit /b 0
)

echo.
echo [1/6] Stopping all containers...
docker-compose down
echo.

echo [2/6] Removing volumes...
docker-compose down -v
echo.

echo [3/6] Removing old images...
docker-compose down --rmi local
echo.

echo [4/6] Cleaning Docker system...
docker system prune -f
echo.

echo [5/6] Rebuilding images (no cache)...
docker-compose build --no-cache --progress=plain
if errorlevel 1 (
    echo.
    echo [ERROR] Build failed! Check the output above for errors.
    echo.
    echo Common issues:
    echo - Missing dependencies in requirements_saas.txt
    echo - Network issues downloading packages
    echo - Insufficient disk space
    echo.
    pause
    exit /b 1
)
echo.

echo [6/6] Starting containers with live logs...
echo.
echo Press Ctrl+C to stop viewing logs (containers will keep running)
echo.
timeout /t 3 /nobreak >nul

docker-compose up

echo.
echo ========================================
echo Rebuild complete!
echo ========================================
echo.
echo To run in background: docker-compose up -d
echo To view logs: docker-compose logs -f
echo To check status: docker-compose ps
echo.
pause
