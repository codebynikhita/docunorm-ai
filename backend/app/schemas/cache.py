from pydantic import BaseModel, Field


class AuditCacheTelemetry(BaseModel):
    """
    Telemetry metadata attached to an audit response indicating whether it was served
    from the Redis/Sovereign semantic cache.
    """

    cached: bool = Field(
        default=False,
        description="Whether this response was served directly from the semantic cache without LLM invocation.",
    )
    cache_type: str | None = Field(
        default=None,
        description="Type of cache match: 'exact' (hash match) or 'semantic' (vector cosine similarity match).",
    )
    similarity_score: float | None = Field(
        default=None,
        description="Cosine similarity score for semantic match (1.0 for exact hash matches).",
    )
    saved_latency_ms: float | None = Field(
        default=None,
        description="Estimated latency saved in milliseconds compared to full LLM generation.",
    )
    timestamp: str | None = Field(
        default=None,
        description="ISO timestamp when the cached finding was generated.",
    )


class CacheStatsResponse(BaseModel):
    """
    Live telemetry and performance metrics for the Redis Dynamic Semantic Cache.
    """

    status: str = Field(
        default="active",
        description="Operational status of the semantic cache ('active' or 'disabled').",
    )
    storage_backend: str = Field(
        description="Active backend storage driver: 'redis' or 'sovereign_in_memory'."
    )
    total_queries: int = Field(
        default=0,
        description="Total audit inquiries checked against the cache.",
    )
    hits: int = Field(
        default=0,
        description="Total successful cache hits (exact + semantic).",
    )
    exact_hits: int = Field(
        default=0,
        description="Count of exact hash matches.",
    )
    semantic_hits: int = Field(
        default=0,
        description="Count of vector semantic similarity matches above threshold.",
    )
    misses: int = Field(
        default=0,
        description="Count of cache misses requiring full LLM inference.",
    )
    hit_ratio: float = Field(
        default=0.0,
        description="Ratio of cache hits to total queries (hits / total_queries).",
    )
    estimated_tokens_saved: int = Field(
        default=0,
        description="Total estimated LLM tokens saved through cache deduplication.",
    )
    estimated_latency_saved_ms: float = Field(
        default=0.0,
        description="Total cumulative latency saved across all cache hits in milliseconds.",
    )
    active_cached_entries: int = Field(
        default=0,
        description="Total number of active cached document audit inquiries.",
    )
    similarity_threshold: float = Field(
        default=0.90,
        description="Minimum vector cosine similarity threshold required to trigger a semantic cache hit.",
    )
    ttl_seconds: int = Field(
        default=86400,
        description="Time-to-live expiration for cached entries in seconds.",
    )


class CacheInvalidateRequest(BaseModel):
    """
    Request payload to invalidate semantic cache entries.
    """

    document_id: str | None = Field(
        default=None,
        description="Optional document UUID to invalidate cache for. If omitted, purges tenant cache.",
    )


class CacheInvalidateResponse(BaseModel):
    """
    Response returned after invalidating semantic cache entries.
    """

    status: str = Field(
        default="success",
        description="Status of the invalidation operation.",
    )
    document_id: str | None = Field(
        default=None,
        description="Target document ID that was purged, or null if tenant/all was purged.",
    )
    tenant_id: str | None = Field(
        default=None,
        description="Tenant ID whose cache was purged.",
    )
    entries_purged: int = Field(
        default=0,
        description="Number of cache keys or vector entries deleted.",
    )
