import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.services.storage import storage_service


@pytest.mark.asyncio
async def test_upload_rejects_non_pdf() -> None:
    """
    Security check: verify the API rejects non-PDF file formats with HTTP 415.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Simulate an executable or text file upload
        files = {"file": ("malicious_payload.txt", b"plain text content", "text/plain")}
        response = await client.post("/api/v1/documents/upload", files=files)
        assert response.status_code == 415
        data = response.json()
        assert "Unsupported media type" in data["detail"]


def test_storage_service_deterministic_hash() -> None:
    """
    Cryptographic verification: verify SHA-256 produces exact tamper-evident hashes.
    """
    sample_bytes = b"%PDF-1.4 Mock corporate audit report content"
    import hashlib

    expected_hash = hashlib.sha256(sample_bytes).hexdigest()

    saved_path = storage_service.save_document(
        tenant_id="test_tenant",
        sha256_hash=expected_hash,
        content=sample_bytes,
    )

    assert saved_path.exists()
    assert saved_path.name == f"{expected_hash}.pdf"
    assert saved_path.read_bytes() == sample_bytes

    # Cleanup test artifact
    saved_path.unlink()
