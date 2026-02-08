@echo off
echo ========================================
echo   Salla Price Optimizer Dashboard
echo ========================================
echo.
echo Starting dashboard on port 8501...
echo Dashboard will open at: http://localhost:8501
echo.
echo Press Ctrl+C to stop the dashboard
echo ========================================
echo.

REM Try the working dashboard first
streamlit run dashboard_working.py --server.port 8501 --server.headless false

pause