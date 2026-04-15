from contextlib import asynccontextmanager
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from typing import AsyncGenerator, AsyncIterator

from api.config import settings
from api.database.models import Base


# Create async engine
engine = create_async_engine(
    settings.database_url, echo=settings.debug, future=True
)

# Create async session maker
async_session_maker = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


_RESEARCH_EVENT_EXTRA_COLUMNS = {
    "timestamp": "FLOAT",
    "message_type": "VARCHAR(32)",
    "message_subtype": "VARCHAR(64)",
    "agent": "VARCHAR(32)",
    "tool_name": "VARCHAR(128)",
    "tool_args": "JSON",
    "tool_call_id": "VARCHAR(128)",
    "metadata_json": "JSON",
}


async def init_db():
    """Initialize database tables and apply lightweight SQLite migrations."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

        # Idempotent add-column migration for the research_events table.
        result = await conn.execute(text("PRAGMA table_info(research_events)"))
        existing = {row[1] for row in result.fetchall()}
        for col_name, col_type in _RESEARCH_EVENT_EXTRA_COLUMNS.items():
            if col_name not in existing:
                await conn.execute(
                    text(f"ALTER TABLE research_events ADD COLUMN {col_name} {col_type}")
                )

        # Idempotent add-column migration for the sessions table.
        result = await conn.execute(text("PRAGMA table_info(sessions)"))
        existing_sessions_cols = {row[1] for row in result.fetchall()}
        if "models_config" not in existing_sessions_cols:
            await conn.execute(
                text("ALTER TABLE sessions ADD COLUMN models_config JSON")
            )
        if "user_name" not in existing_sessions_cols:
            await conn.execute(
                text("ALTER TABLE sessions ADD COLUMN user_name VARCHAR(200)")
            )
        if "user_email" not in existing_sessions_cols:
            await conn.execute(
                text("ALTER TABLE sessions ADD COLUMN user_email VARCHAR(320)")
            )


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency yielding an async DB session."""
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()


@asynccontextmanager
async def db_session_context() -> AsyncIterator[AsyncSession]:
    """Standalone async context manager for DB sessions (for background tasks)."""
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()
