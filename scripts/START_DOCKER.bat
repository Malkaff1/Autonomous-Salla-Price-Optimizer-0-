@echo off
echo ========================================
echo Starting Salla Price Optimizer SaaS
echo ========================================
echo.

:: Check Docker
echo [1/5] Checking Docker...
docker --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker is not installed or not running!
    echo Please install Docker Desktop from: https://www.docker.com/products/docker-desktop
    pause
    exit /b 1
)

docker info >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker daemon is not running!
    echo Please start Docker Desktop and wait for it to be ready.
    pause
    exit /b 1
)
echo [OK] Docker is running
echo.

:: Check .env file
echo [2/5] Checking configuration...
if not exist ".env" (
    echo [WARNING] .env file not found!
    if exist ".env.example" (
        echo Creating .env from .env.example...
        copy ".env.example" ".env" >nul
        echo [OK] .env file created - Please edit it with your API keys
        echo.
        echo Required keys:
        echo - OPENAI_API_KEY
        echo - TAVILY_API_KEY
        echo - SALLA_ACCESS_TOKEN
        echo - SALLA_REFRESH_TOKEN
        echo.
        pause
    ) else (
        echo [ERROR] .env.example not found!
        pause
        exit /b 1
    )
) else (
    echo [OK] .env file exists
)
echo.

:: Check for port conflicts
echo [3/5] Checking ports...
set PORT_CONFLICT=0

netstat -ano | findstr ":5432 " | findstr "LISTENING" >nul 2>&1
if not errorlevel 1 (
    echo [WARNING] Port 5432 ^(PostgreSQL^) is already in use!
    set PORT_CONFLICT=1
)

netstat -ano | findstr ":6379 " | findstr "LISTENING" >nul 2>&1
if not errorlevel 1 (
    echo [WARNING] Port 6379 ^(Redis^) is already in use!
    set PORT_CONFLICT=1
)

netstat -ano | findstr ":8000 " | findstr "LISTENING" >nul 2>&1
if not errorlevel 1 (
    echo [WARNING] Port 8000 ^(API^) is already in use!
    set PORT_CONFLICT=1
)

netstat -ano | findstr ":8501 " | findstr "LISTENING" >nul 2>&1
if not errorlevel 1 (
    echo [WARNING] Port 8501 ^(Dashboard^) is already in use!
    set PORT_CONFLICT=1
)

if %PORT_CONFLICT%==1 (
    echo.
    echo [WARNING] Some ports are already in use!
    echo This may cause conflicts. Continue anyway?
    set /p continue="Continue? (yes/no): "
    if /i not "!continue!"=="yes" (
        echo Cancelled.
        pause
        exit /b 1
    )
) else (
    echo [OK] All ports are available
)
echo.

:: Start services
echo [4/5] Starting Docker containers...
echo This may take a few minutes on first run...
echo.

docker-compose up -d

if errorlevel 1 (
    echo.
    echo [ERROR] Failed to start containers!
    echo.
    echo Run 'diagnose.bat' for detailed diagnostics
    echo Or run 'check_logs.bat' to view error logs
    echo.
    pause
    exit /b 1
)

echo.
echo [5/5] Waiting for services to be ready...
echo.

:: Wait for services
timeout /t 5 /nobreak >nul

:: Check container status
echo Checking container status...
docker-compose ps

echo.
echo ========================================
echo Services Started Successfully!
echo ========================================
echo.
echo Access your services:
echo.
echo  🛍️  Dashboard:  http://localhost:8501
echo  📊 API Docs:    http://localhost:8000/docs
echo. 🔐 API:         http://localhost:8000
echo  🌸 Flower:      http://localhost:5555
echo   
echo Useful commands:
echo   - View logs:    docker-compose logs -f
echo   - Stop:         docker-compose down
echo   - Restart:      docker-compose restart
echo   - Status:       docker-compose ps
echo.
echo Or use helper scripts:
echo   - check_logs.bat  - View service logs
echo   - diagnose.bat    - Run diagnostics
echo   - rebuild.bat     - Force rebuild
echo.

:: Ask if user wants to view logs
set /p viewlogs="View live logs now? (yes/no): "
if /i "%viewlogs%"=="yes" (
    echo.
    echo Press Ctrl+C to stop viewing logs...
    timeout /t 2 /nobreak >nul
    docker-compose logs -f
) else (
    echo.
    echo Containers are running in the background.
    echo Open Docker Desktop to see them in the Containers tab.
    echo.
    pause
)
