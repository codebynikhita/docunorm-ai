"""
DocuNorm Prometheus Observability & Regulatory Performance Metrics Registry.

Defines Prometheus Counters, Histograms, and Gauges for:
- API Traffic & HTTP Latencies
- LLM Token Consumption & Inference Latencies
- Semantic Cache Operations & Deduplication
- Active SSE Audit Streams
- Regulatory Compliance Findings & Tamper-Evident Ledger Events
"""

from __future__ import annotations

import time
from typing import Any

import prometheus_client as prom

# Custom CollectorRegistry to keep DocuNorm metrics isolated and clean
metrics_registry = prom.CollectorRegistry(auto_describe=True)

# 1. HTTP Traffic & Latency
HTTP_REQUESTS_TOTAL = prom.Counter(
    "docunorm_http_requests_total",
    "Total count of HTTP requests processed by DocuNorm API",
    ["method", "endpoint", "status_code", "tenant"],
    registry=metrics_registry,
)

HTTP_REQUEST_DURATION_SECONDS = prom.Histogram(
    "docunorm_http_request_duration_seconds",
    "HTTP request latency in seconds",
    ["method", "endpoint", "tenant"],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0),
    registry=metrics_registry,
)

# 2. LLM Inference & Token Consumption
LLM_INFERENCE_DURATION_SECONDS = prom.Histogram(
    "docunorm_llm_inference_duration_seconds",
    "Duration of LLM regulatory audits and reasoning calls in seconds",
    ["framework", "model", "status", "tenant"],
    buckets=(0.1, 0.25, 0.5, 1.0, 2.0, 5.0, 10.0, 20.0),
    registry=metrics_registry,
)

LLM_TOKENS_TOTAL = prom.Counter(
    "docunorm_llm_tokens_total",
    "Total tokens consumed or generated during regulatory audits",
    ["framework", "type", "tenant"],  # type: prompt | completion
    registry=metrics_registry,
)

COMPLIANCE_VIOLATIONS_TOTAL = prom.Counter(
    "docunorm_compliance_violations_total",
    "Total compliance violations detected across regulatory frameworks",
    ["framework", "severity", "tenant"],  # severity: CRITICAL | HIGH | MEDIUM | LOW
    registry=metrics_registry,
)

# 3. Dynamic Semantic Cache Deduplication
SEMANTIC_CACHE_OPERATIONS_TOTAL = prom.Counter(
    "docunorm_semantic_cache_operations_total",
    "Semantic cache queries, hits, and invalidations",
    ["operation", "result", "tenant"],  # operation: lookup | write | evict; result: exact_hit | semantic_hit | miss | success
    registry=metrics_registry,
)

# 4. Real-Time Streaming & Concurrency
ACTIVE_AUDIT_STREAMS = prom.Gauge(
    "docunorm_active_audit_streams",
    "Number of active Server-Sent Events (SSE) live audit sessions",
    ["tenant"],
    registry=metrics_registry,
)

# 5. Ingestion & Audit Ledger Events
DOCUMENT_INGESTION_DURATION_SECONDS = prom.Histogram(
    "docunorm_document_ingestion_duration_seconds",
    "Latency of document ingestion and parsing pipeline in seconds",
    ["mode", "tenant"],  # mode: text | ocr_raster | hybrid
    buckets=(0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0),
    registry=metrics_registry,
)

REGULATORY_AUDIT_EVENTS_TOTAL = prom.Counter(
    "docunorm_regulatory_audit_events_total",
    "Count of tamper-evident SHA-256 audit ledger events generated",
    ["event_type", "tenant"],
    registry=metrics_registry,
)

ACTIVE_TENANTS = prom.Gauge(
    "docunorm_active_tenants",
    "Number of active tenants registered in system",
    registry=metrics_registry,
)
ACTIVE_TENANTS.set(4)  # Canonical: Siemens, Deutsche Bank, Allianz, BMW

# System start timestamp for uptime calculation
_SYSTEM_START_TIME = time.time()


def generate_prometheus_exposition() -> bytes:
    """Export all registered metrics in standard Prometheus text exposition format."""
    return prom.generate_latest(metrics_registry)


def get_metrics_summary() -> dict[str, Any]:
    """
    Compute structured telemetry summary from live Prometheus metrics.
    Suitable for frontend executive and auditor dashboards.
    """
    uptime_sec = round(time.time() - _SYSTEM_START_TIME, 1)

    total_requests = 0
    total_errors = 0
    requests_by_endpoint: dict[str, int] = {}
    requests_by_status: dict[str, int] = {}

    for metric in metrics_registry.collect():
        if metric.name in ("docunorm_http_requests", "docunorm_http_requests_total"):
            for sample in metric.samples:
                if sample.name.endswith("_total"):
                    val = int(sample.value)
                    total_requests += val
                    ep = sample.labels.get("endpoint", "unknown")
                    sc = sample.labels.get("status_code", "200")
                    requests_by_endpoint[ep] = requests_by_endpoint.get(ep, 0) + val
                    requests_by_status[sc] = requests_by_status.get(sc, 0) + val
                    if sc.startswith("4") or sc.startswith("5"):
                        total_errors += val

    error_rate = round((total_errors / total_requests * 100), 2) if total_requests > 0 else 0.0

    # Token counts
    tokens_prompt = 0
    tokens_completion = 0
    for metric in metrics_registry.collect():
        if metric.name in ("docunorm_llm_tokens", "docunorm_llm_tokens_total"):
            for sample in metric.samples:
                if sample.name.endswith("_total"):
                    ttype = sample.labels.get("type", "prompt")
                    val = int(sample.value)
                    if ttype == "prompt":
                        tokens_prompt += val
                    else:
                        tokens_completion += val

    # Violations by framework & severity
    violations_by_framework: dict[str, int] = {}
    violations_by_severity: dict[str, int] = {
        "CRITICAL": 0,
        "HIGH": 0,
        "MEDIUM": 0,
        "LOW": 0,
    }
    for metric in metrics_registry.collect():
        if metric.name in ("docunorm_compliance_violations", "docunorm_compliance_violations_total"):
            for sample in metric.samples:
                if sample.name.endswith("_total"):
                    fw = sample.labels.get("framework", "UNKNOWN")
                    sev = sample.labels.get("severity", "LOW")
                    val = int(sample.value)
                    violations_by_framework[fw] = violations_by_framework.get(fw, 0) + val
                    violations_by_severity[sev] = violations_by_severity.get(sev, 0) + val

    # Active streams count
    active_streams = 0
    for metric in metrics_registry.collect():
        if metric.name == "docunorm_active_audit_streams":
            for sample in metric.samples:
                active_streams += int(sample.value)

    # Cache stats
    cache_exact_hits = 0
    cache_semantic_hits = 0
    cache_misses = 0
    for metric in metrics_registry.collect():
        if metric.name in ("docunorm_semantic_cache_operations", "docunorm_semantic_cache_operations_total"):
            for sample in metric.samples:
                if sample.name.endswith("_total"):
                    res = sample.labels.get("result", "")
                    val = int(sample.value)
                    if res == "exact_hit":
                        cache_exact_hits += val
                    elif res == "semantic_hit":
                        cache_semantic_hits += val
                    elif res == "miss":
                        cache_misses += val

    total_cache_queries = cache_exact_hits + cache_semantic_hits + cache_misses
    cache_hit_ratio = (
        round(((cache_exact_hits + cache_semantic_hits) / total_cache_queries) * 100, 1)
        if total_cache_queries > 0
        else 0.0
    )

    return {
        "status": "HEALTHY",
        "uptime_seconds": uptime_sec,
        "region": "eu-central-1-fra (Frankfurt)",
        "traffic": {
            "total_requests": total_requests,
            "total_errors": total_errors,
            "error_rate_pct": error_rate,
            "requests_by_endpoint": requests_by_endpoint,
            "requests_by_status": requests_by_status,
        },
        "llm_telemetry": {
            "total_prompt_tokens": tokens_prompt,
            "total_completion_tokens": tokens_completion,
            "total_tokens": tokens_prompt + tokens_completion,
        },
        "semantic_cache": {
            "total_queries": total_cache_queries,
            "exact_hits": cache_exact_hits,
            "semantic_hits": cache_semantic_hits,
            "misses": cache_misses,
            "hit_ratio_pct": cache_hit_ratio,
        },
        "active_sse_streams": active_streams,
        "regulatory_findings": {
            "total_violations": sum(violations_by_severity.values()),
            "by_severity": violations_by_severity,
            "by_framework": violations_by_framework,
        },
    }
