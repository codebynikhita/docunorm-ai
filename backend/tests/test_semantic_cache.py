from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient
from sqlmodel import select

from app.core.db import async_session_factory
from app.core.tenant import SIEMENS_TENANT_ID, tenant_context
from app.main import app
from app.models.document import Document
from app.services.semantic_cache import SemanticCacheService, semantic_cache


@pytest.mark.asyncio
async def test_semantic_cache_exact_and_semantic_hits():
    """
    Tests exact hash deduplication (1.0) and semantic vector cosine similarity match (>= 0.90).
    """
    cache = SemanticCacheService(threshold=0.88, ttl_seconds=3600)
    tenant_id = uuid4()
    doc_id = uuid4()

    sample_response = {
        "finding_summary": "Pursuant to DORA Art. 30(2), the exit transition period is 60 days.",
        "framework": "DORA",
        "status": "COMPLIANT",
        "citations": [
            {
                "source_tag": "[SOURCE_1]",
                "chunk_id": str(uuid4()),
                "page_number": 2,
                "bounding_box": [50.0, 100.0, 500.0, 160.0],
                "content": "Kündigungsfrist von 60 Tagen gem. DORA Art. 30",
            }
        ],
    }

    # Store first query
    primary_query = "What is the exit termination period under DORA Art. 30?"
    await cache.set(
        tenant_id=tenant_id,
        document_id=doc_id,
        query=primary_query,
        framework="DORA",
        lang="EN",
        response_data=sample_response,
    )

    # 1. Exact match test (with slight casing/punctuation differences)
    exact_res = await cache.get(
        tenant_id=tenant_id,
        document_id=doc_id,
        query="what is the exit termination period under dora art. 30",
        framework="DORA",
        lang="EN",
    )
    assert exact_res.hit is True
    assert exact_res.cache_type == "exact"
    assert exact_res.similarity_score == 1.0
    assert exact_res.response_data == sample_response
    assert exact_res.telemetry.cached is True

    # 2. Semantic similarity match test (substantially similar query)
    semantic_query = "exit termination period under DORA Art. 30"
    sem_res = await cache.get(
        tenant_id=tenant_id,
        document_id=doc_id,
        query=semantic_query,
        framework="DORA",
        lang="EN",
    )
    assert sem_res.hit is True
    assert sem_res.cache_type in ("exact", "semantic")
    assert sem_res.similarity_score >= 0.88

    # 3. Dissimilar query test -> Cache Miss
    dissimilar_query = "What are the rules regarding ZUGFeRD 2.3 XML Leitweg-ID?"
    miss_res = await cache.get(
        tenant_id=tenant_id,
        document_id=doc_id,
        query=dissimilar_query,
        framework="DORA",
        lang="EN",
    )
    assert miss_res.hit is False
    assert miss_res.response_data is None


@pytest.mark.asyncio
async def test_semantic_cache_invalidation_and_stats():
    """
    Verifies document-level cache purging and performance metrics tracking.
    """
    cache = SemanticCacheService(threshold=0.90, ttl_seconds=3600)
    tenant_id = uuid4()
    doc_a = uuid4()
    doc_b = uuid4()

    dummy_payload = {"finding_summary": "Test", "citations": []}

    await cache.set(tenant_id, doc_a, "Query A1", "DORA", "EN", dummy_payload)
    await cache.set(tenant_id, doc_a, "Query A2", "DORA", "EN", dummy_payload)
    await cache.set(tenant_id, doc_b, "Query B1", "DORA", "EN", dummy_payload)

    # Invalidate doc_a
    purged_count = await cache.invalidate_document(doc_a, tenant_id=tenant_id)
    assert purged_count >= 2

    # Verify doc_a is gone
    check_a = await cache.get(tenant_id, doc_a, "Query A1", "DORA", "EN")
    assert check_a.hit is False

    # Verify doc_b remains intact
    check_b = await cache.get(tenant_id, doc_b, "Query B1", "DORA", "EN")
    assert check_b.hit is True

    stats = await cache.get_stats()
    assert stats.hits >= 1
    assert stats.misses >= 1
    assert stats.total_queries >= 2
    assert stats.hit_ratio > 0.0
    assert stats.estimated_tokens_saved >= 850


@pytest.mark.asyncio
async def test_cache_api_endpoints():
    """
    Tests GET /api/v1/cache/stats and POST /api/v1/cache/invalidate endpoints.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Fetch cache stats
        res = await client.get("/api/v1/cache/stats")
        assert res.status_code == 200
        data = res.json()
        assert "storage_backend" in data
        assert "total_queries" in data
        assert "hit_ratio" in data
        assert "estimated_tokens_saved" in data
        assert "estimated_latency_saved_ms" in data

        # 2. Invalidate cache
        inv_res = await client.post(
            "/api/v1/cache/invalidate",
            json={"document_id": str(uuid4())},
        )
        assert inv_res.status_code == 200
        inv_data = inv_res.json()
        assert inv_data["status"] == "success"


@pytest.mark.asyncio
async def test_audit_endpoint_caching_lifecycle():
    """
    Tests end-to-end audit caching: first call computes finding, second call hits cache with telemetry.
    """
    async with async_session_factory() as session:
        with tenant_context(SIEMENS_TENANT_ID):
            doc_stmt = select(Document).where(Document.tenant_id == SIEMENS_TENANT_ID)
            res = await session.execute(doc_stmt)
            doc = res.scalars().first()
            assert doc is not None

    # Clear cache before test
    await semantic_cache.clear_all()

    transport = ASGITransport(app=app)
    headers = {"X-Tenant-ID": "siemens-ag"}
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        audit_payload = {
            "query": "Welche Kündigungsfrist gilt für den Ausstieg?",
            "framework": "DORA",
            "lang": "DE",
        }

        # First Call: Cache Miss (generates and stores)
        res1 = await client.post(
            f"/api/v1/documents/{doc.id}/audit",
            json=audit_payload,
            headers=headers,
        )
        assert res1.status_code == 200
        data1 = res1.json()
        assert "finding_summary" in data1
        assert data1.get("cache_telemetry") is not None
        assert data1["cache_telemetry"]["cached"] is False

        # Second Call: Exact Hash Cache Hit
        res2 = await client.post(
            f"/api/v1/documents/{doc.id}/audit",
            json=audit_payload,
            headers=headers,
        )
        assert res2.status_code == 200
        data2 = res2.json()
        assert data2.get("cache_telemetry") is not None
        assert data2["cache_telemetry"]["cached"] is True
        assert data2["cache_telemetry"]["cache_type"] == "exact"
        assert data2["cache_telemetry"]["saved_latency_ms"] is not None

        # Third Call: Streaming SSE Cache Hit
        stream_res = await client.post(
            f"/api/v1/documents/{doc.id}/audit-stream",
            json=audit_payload,
            headers=headers,
        )
        assert stream_res.status_code == 200
        assert "text/event-stream" in stream_res.headers.get("content-type", "")
        stream_text = stream_res.text
        assert "cache_hit" in stream_text
        assert "event: done" in stream_text
