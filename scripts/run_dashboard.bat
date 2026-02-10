@echo off
echo Starting Salla Price Optimizer Dashboard...
echo.
echo Dashboard will open in your browser at: http://localhost:8501
echo.
echo Press Ctrl+C to stop the dashboard
echo.
streamlit run dashboard.py --server.port 8501 --server.headless false
pause