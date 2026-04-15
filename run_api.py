#!/usr/bin/env python3
"""
Start script for the Deep Researcher API.
Runs the FastAPI application with uvicorn.
"""

import uvicorn
from api.config import settings

if __name__ == "__main__":
    print(f"Starting {settings.app_name}...")
    print(f"Server will be available at: http://{settings.api_host}:{settings.api_port}")
    print(f"API docs: http://{settings.api_host}:{settings.api_port}/docs")
    print(f"WebSocket: ws://{settings.api_host}:{settings.api_port}/ws/{{session_id}}")
    print("\nPress CTRL+C to stop the server\n")

    uvicorn.run(
        "api.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
        log_level="info",
    )
