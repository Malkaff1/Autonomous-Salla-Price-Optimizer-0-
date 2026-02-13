#!/usr/bin/env python3
"""
Simple API starter script that ensures uvicorn binds to 0.0.0.0
"""
import sys
import os

# Add parent directory to Python path so we can import api module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "api.oauth_handler:app",
        host="0.0.0.0",
        port=8000,
        log_level="info",
        timeout_keep_alive=120
    )
