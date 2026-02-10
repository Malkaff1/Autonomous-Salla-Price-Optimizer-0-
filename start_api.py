#!/usr/bin/env python3
"""
Simple API starter script that ensures uvicorn binds to 0.0.0.0
"""
import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "api.oauth_handler:app",
        host="0.0.0.0",
        port=8000,
        log_level="info",
        timeout_keep_alive=120
    )
