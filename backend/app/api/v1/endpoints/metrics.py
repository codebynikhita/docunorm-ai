"""
Endpoints for Prometheus Observability and OpenTelemetry Tracing inspection.
"""

from fastapi import APIRouter, Query, Response

from app.core.metrics import generate_prometheus_exposition, get_metrics_summary
from app.core.tracing import get_current_trace_id, get_recent_trace_spans
from app.schemas.metrics import MetricsSummaryResponse, RecentTracesResponse

router = APIRouter()


@router.get(
    "/summary",
    response_model=MetricsSummaryResponse,
    summary="Get aggregated Prometheus & OpenTelemetry metrics summary",
    description="Returns high-level API traffic, LLM latency, cache efficiency, and regulatory findings.",
)
async def get_summary() -> MetricsSummaryResponse:
    """Return structured JSON observability summary."""
    data = get_metrics_summary()
    return MetricsSummaryResponse(**data)


@router.get(
    "/traces",
    response_model=RecentTracesResponse,
    summary="Get recent OpenTelemetry distributed trace spans",
    description="Returns the ring-buffered in-memory trace spans with W3C trace_id, duration, and metadata.",
)
async def get_recent_traces(
    limit: int = Query(default=30, ge=1, le=100, description="Max number of spans to return")
) -> RecentTracesResponse:
    """Return recent in-memory trace spans for live telemetry inspector."""
    spans = get_recent_trace_spans(limit=limit)
    active_tid = get_current_trace_id()
    return RecentTracesResponse(
        total_spans=len(spans),
        active_trace_id=active_tid,
        spans=spans,
    )


@router.get(
    "/raw",
    summary="Raw Prometheus Exposition Format",
    description="Returns Prometheus-formatted metrics text for scraping or administrative inspection.",
)
async def get_raw_metrics() -> Response:
    """Scrapable Prometheus text exposition endpoint."""
    content = generate_prometheus_exposition()
    return Response(
        content=content,
        media_type="text/plain; version=0.0.4; charset=utf-8",
    )
