from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlmodel import SQLModel, create_engine

from app.core.config import get_settings

settings = get_settings()

# Asynchronous engine for high-throughput API requests
async_engine = create_async_engine(
    settings.async_database_url,
    echo=settings.DEBUG,
    future=True,
    pool_pre_ping=True,
)

# Session factory for generating request-scoped database sessions
async_session_factory = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Synchronous engine for initial table creation and administrative scripts
sync_engine = create_engine(
    settings.sync_database_url,
    echo=settings.DEBUG,
    pool_pre_ping=True,
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency injection for FastAPI routes.
    Provides an async database session per request and guarantees cleanup.
    """
    async with async_session_factory() as session:
        yield session


def init_db() -> None:
    """
    Creates all database tables defined in SQLModel metadata if they do not exist.
    """
    import app.models as _  # noqa: F401

    SQLModel.metadata.create_all(sync_engine)
