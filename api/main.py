"""
FastAPI application for Deep Researcher API.
Provides REST endpoints and WebSocket streaming for multi-agent research.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from api.config import settings
from api.database.db import init_db
from api.database.checkpointer import get_checkpointer_manager
from api.routes import sessions, websocket


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    print("=" * 60)
    print(f"Starting {settings.app_name}")
    print("=" * 60)

    print("Initializing database...")
    await init_db()

    print("Initializing LangGraph checkpointer...")
    checkpointer_manager = get_checkpointer_manager()
    await checkpointer_manager.initialize()

    print(f"\nAPI ready at http://{settings.api_host}:{settings.api_port}")
    print(f"WebSocket endpoint: ws://{settings.api_host}:{settings.api_port}/ws/{{session_id}}")
    print("=" * 60)

    yield

    # Shutdown
    print("\nShutting down...")
    print("Closing checkpointer...")
    await checkpointer_manager.close()

    print("Application shutdown complete")


# Create FastAPI app
app = FastAPI(title=settings.app_name, lifespan=lifespan, debug=settings.debug)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(sessions.router)
app.include_router(websocket.router)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": settings.app_name,
        "version": "1.0.0",
        "docs": "/docs",
        "websocket": "/ws/{session_id}",
    }


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy", "service": settings.app_name}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "api.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
    )
