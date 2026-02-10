@echo off
setlocal enabledelayedexpansion

echo ========================================
echo LOG VIEWER - Salla Price Optimizer
echo ========================================
echo.

:menu
echo Select service to view logs:
echo.
echo 1. All services (combined)
echo 2. PostgreSQL Database
echo 3. Redis Cache
echo 4. FastAPI Web Server
echo 5. Celery Worker
echo 6. Celery Beat
echo 7. Flower Monitor
echo 8. Streamlit Dashboard
echo 9. Live tail (follow all logs)
echo 0. Exit
echo.
set /p choice="Enter choice (0-9): "

if "%choice%"=="0" exit /b 0

echo.
echo ========================================

if "%choice%"=="1" (
    echo SHOWING: All Services ^(last 100 lines^)
    echo ========================================
    docker-compose logs --tail=100
) else if "%choice%"=="2" (
    echo SHOWING: PostgreSQL Database
    echo ========================================
    docker-compose logs --tail=100 db
) else if "%choice%"=="3" (
    echo SHOWING: Redis Cache
    echo ========================================
    docker-compose logs --tail=100 redis
) else if "%choice%"=="4" (
    echo SHOWING: FastAPI Web Server
    echo ========================================
    docker-compose logs --tail=100 web
) else if "%choice%"=="5" (
    echo SHOWING: Celery Worker
    echo ========================================
    docker-compose logs --tail=100 celery_worker
) else if "%choice%"=="6" (
    echo SHOWING: Celery Beat
    echo ========================================
    docker-compose logs --tail=100 celery_beat
) else if "%choice%"=="7" (
    echo SHOWING: Flower Monitor
    echo ========================================
    docker-compose logs --tail=100 flower
) else if "%choice%"=="8" (
    echo SHOWING: Streamlit Dashboard
    echo ========================================
    docker-compose logs --tail=100 dashboard
) else if "%choice%"=="9" (
    echo SHOWING: Live Tail ^(Press Ctrl+C to stop^)
    echo ========================================
    docker-compose logs -f
) else (
    echo Invalid choice!
)

echo.
echo ========================================
echo.
pause
goto menu
