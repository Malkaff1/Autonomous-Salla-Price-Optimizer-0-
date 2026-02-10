@echo off
echo Installing plotly in running containers...
echo.

echo [1/2] Installing in dashboard container...
docker exec salla-dashboard pip install plotly>=5.18.0
echo.

echo [2/2] Restarting dashboard...
docker-compose restart dashboard
echo.

echo Done! Wait 10 seconds then refresh your browser at http://localhost:8501
timeout /t 10
