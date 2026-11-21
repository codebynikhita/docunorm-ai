from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.endpoints.documents import get_or_create_default_tenant_and_user
from app.core.db import get_session
from app.schemas.cache import (
    CacheInvalidateRequest,
    CacheInvalidateResponse,
    CacheStatsResponse,
)
from app.services.semantic_cache import semantic_cache

router = APIRouter(prefix="/cache", tags=["Semantic Cache & Deduplication"])


@router.get(
    "/stats",
    response_model=CacheStatsResponse,
    summary="Retrieve Redis Dynamic Semantic Cache Performance Metrics",
)
async def get_cache_stats() -> CacheStatsResponse:
    """
    Returns real-time operational statistics for the semantic cache:
    - Total queries, exact hits, semantic hits, misses, and hit ratio.
    - Cumulative estimated LLM tokens saved.
    - Cumulative estimated API latency saved in milliseconds.
    - Storage backend (Redis vs. Sovereign In-Memory fallback).
    """
    return await semantic_cache.get_stats()


@router.post(
    "/invalidate",
    response_model=CacheInvalidateResponse,
    summary="Invalidate Semantic Cache Entries",
)
async def invalidate_cache(
    payload: CacheInvalidateRequest,
    db: Annotated[AsyncSession, Depends(get_session)],
) -> CacheInvalidateResponse:
    """
    Invalidates cached inquiries for a specific document or purges all cached entries.
    """
    tenant, _ = await get_or_create_default_tenant_and_user(db)

    if payload.document_id:
        purged = await semantic_cache.invalidate_document(
            document_id=payload.document_id,
            tenant_id=tenant.id,
        )
        return CacheInvalidateResponse(
            status="success",
            document_id=payload.document_id,
            tenant_id=str(tenant.id),
            entries_purged=purged,
        )

    purged = await semantic_cache.clear_all()
    return CacheInvalidateResponse(
        status="success",
        document_id=None,
        tenant_id=str(tenant.id),
        entries_purged=purged,
    )


@router.delete(
    "/documents/{document_id}",
    response_model=CacheInvalidateResponse,
    summary="Purge Semantic Cache for Specific Document",
)
async def invalidate_document_cache(
    document_id: UUID,
    db: Annotated[AsyncSession, Depends(get_session)],
) -> CacheInvalidateResponse:
    """
    Purges all cached audit findings for the specified document ID.
    """
    tenant, _ = await get_or_create_default_tenant_and_user(db)
    purged = await semantic_cache.invalidate_document(
        document_id=str(document_id),
        tenant_id=tenant.id,
    )
    return CacheInvalidateResponse(
        status="success",
        document_id=str(document_id),
        tenant_id=str(tenant.id),
        entries_purged=purged,
    )
