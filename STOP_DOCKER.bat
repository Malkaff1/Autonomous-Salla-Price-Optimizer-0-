@echo off
echo ========================================
echo Stopping Salla Price Optimizer
echo ========================================
echo.

echo What would you like to do?
echo.
echo 1. Stop containers (keep data)
echo 2. Stop and remove containers (keep data)
echo 3. Stop, remove containers and volumes (DELETE ALL DATA)
echo 4. Cancel
echo.
set /p choice="Enter choice (1-4): "

if "%choice%"=="1" (
    echo.
    echo Stopping containers...
    docker-compose stop
    echo [OK] Containers stopped
) else if "%choice%"=="2" (
    echo.
    echo Stopping and removing containers...
    docker-compose down
    echo [OK] Containers removed
) else if "%choice%"=="3" (
    echo.
    echo WARNING: This will delete all data including database!
    set /p confirm="Are you sure? (yes/no): "
    if /i "!confirm!"=="yes" (
        echo.
        echo Stopping and removing everything...
        docker-compose down -v
        echo [OK] Everything removed
    ) else (
        echo Cancelled.
    )
) else if "%choice%"=="4" (
    echo Cancelled.
) else (
    echo Invalid choice!
)

echo.
echo Current status:
docker-compose ps

echo.
pause
