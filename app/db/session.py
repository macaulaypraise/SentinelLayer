import os
from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.config import settings

#  Force fetch from the OS environment to prevent Pydantic string masking
raw_db_url = os.getenv("DATABASE_URL")

# Fallback for local development if the OS variable isn't set
if not raw_db_url:
    raw_db_url = str(settings.database_url)

#  Inject the async driver
if raw_db_url.startswith("postgresql://"):
    raw_db_url = raw_db_url.replace("postgresql://", "postgresql+asyncpg://", 1)

engine = create_async_engine(
    raw_db_url,
    pool_pre_ping=True,
    pool_size=100,
    max_overflow=50,
    pool_timeout=30.0,
    echo=settings.app_env == "development",
)
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


class Base(DeclarativeBase):
    pass


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
