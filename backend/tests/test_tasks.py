import uuid
import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.services.tasks import get_task_progress, set_task_progress


@pytest.mark.asyncio
async def test_set_and_get_task_progress() -> None:
    """
    Verify real-time Redis task progress tracking.
    """
    doc_id = uuid.uuid4()
    await set_task_progress(
        document_id=doc_id,
        status="processing",
        progress=45,
        stage="redacting_german_pii",
    )

    info = await get_task_progress(doc_id)
    assert info["document_id"] == str(doc_id)
    assert info["status"] == "processing"
    assert info["progress"] == 45
    assert info["stage"] == "redacting_german_pii"


@pytest.mark.asyncio
async def test_task_progress_endpoint() -> None:
    """
    Verify GET /api/v1/documents/{document_id}/task-progress returns valid status.
    """
    doc_id = uuid.uuid4()
    await set_task_progress(
        document_id=doc_id,
        status="ready",
        progress=100,
        stage="ingestion_complete",
    )

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get(f"/api/v1/documents/{doc_id}/task-progress")
        assert res.status_code == 200
        data = res.json()
        assert data["document_id"] == str(doc_id)
        assert data["status"] == "ready"
        assert data["progress"] == 100
