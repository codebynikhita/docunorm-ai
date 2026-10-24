from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Annotated, Any

from fastapi import Depends, FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from redis.asyncio import Redis
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.api import api_router
from app.core.config import get_settings
from app.core.db import get_session, init_db

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Application lifespan manager.
    Executes database table creation and connectivity verification on startup,
    and handles graceful resource disposal on shutdown.
    """
    print("🚀 [Startup] Ensuring database schema is ready...")
    init_db()

    # Verify Redis connectivity on startup
    redis = Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        decode_responses=True,
    )
    try:
        await redis.ping()
        print("✅ [Startup] Redis connection established.")
    except Exception as e:
        print(f"⚠️ [Startup] Redis connectivity warning: {e}")
    finally:
        await redis.aclose()

    yield

    print("🛑 [Shutdown] Disposing application resources...")


app = FastAPI(
    title="DocuNorm AI API",
    description=(
        "Enterprise Privacy-First Document Intelligence & Regulatory "
        "Audit Platform (GDPR & EU AI Act compliant)."
    ),
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# Enterprise CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"http://(localhost|127\.0\.0\.1)(:\d+)?",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API v1 Endpoints (Documents, Search, Audit, Chat)
app.include_router(api_router)


@app.get(
    "/health",
    tags=["System"],
    summary="Comprehensive Infrastructure Health Check",
    status_code=status.HTTP_200_OK,
)
async def health_check(
    db: Annotated[AsyncSession, Depends(get_session)],
) -> dict[str, Any]:
    """
    Kubernetes / Docker health probe endpoint.
    Performs live queries against PostgreSQL and Redis to verify complete stack health.
    """
    health_status: dict[str, Any] = {
        "status": "healthy",
        "service": "docunorm-api",
        "environment": settings.APP_ENV,
        "version": "0.1.0",
        "checks": {
            "database": "unknown",
            "redis": "unknown",
        },
    }

    # 1. Probe PostgreSQL connectivity
    try:
        result = await db.execute(text("SELECT 1;"))
        if result.scalar() == 1:
            health_status["checks"]["database"] = "healthy"
    except Exception as e:
        health_status["status"] = "degraded"
        health_status["checks"]["database"] = f"unhealthy: {e!s}"

    # 2. Probe Redis connectivity
    redis = Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        decode_responses=True,
    )
    try:
        if await redis.ping():
            health_status["checks"]["redis"] = "healthy"
    except Exception as e:
        health_status["status"] = "degraded"
        health_status["checks"]["redis"] = f"unhealthy: {e!s}"
    finally:
        await redis.aclose()

    return health_status


@app.get(
    "/",
    tags=["System"],
    summary="Root Welcome Endpoint",
    status_code=status.HTTP_200_OK,
)
async def root() -> dict[str, str]:
    return {
        "message": "Welcome to DocuNorm AI — Enterprise Document Intelligence & Regulatory Audit API",
        "documentation": "/docs",
        "health": "/health",
    }
