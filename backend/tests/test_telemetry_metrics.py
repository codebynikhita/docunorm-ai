"""
Integration and Unit Tests for Prometheus & OpenTelemetry Regulatory Performance Instrumentation (Day 34).
"""

import pytest
from httpx import ASGITransport, AsyncClient

from app.core.metrics import (
    HTTP_REQUEST_DURATION_SECONDS,
    HTTP_REQUESTS_TOTAL,
    generate_prometheus_exposition,
    get_metrics_summary,
)
from app.core.tenant import SIEMENS_TENANT_ID
from app.core.tracing import (
    format_traceparent,
    generate_span_id,
    generate_trace_id,
    get_current_span_id,
    get_current_trace_id,
    get_recent_trace_spans,
    parse_traceparent,
    reset_trace_context,
    set_trace_context,
    trace_span,
)
from app.main import app


@pytest.mark.asyncio
async def test_w3c_traceparent_parsing_and_formatting() -> None:
    """Test standard W3C traceparent parsing and generation."""
    trace_id = generate_trace_id()
    span_id = generate_span_id()
    assert len(trace_id) == 32
    assert len(span_id) == 16

    tp_string = format_traceparent(trace_id, span_id, sampled=True)
    assert tp_string == f"00-{trace_id}-{span_id}-01"

    parsed = parse_traceparent(tp_string)
    assert parsed is not None
    assert parsed[0] == trace_id
    assert parsed[1] == span_id
    assert parsed[2] == "01"

    # Test invalid headers
    assert parse_traceparent(None) is None
    assert parse_traceparent("invalid-header") is None
    assert parse_traceparent("00-00000000000000000000000000000000-00f067aa0ba902b7-01") is None


@pytest.mark.asyncio
async def test_trace_context_propagation() -> None:
    """Test ContextVar-based trace ID and span ID propagation."""
    tid = generate_trace_id()
    sid = generate_span_id()

    tokens = set_trace_context(tid, sid)
    assert get_current_trace_id() == tid
    assert get_current_span_id() == sid

    reset_trace_context(tokens)


@pytest.mark.asyncio
async def test_opentelemetry_trace_span_lifecycle() -> None:
    """Test OpenTelemetry trace_span context manager and ring buffer storage."""
    with trace_span("regulatory_benchmark_span", {"framework": "DORA", "article": "30"}):
        # Nested work
        pass

    spans = get_recent_trace_spans(limit=10)
    assert len(spans) > 0
    latest = spans[0]
    assert latest["name"] == "regulatory_benchmark_span"
    assert latest["status"] == "OK"
    assert latest["attributes"].get("framework") == "DORA"
    assert latest["attributes"].get("article") == "30"
    assert "execution.latency_ms" in latest["attributes"]

    # Test exception handling in span
    with pytest.raises(ValueError):
        with trace_span("failing_span"):
            raise ValueError("Simulated trace failure")

    spans_after_err = get_recent_trace_spans(limit=10)
    failed_span = spans_after_err[0]
    assert failed_span["name"] == "failing_span"
    assert failed_span["status"] == "ERROR"


@pytest.mark.asyncio
async def test_prometheus_exposition_and_summary() -> None:
    """Test Prometheus raw exposition generation and structured summary."""
    HTTP_REQUESTS_TOTAL.labels(
        method="GET",
        endpoint="/api/v1/test",
        status_code="200",
        tenant="siemens",
    ).inc()
    HTTP_REQUEST_DURATION_SECONDS.labels(
        method="GET",
        endpoint="/api/v1/test",
        tenant="siemens",
    ).observe(0.045)

    raw_exposition = generate_prometheus_exposition().decode("utf-8")
    assert "docunorm_http_requests_total" in raw_exposition
    assert "docunorm_active_tenants" in raw_exposition

    summary = get_metrics_summary()
    assert summary["status"] == "HEALTHY"
    assert summary["traffic"]["total_requests"] >= 1
    assert "semantic_cache" in summary
    assert "regulatory_findings" in summary


@pytest.mark.asyncio
async def test_metrics_api_endpoints() -> None:
    """Test /metrics scrape endpoint and /api/v1/metrics REST endpoints via ASGI client."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Prometheus Scrapable Endpoint
        res_metrics = await client.get("/metrics")
        assert res_metrics.status_code == 200
        assert "text/plain" in res_metrics.headers["content-type"]
        assert "docunorm_" in res_metrics.text

        # 2. W3C Traceparent Header Ingestion & Propagation
        test_tid = "4bf92f3577b34da6a3ce929d0e0e4736"
        test_sid = "00f067aa0ba902b7"
        in_traceparent = f"00-{test_tid}-{test_sid}-01"

        res_summary = await client.get(
            "/api/v1/metrics/summary",
            headers={
                "traceparent": in_traceparent,
                "X-Tenant-ID": str(SIEMENS_TENANT_ID),
            },
        )
        assert res_summary.status_code == 200
        assert "traceparent" in res_summary.headers
        assert res_summary.headers["X-Trace-ID"] == test_tid
        assert res_summary.headers["X-Tenant-ID"] == str(SIEMENS_TENANT_ID)

        body = res_summary.json()
        assert body["status"] == "HEALTHY"
        assert "traffic" in body
        assert "llm_telemetry" in body
        assert "semantic_cache" in body

        # 3. Traces Inspector Endpoint
        res_traces = await client.get("/api/v1/metrics/traces?limit=10")
        assert res_traces.status_code == 200
        traces_body = res_traces.json()
        assert "spans" in traces_body
        assert "total_spans" in traces_body
