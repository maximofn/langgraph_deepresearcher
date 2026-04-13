"""
FastAPI application for Deep Researcher API.

Provides REST endpoints and WebSocket streaming for the LangGraph multi-agent
research pipeline.
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

from api.config import settings
from api.database.checkpointer import get_checkpointer_manager
from api.database.db import init_db
from api.routes import sessions, websocket
from api.utils.exceptions import APIException, ErrorResponse
from api.utils.logging import configure_logging
from api.utils.paths import ensure_src_on_path
from api.websockets.message_interceptor import install_interceptor

# Make src/* importable before anything in the request path touches it.
ensure_src_on_path()

configure_logging(level=settings.log_level, json_format=settings.log_json)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    logger.info("Starting %s", settings.app_name)

    logger.info("Initializing database")
    await init_db()

    logger.info("Initializing LangGraph checkpointer")
    checkpointer_manager = get_checkpointer_manager()
    await checkpointer_manager.initialize()

    logger.info("Installing message interceptor")
    install_interceptor()

    logger.info(
        "API ready at http://%s:%s", settings.api_host, settings.api_port
    )

    yield

    logger.info("Shutting down; closing checkpointer")
    await checkpointer_manager.close()


app = FastAPI(title=settings.app_name, lifespan=lifespan, debug=settings.debug)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------- Rate limiting ----------
if settings.enable_rate_limit:
    try:
        from slowapi import Limiter, _rate_limit_exceeded_handler
        from slowapi.errors import RateLimitExceeded
        from slowapi.middleware import SlowAPIMiddleware
        from slowapi.util import get_remote_address

        limiter = Limiter(
            key_func=get_remote_address,
            default_limits=[settings.rate_limit_create_session],
        )
        app.state.limiter = limiter
        app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
        app.add_middleware(SlowAPIMiddleware)
    except ImportError:
        logger.warning("slowapi not installed; rate limiting disabled")
        app.state.limiter = None
else:
    app.state.limiter = None


# ---------- Metrics ----------
if settings.enable_metrics:
    try:
        from prometheus_fastapi_instrumentator import Instrumentator

        Instrumentator().instrument(app).expose(app, endpoint="/metrics")
    except ImportError:
        logger.warning("prometheus_fastapi_instrumentator not installed; metrics disabled")


# ---------- Exception handlers ----------
@app.exception_handler(APIException)
async def api_exception_handler(request: Request, exc: APIException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(code=exc.code, message=exc.message, details=exc.details).model_dump(),
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    return JSONResponse(
        status_code=422,
        content=ErrorResponse(
            code="validation_error",
            message="Request validation failed",
            details={"errors": exc.errors()},
        ).model_dump(),
    )


@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError) -> JSONResponse:
    logger.exception("Database error on %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(code="database_error", message="Internal database error").model_dump(),
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("Unhandled error on %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(code="internal_error", message="Internal server error").model_dump(),
    )


# ---------- Routers ----------
app.include_router(sessions.router)
app.include_router(websocket.router)


@app.get("/")
async def root():
    return {
        "message": settings.app_name,
        "version": "1.0.0",
        "docs": "/docs",
        "websocket": "/ws/{session_id}",
    }


@app.get("/health")
async def health():
    return {"status": "healthy", "service": settings.app_name}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "api.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
    )
