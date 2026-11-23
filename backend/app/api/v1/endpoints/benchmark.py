"""
FastAPI REST Endpoints for Week 5 Capstone: Enterprise Hardening Benchmark & 100k-Token Stress Test.
"""

from fastapi import APIRouter, Response

from app.schemas.benchmark import BenchmarkRunRequest, HardeningBenchmarkReport
from app.services.hardening_benchmark import hardening_benchmark_engine
from app.services.hardening_pdf_exporter import generate_hardening_benchmark_pdf

router = APIRouter()


@router.post(
    "/run",
    response_model=HardeningBenchmarkReport,
    summary="Execute Week 5 Capstone Enterprise Hardening Benchmark & 100k-Token Stress Test",
    description="Simulates concurrent multi-tenant audit traffic, measures P50/P95/P99 latency, tests semantic cache, and signs SHA-256 seal.",
)
async def run_hardening_benchmark(payload: BenchmarkRunRequest | None = None) -> HardeningBenchmarkReport:
    """Execute the stress test benchmark."""
    req = payload or BenchmarkRunRequest()
    report = await hardening_benchmark_engine.run_stress_test(
        total_inquiries=req.total_inquiries,
        concurrent_streams=req.concurrent_inquiries,
        include_ocr_stress=req.include_ocr_stress,
        target_tenant=req.target_tenant,
    )
    return report


@router.get(
    "/latest",
    response_model=HardeningBenchmarkReport,
    summary="Get Most Recent Hardening Benchmark Report",
    description="Returns the cached results of the latest benchmark run or triggers a baseline evaluation if none exists.",
)
async def get_latest_benchmark() -> HardeningBenchmarkReport:
    """Retrieve latest benchmark report."""
    if hardening_benchmark_engine.latest_report:
        return hardening_benchmark_engine.latest_report
    # Auto-run baseline
    return await hardening_benchmark_engine.run_stress_test(total_inquiries=40, concurrent_streams=10)


@router.get(
    "/export-certificate-pdf",
    summary="Export Official DIN 5008 Master Hardening Benchmark PDF Certificate",
    description="Generates an executive 3-page DIN 5008 compliance and SLA certificate signed with SHA-256 ledger seal.",
)
async def export_benchmark_certificate_pdf() -> Response:
    """Export the signed 3-page DIN 5008 PDF certificate."""
    report = hardening_benchmark_engine.latest_report
    if not report:
        report = await hardening_benchmark_engine.run_stress_test(total_inquiries=40, concurrent_streams=10)

    pdf_bytes = generate_hardening_benchmark_pdf(report)
    filename = f"DOCUNORM_ENTERPRISE_HARDENING_ZERTIFIKAT_{report.benchmark_id}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
