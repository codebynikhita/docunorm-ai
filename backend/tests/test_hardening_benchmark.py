"""
Tests for Week 5 Capstone: Enterprise Hardening Benchmark & 100k-Token Stress Test (Day 35).
"""

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.schemas.benchmark import BenchmarkRunRequest
from app.services.hardening_benchmark import hardening_benchmark_engine
from app.services.hardening_pdf_exporter import generate_hardening_benchmark_pdf


@pytest.mark.asyncio
async def test_hardening_benchmark_execution() -> None:
    """Test full execution of the 100k-token enterprise stress benchmark."""
    report = await hardening_benchmark_engine.run_stress_test(
        total_inquiries=25,
        concurrent_streams=5,
        include_ocr_stress=True,
    )

    assert report.benchmark_id.startswith("BENCH-W5-")
    assert report.overall_score_pct >= 95.0
    assert report.status == "CERTIFIED_ENTERPRISE_READY"
    assert report.corpus.total_tokens >= 100_000
    assert len(report.sha256_attestation) == 64
    assert report.sla_compliance_met is True
    assert report.latencies.p50_ms <= report.latencies.p95_ms
    assert report.throughput.requests_per_second > 0
    assert report.cache.deduplication_ratio_pct > 0


@pytest.mark.asyncio
async def test_hardening_pdf_certificate_generation() -> None:
    """Test generating 3-page DIN 5008 Master Certificate PDF."""
    report = await hardening_benchmark_engine.run_stress_test(
        total_inquiries=15,
        concurrent_streams=3,
        include_ocr_stress=False,
    )
    pdf_bytes = generate_hardening_benchmark_pdf(report)
    assert pdf_bytes is not None
    assert pdf_bytes.startswith(b"%PDF")
    assert len(pdf_bytes) > 5000


@pytest.mark.asyncio
async def test_benchmark_api_endpoints() -> None:
    """Test REST API routes for executing benchmarks and downloading certificates."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Run benchmark
        payload = BenchmarkRunRequest(total_inquiries=15, concurrent_inquiries=5)
        run_res = await client.post("/api/v1/benchmark/run", json=payload.model_dump())
        assert run_res.status_code == 200
        run_data = run_res.json()
        assert run_data["status"] == "CERTIFIED_ENTERPRISE_READY"
        assert "sha256_attestation" in run_data

        # 2. Get latest
        latest_res = await client.get("/api/v1/benchmark/latest")
        assert latest_res.status_code == 200
        latest_data = latest_res.json()
        assert latest_data["benchmark_id"] == run_data["benchmark_id"]

        # 3. Export PDF
        pdf_res = await client.get("/api/v1/benchmark/export-certificate-pdf")
        assert pdf_res.status_code == 200
        assert pdf_res.headers["content-type"] == "application/pdf"
        assert len(pdf_res.content) > 5000
