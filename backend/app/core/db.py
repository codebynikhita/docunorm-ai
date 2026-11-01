from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlmodel import SQLModel, create_engine

from app.core.config import get_settings

settings = get_settings()

import os
import socket
from collections.abc import AsyncGenerator
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlmodel import SQLModel, create_engine

from app.core.config import get_settings

settings = get_settings()


def _is_postgres_online(host: str, port: int) -> bool:
    """Checks whether the PostgreSQL daemon is reachable within 200ms."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(0.2)
        res = sock.connect_ex((host, port))
        sock.close()
        return res == 0
    except Exception:
        return False


# Determine database URLs (prefer PostgreSQL, fallback gracefully to SQLite)
_postgres_available = _is_postgres_online(settings.POSTGRES_HOST, settings.POSTGRES_PORT)
_sqlite_file = Path(__file__).resolve().parent.parent.parent / "docunorm_local.db"

if _postgres_available and os.getenv("FORCE_SQLITE", "0") != "1":
    _async_url = settings.async_database_url
    _sync_url = settings.sync_database_url
    _is_sqlite = False
else:
    _async_url = f"sqlite+aiosqlite:///{_sqlite_file}"
    _sync_url = f"sqlite:///{_sqlite_file}"
    _is_sqlite = True
    print(f"📦 [Database] Operating in persistent SQLite Sovereign Mode ({_sqlite_file.name})")

# Asynchronous engine for high-throughput API requests
async_engine = create_async_engine(
    _async_url,
    echo=False,
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
    _sync_url,
    echo=False,
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
