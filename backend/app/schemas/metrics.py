"""
Pydantic schemas for Prometheus & OpenTelemetry Regulatory Observability.
"""

from typing import Any

from pydantic import BaseModel, Field


class TrafficStats(BaseModel):
    total_requests: int = Field(default=0, description="Total HTTP API calls processed")
    total_errors: int = Field(default=0, description="Total 4xx and 5xx error responses")
    error_rate_pct: float = Field(default=0.0, description="Percentage of requests resulting in errors")
    requests_by_endpoint: dict[str, int] = Field(default_factory=dict)
    requests_by_status: dict[str, int] = Field(default_factory=dict)


class LLMTelemetryStats(BaseModel):
    total_prompt_tokens: int = Field(default=0)
    total_completion_tokens: int = Field(default=0)
    total_tokens: int = Field(default=0)


class SemanticCacheStats(BaseModel):
    total_queries: int = Field(default=0)
    exact_hits: int = Field(default=0)
    semantic_hits: int = Field(default=0)
    misses: int = Field(default=0)
    hit_ratio_pct: float = Field(default=0.0)


class RegulatoryFindingsStats(BaseModel):
    total_violations: int = Field(default=0)
    by_severity: dict[str, int] = Field(default_factory=dict)
    by_framework: dict[str, int] = Field(default_factory=dict)


class MetricsSummaryResponse(BaseModel):
    status: str = Field(default="HEALTHY")
    uptime_seconds: float = Field(default=0.0)
    region: str = Field(default="eu-central-1-fra (Frankfurt)")
    traffic: TrafficStats
    llm_telemetry: LLMTelemetryStats
    semantic_cache: SemanticCacheStats
    active_sse_streams: int = Field(default=0)
    regulatory_findings: RegulatoryFindingsStats


class TraceSpanItem(BaseModel):
    name: str
    trace_id: str
    span_id: str
    parent_span_id: str | None = None
    status: str = "OK"
    status_description: str | None = None
    duration_ms: float = 0.0
    timestamp: str
    attributes: dict[str, Any] = Field(default_factory=dict)


class RecentTracesResponse(BaseModel):
    total_spans: int
    active_trace_id: str | None = None
    spans: list[TraceSpanItem]
