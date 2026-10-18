import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.mark.asyncio
async def test_root_endpoint() -> None:
    """
    Smoke test: verify root welcome endpoint returns 200 OK.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "documentation" in data
        assert data["documentation"] == "/docs"


@pytest.mark.asyncio
async def test_health_check_endpoint() -> None:
    """
    Integration test: verify health check probes PostgreSQL and Redis.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["service"] == "docunorm-api"
        assert "checks" in data
        assert "database" in data["checks"]
        assert "redis" in data["checks"]
