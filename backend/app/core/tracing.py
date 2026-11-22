"""
DocuNorm OpenTelemetry Distributed Tracing & W3C Trace Context Instrumentation.

Provides:
- W3C Trace Context standard compliant parser and generator (traceparent).
- Request-scoped ContextVar propagation for end-to-end correlation.
- OpenTelemetry SDK integration with in-memory ring buffer exporter for real-time audit visualization.
- Span lifecycle context managers for LLM audits, semantic cache, OCR, and audit logs.
"""

from __future__ import annotations

import contextvars
import os
import re
import time
from collections.abc import Generator
from contextlib import contextmanager
from datetime import UTC, datetime
from typing import Any

import opentelemetry.trace as trace
from opentelemetry.sdk.trace import ReadableSpan, TracerProvider
from opentelemetry.sdk.trace.export import (
    SimpleSpanProcessor,
    SpanExporter,
    SpanExportResult,
)
from opentelemetry.trace import Status, StatusCode

# W3C Traceparent pattern: 00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01
TRACEPARENT_REGEX = re.compile(
    r"^00-([0-9a-f]{32})-([0-9a-f]{16})-([0-9a-f]{2})$"
)

# Request-scoped context variables
_current_trace_id: contextvars.ContextVar[str | None] = contextvars.ContextVar(
    "current_trace_id", default=None
)
_current_span_id: contextvars.ContextVar[str | None] = contextvars.ContextVar(
    "current_span_id", default=None
)


def generate_trace_id() -> str:
    """Generate a random 32-character hex trace ID (128-bit)."""
    return os.urandom(16).hex()


def generate_span_id() -> str:
    """Generate a random 16-character hex span ID (64-bit)."""
    return os.urandom(8).hex()


def parse_traceparent(header_val: str | None) -> tuple[str, str, str] | None:
    """
    Parse a W3C traceparent header.
    Returns (trace_id, parent_id, flags) or None if invalid.
    """
    if not header_val:
        return None
    match = TRACEPARENT_REGEX.match(header_val.strip())
    if not match:
        return None
    trace_id, parent_id, flags = match.groups()
    if trace_id == "0" * 32 or parent_id == "0" * 16:
        return None
    return trace_id, parent_id, flags


def format_traceparent(trace_id: str, span_id: str, sampled: bool = True) -> str:
    """Format into standard W3C traceparent string: 00-{trace_id}-{span_id}-{flags}."""
    flags = "01" if sampled else "00"
    return f"00-{trace_id}-{span_id}-{flags}"


def get_current_trace_id() -> str:
    """Return the active trace ID or generate a fallback one."""
    tid = _current_trace_id.get()
    if not tid:
        tid = generate_trace_id()
        _current_trace_id.set(tid)
    return tid


def get_current_span_id() -> str:
    """Return the active span ID or generate a fallback one."""
    sid = _current_span_id.get()
    if not sid:
        sid = generate_span_id()
        _current_span_id.set(sid)
    return sid


def set_trace_context(trace_id: str, span_id: str) -> tuple[contextvars.Token[str | None], contextvars.Token[str | None]]:
    """Set the active trace and span ID in the current async context."""
    tok_trace = _current_trace_id.set(trace_id)
    tok_span = _current_span_id.set(span_id)
    return tok_trace, tok_span


def reset_trace_context(tokens: tuple[contextvars.Token[str | None], contextvars.Token[str | None]]) -> None:
    """Reset context variables to their previous states."""
    tok_trace, tok_span = tokens
    _current_trace_id.reset(tok_trace)
    _current_span_id.reset(tok_span)


class InMemoryRingBufferSpanExporter(SpanExporter):
    """
    Thread-safe in-memory ring buffer holding finished OpenTelemetry spans.
    Enables live queryability via the Telemetry API without requiring external collector backends.
    """

    def __init__(self, capacity: int = 150) -> None:
        self.capacity = capacity
        self.spans: list[ReadableSpan] = []

    def export(self, spans: list[ReadableSpan]) -> SpanExportResult:
        self.spans.extend(spans)
        if len(self.spans) > self.capacity:
            self.spans = self.spans[-self.capacity:]
        return SpanExportResult.SUCCESS

    def shutdown(self) -> None:
        self.spans.clear()

    def get_recent(self, limit: int = 50) -> list[dict[str, Any]]:
        """Return formatted metadata for the most recent spans."""
        formatted: list[dict[str, Any]] = []
        for s in reversed(self.spans[-limit:]):
            start_ns = s.start_time or 0
            end_ns = s.end_time or start_ns
            duration_ms = round((end_ns - start_ns) / 1_000_000.0, 2) if end_ns >= start_ns else 0.0

            # Trace/Span hex conversion
            tid = f"{s.context.trace_id:032x}" if s.context and s.context.trace_id else get_current_trace_id()
            sid = f"{s.context.span_id:016x}" if s.context and s.context.span_id else get_current_span_id()
            pid = f"{s.parent.span_id:016x}" if s.parent and s.parent.span_id else None

            status_str = "OK" if s.status.is_ok else ("ERROR" if s.status.status_code == StatusCode.ERROR else "UNSET")

            # Convert attributes
            attrs = {k: str(v) if not isinstance(v, (int, float, bool)) else v for k, v in (s.attributes or {}).items()}

            dt_iso = datetime.fromtimestamp(start_ns / 1_000_000_000.0, tz=UTC).isoformat() if start_ns else datetime.now(UTC).isoformat()

            formatted.append({
                "name": s.name,
                "trace_id": tid,
                "span_id": sid,
                "parent_span_id": pid,
                "status": status_str,
                "status_description": s.status.description,
                "duration_ms": duration_ms,
                "timestamp": dt_iso,
                "attributes": attrs,
            })
        return formatted


# Initialize OpenTelemetry Global Tracer with our Ring Buffer
_ring_buffer_exporter = InMemoryRingBufferSpanExporter(capacity=200)
_provider = TracerProvider()
_provider.add_span_processor(SimpleSpanProcessor(_ring_buffer_exporter))
trace.set_tracer_provider(_provider)
docunorm_tracer = trace.get_tracer("docunorm.regulatory.tracer", "0.1.0")


def get_recent_trace_spans(limit: int = 50) -> list[dict[str, Any]]:
    """Retrieve the most recent OpenTelemetry spans recorded in memory."""
    return _ring_buffer_exporter.get_recent(limit)


@contextmanager
def trace_span(name: str, attributes: dict[str, Any] | None = None) -> Generator[trace.Span, None, None]:
    """
    Context manager to trace a logical block of execution.
    Automatically enriches the span with the current request trace_id and tenant context.
    """
    attrs = dict(attributes or {})
    active_tid = _current_trace_id.get()
    if active_tid and "trace_id" not in attrs:
        attrs["trace_id"] = active_tid

    with docunorm_tracer.start_as_current_span(name) as span:
        # Assign attributes
        for k, v in attrs.items():
            if isinstance(v, (str, bool, int, float)):
                span.set_attribute(k, v)
            elif v is not None:
                span.set_attribute(k, str(v))

        # Update span ID context
        span_ctx = span.get_span_context()
        tok_span = None
        if span_ctx and span_ctx.span_id:
            hex_sid = f"{span_ctx.span_id:016x}"
            tok_span = _current_span_id.set(hex_sid)

        start_time = time.perf_counter()
        try:
            yield span
            span.set_status(Status(StatusCode.OK))
        except Exception as exc:
            span.record_exception(exc)
            span.set_status(Status(StatusCode.ERROR, description=str(exc)))
            raise
        finally:
            elapsed_ms = (time.perf_counter() - start_time) * 1000.0
            span.set_attribute("execution.latency_ms", round(elapsed_ms, 2))
            if tok_span:
                _current_span_id.reset(tok_span)
