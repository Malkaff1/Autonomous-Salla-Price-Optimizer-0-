#!/usr/bin/env python3
"""
Local dashboard runner - bypasses Streamlit Cloud deployment
"""

import subprocess
import sys
import os
import webbrowser
import time

def run_local_dashboard():
    """Run the dashboard locally without deployment."""
    
    print("🚀 Starting Salla Price Optimizer Dashboard Locally...")
    print("=" * 60)
    
    # Check if dashboard.py exists
    if not os.path.exists("dashboard.py"):
        print("❌ dashboard.py not found!")
        return False
    
    print("✅ Dashboard file found")
    print("🌐 Starting local server...")
    print("📱 Dashboard will open at: http://localhost:8501")
    print("⏹️  Press Ctrl+C to stop the dashboard")
    print("=" * 60)
    
    try:
        # Run streamlit with specific local settings
        cmd = [
            sys.executable, "-m", "streamlit", "run", "dashboard.py",
            "--server.port", "8501",
            "--server.headless", "false",
            "--browser.gatherUsageStats", "false",
            "--server.enableCORS", "false",
            "--server.enableXsrfProtection", "false"
        ]
        
        # Start the process
        process = subprocess.Popen(cmd)
        
        # Wait a moment then open browser
        time.sleep(3)
        webbrowser.open("http://localhost:8501")
        
        # Wait for process to complete
        process.wait()
        
    except KeyboardInterrupt:
        print("\n🛑 Dashboard stopped by user")
        return True
    except Exception as e:
        print(f"❌ Error starting dashboard: {str(e)}")
        return False

if __name__ == "__main__":
    run_local_dashboard()