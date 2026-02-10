@echo off
REM ============================================
REM Deep Clean & Rebuild Script for SaaS Stack
REM ============================================
echo.
echo ========================================
echo  DEEP CLEAN AND REBUILD SAAS STACK
echo ========================================
echo.

echo [1/6] Stopping all running containers...
docker-compose down -v
timeout /t 2 /nobreak >nul

echo.
echo [2/6] Removing all stopped containers...
docker container prune -f

echo.
echo [3/6] Removing dangling images...
docker image prune -f

echo.
echo [4/6] Removing build cache...
docker builder prune -f

echo.
echo [5/6] Removing unused volumes...
docker volume prune -f

echo.
echo [6/6] Starting fresh build (this may take 5-10 minutes)...
echo.
docker-compose build --no-cache --progress=plain

echo.
echo ========================================
echo  BUILD COMPLETE
echo ========================================
echo.
echo To start the services, run:
echo   docker-compose up -d
echo.
echo To view logs:
echo   docker-compose logs -f
echo.
pause
