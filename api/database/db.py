from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from typing import AsyncGenerator

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


async def init_db():
    """Initialize database tables"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for getting database session"""
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()
