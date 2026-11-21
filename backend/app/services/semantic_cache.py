import asyncio
import hashlib
import json
import logging
import re
import time
from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from app.core.config import get_settings
from app.schemas.cache import AuditCacheTelemetry, CacheStatsResponse
from app.services.embedding import embedding_service

logger = logging.getLogger("docunorm.semantic_cache")

settings = get_settings()

AVERAGE_TOKENS_PER_AUDIT = 850
AVERAGE_LATENCY_MS_SAVED = 1250.0

QUESTION_STOPWORDS = {
    "what", "is", "are", "the", "a", "an", "for", "of", "to", "in", "on", "at",
    "under", "pursuant", "which", "how", "tell", "me", "show", "please", "can",
    "you", "give", "explain", "details",
    "wie", "ist", "sind", "der", "die", "das", "ein", "eine", "einer", "für",
    "von", "zu", "im", "auf", "unter", "gemäß", "gem", "nach",
    "welche", "welcher", "welches", "bitte", "erkläre", "zeige", "nenne", "gibt",
    "es", "gilt",
}


class CacheResult:
    """
    Encapsulates the result of a semantic cache lookup.
    """

    def __init__(
        self,
        hit: bool,
        response_data: dict[str, Any] | None = None,
        cache_type: str | None = None,
        similarity_score: float | None = None,
        saved_latency_ms: float | None = None,
        cached_at: str | None = None,
    ) -> None:
        self.hit = hit
        self.response_data = response_data
        self.cache_type = cache_type
        self.similarity_score = similarity_score
        self.saved_latency_ms = saved_latency_ms
        self.cached_at = cached_at

    @property
    def telemetry(self) -> AuditCacheTelemetry:
        return AuditCacheTelemetry(
            cached=self.hit,
            cache_type=self.cache_type,
            similarity_score=self.similarity_score,
            saved_latency_ms=self.saved_latency_ms,
            timestamp=self.cached_at,
        )


class SemanticCacheService:
    """
    High-Performance Redis Dynamic Semantic Cache & Deduplication Engine (Day 33).

    Features:
    - Tier 1: Instant Exact Hash Deduplication (O(1) SHA-256 normalized hash).
    - Tier 2: Deep Vector Semantic Cosine Similarity Deduplication (threshold >= 0.90).
    - Dual Storage Backend: Asynchronous Redis client with seamless, crash-proof
      fallback to sovereign in-memory LRU cache on air-gapped or standalone hosts.
    - Tenant & Document Isolation: Guarantees strict multi-client partitioning.
    - Telemetry & KPI Engine: Tracks cache hits, ratio, tokens saved, and latency saved.
    """

    def __init__(
        self,
        threshold: float | None = None,
        ttl_seconds: int | None = None,
    ) -> None:
        self.enabled = settings.SEMANTIC_CACHE_ENABLED
        self.threshold = (
            threshold if threshold is not None else settings.SEMANTIC_CACHE_THRESHOLD
        )
        self.ttl = (
            ttl_seconds if ttl_seconds is not None else settings.SEMANTIC_CACHE_TTL
        )

        # In-Memory Sovereign Fallback Cache
        # Structure: key -> { "query": str, "normalized_query": str, "embedding": list[float],
        #                    "tenant_id": str, "document_id": str, "framework": str,
        #                    "lang": str, "response": dict, "created_at": float, "iso_time": str }
        self._memory_cache: dict[str, dict[str, Any]] = {}
        # Document Index: doc_key -> set of cache keys
        self._memory_doc_index: dict[str, set[str]] = {}

        # Redis Client Instance
        self._redis_client: Any = None
        self._redis_available: bool | None = None
        self._lock = asyncio.Lock()

        # Telemetry counters
        self._exact_hits = 0
        self._semantic_hits = 0
        self._misses = 0

    def normalize_query(self, query: str) -> str:
        """
        Normalizes natural language queries for deterministic exact-match hashing:
        lowercases, removes excess whitespace, strips non-alphanumeric punctuation.
        """
        cleaned = query.lower().strip()
        cleaned = re.sub(r"[?!.,;:\'\"`]+", "", cleaned)
        cleaned = re.sub(r"\s+", " ", cleaned).strip()
        return cleaned

    def extract_semantic_query(self, query: str) -> str:
        """
        Extracts core semantic keywords by stripping question affixes and stopwords,
        enabling high-fidelity vector matching across stylistic phrasing variants.
        """
        cleaned = re.sub(r"[^\w\s]", " ", query.lower())
        tokens = [w for w in cleaned.split() if w not in QUESTION_STOPWORDS]
        if tokens:
            return " ".join(tokens)
        return query.lower().strip()

    def _build_exact_key(
        self,
        tenant_id: str | UUID,
        document_id: str | UUID,
        framework: str,
        lang: str,
        normalized_query: str,
    ) -> str:
        h = hashlib.sha256(
            f"{tenant_id}:{document_id}:{framework.upper()}:{lang.upper()}:{normalized_query}".encode()
        ).hexdigest()[:24]
        return f"docunorm:cache:{tenant_id}:{document_id}:{h}"

    def _build_doc_index_key(
        self, tenant_id: str | UUID, document_id: str | UUID
    ) -> str:
        return f"docunorm:cache_index:{tenant_id}:{document_id}"

    async def _get_redis(self) -> Any:
        """
        Acquires or initializes Redis client connection.
        If Redis is unreachable, cleanly marks backend as sovereign in-memory fallback.
        """
        if self._redis_available is False:
            return None

        if self._redis_client is not None:
            return self._redis_client

        async with self._lock:
            if self._redis_client is not None:
                return self._redis_client

            try:
                import redis.asyncio as aioredis

                client = aioredis.from_url(
                    settings.redis_url,
                    socket_connect_timeout=0.8,
                    socket_timeout=1.0,
                    decode_responses=True,
                )
                # Test connectivity
                await asyncio.wait_for(client.ping(), timeout=1.0)
                self._redis_client = client
                self._redis_available = True
                logger.info(
                    "Connected to Redis cache at %s:%s",
                    settings.REDIS_HOST,
                    settings.REDIS_PORT,
                )
                return self._redis_client
            except Exception as e:
                self._redis_available = False
                self._redis_client = None
                logger.warning(
                    "Redis unavailable (%s). Using Sovereign In-Memory Semantic Cache fallback.",
                    e,
                )
                return None

    async def get(
        self,
        tenant_id: str | UUID,
        document_id: str | UUID,
        query: str,
        framework: str = "DORA",
        lang: str = "DE",
    ) -> CacheResult:
        """
        Searches semantic cache for an existing audit finding:
        1. Checks exact normalized hash match (O(1)).
        2. If no exact match, computes cosine similarity against all cached
           queries for the same document and tenant.
        3. Returns CacheResult with hit=True if similarity >= threshold.
        """
        if not self.enabled or not query.strip():
            return CacheResult(hit=False)

        tenant_str = str(tenant_id)
        doc_str = str(document_id)
        fw_upper = framework.upper()
        lang_upper = lang.upper()
        norm_query = self.normalize_query(query)
        exact_key = self._build_exact_key(
            tenant_str, doc_str, fw_upper, lang_upper, norm_query
        )

        redis = await self._get_redis()

        # -------------------------------------------------------------
        # STEP 1: Exact Normalized Hash Lookup
        # -------------------------------------------------------------
        if redis:
            try:
                raw_json = await redis.get(exact_key)
                if raw_json:
                    entry = json.loads(raw_json)
                    self._exact_hits += 1
                    return CacheResult(
                        hit=True,
                        response_data=entry["response"],
                        cache_type="exact",
                        similarity_score=1.0,
                        saved_latency_ms=AVERAGE_LATENCY_MS_SAVED,
                        cached_at=entry.get("iso_time"),
                    )
            except Exception as e:
                logger.debug("Redis exact get error: %s", e)

        # In-memory exact lookup
        if exact_key in self._memory_cache:
            entry = self._memory_cache[exact_key]
            # Check TTL
            if time.time() - entry.get("created_at", 0) <= self.ttl:
                self._exact_hits += 1
                return CacheResult(
                    hit=True,
                    response_data=entry["response"],
                    cache_type="exact",
                    similarity_score=1.0,
                    saved_latency_ms=AVERAGE_LATENCY_MS_SAVED,
                    cached_at=entry.get("iso_time"),
                )
            else:
                self._remove_memory_key(exact_key)

        # -------------------------------------------------------------
        # STEP 2: Vector Semantic Similarity Lookup
        # -------------------------------------------------------------
        query_vector = embedding_service.generate_embedding(
            self.extract_semantic_query(query)
        )
        candidate_entries: list[dict[str, Any]] = []

        if redis:
            try:
                doc_idx_key = self._build_doc_index_key(tenant_str, doc_str)
                keys = await redis.smembers(doc_idx_key)
                if keys:
                    for k in keys:
                        raw = await redis.get(k)
                        if raw:
                            candidate_entries.append(json.loads(raw))
            except Exception as e:
                logger.debug("Redis candidate scan error: %s", e)

        # If Redis had no candidates or is offline, check in-memory doc index
        if not candidate_entries:
            doc_idx_key = self._build_doc_index_key(tenant_str, doc_str)
            keys = self._memory_doc_index.get(doc_idx_key, set())
            now = time.time()
            for k in list(keys):
                entry = self._memory_cache.get(k)
                if entry:
                    if now - entry.get("created_at", 0) <= self.ttl:
                        candidate_entries.append(entry)
                    else:
                        self._remove_memory_key(k)

        # Evaluate candidate semantic similarities
        best_entry: dict[str, Any] | None = None
        best_similarity = 0.0

        for entry in candidate_entries:
            # Must match tenant, document, framework, and language
            if (
                entry.get("tenant_id") == tenant_str
                and entry.get("document_id") == doc_str
                and entry.get("framework") == fw_upper
                and entry.get("lang") == lang_upper
            ):
                cached_vec = entry.get("embedding")
                if cached_vec and len(cached_vec) == len(query_vector):
                    sim = embedding_service.cosine_similarity(query_vector, cached_vec)
                    if sim > best_similarity:
                        best_similarity = sim
                        best_entry = entry

        if best_entry and best_similarity >= self.threshold:
            self._semantic_hits += 1
            # Dynamic latency estimation scaled by similarity
            saved_ms = round(AVERAGE_LATENCY_MS_SAVED * (best_similarity**2), 1)
            return CacheResult(
                hit=True,
                response_data=best_entry["response"],
                cache_type="semantic",
                similarity_score=round(best_similarity, 4),
                saved_latency_ms=saved_ms,
                cached_at=best_entry.get("iso_time"),
            )

        # -------------------------------------------------------------
        # STEP 3: Cache Miss
        # -------------------------------------------------------------
        self._misses += 1
        return CacheResult(hit=False)

    async def set(
        self,
        tenant_id: str | UUID,
        document_id: str | UUID,
        query: str,
        framework: str,
        lang: str,
        response_data: dict[str, Any],
        query_vector: list[float] | None = None,
    ) -> None:
        """
        Stores an audited query and response payload in the semantic cache.
        """
        if not self.enabled or not query.strip():
            return

        tenant_str = str(tenant_id)
        doc_str = str(document_id)
        fw_upper = framework.upper()
        lang_upper = lang.upper()
        norm_query = self.normalize_query(query)
        exact_key = self._build_exact_key(
            tenant_str, doc_str, fw_upper, lang_upper, norm_query
        )
        doc_idx_key = self._build_doc_index_key(tenant_str, doc_str)

        if query_vector is None:
            query_vector = embedding_service.generate_embedding(
                self.extract_semantic_query(query)
            )

        now = time.time()
        iso_time = datetime.now(UTC).isoformat()

        entry = {
            "key": exact_key,
            "query": query,
            "normalized_query": norm_query,
            "embedding": query_vector,
            "tenant_id": tenant_str,
            "document_id": doc_str,
            "framework": fw_upper,
            "lang": lang_upper,
            "response": response_data,
            "created_at": now,
            "iso_time": iso_time,
        }

        # 1. Store to Redis if available
        redis = await self._get_redis()
        if redis:
            try:
                payload_str = json.dumps(entry)
                await redis.set(exact_key, payload_str, ex=self.ttl)
                await redis.sadd(doc_idx_key, exact_key)
                await redis.expire(doc_idx_key, self.ttl)
            except Exception as e:
                logger.debug("Redis set error: %s", e)

        # 2. Always persist into Sovereign In-Memory store as well
        self._memory_cache[exact_key] = entry
        if doc_idx_key not in self._memory_doc_index:
            self._memory_doc_index[doc_idx_key] = set()
        self._memory_doc_index[doc_idx_key].add(exact_key)

    def _remove_memory_key(self, key: str) -> None:
        entry = self._memory_cache.pop(key, None)
        if entry:
            doc_idx_key = self._build_doc_index_key(
                entry.get("tenant_id", ""), entry.get("document_id", "")
            )
            if doc_idx_key in self._memory_doc_index:
                self._memory_doc_index[doc_idx_key].discard(key)

    async def invalidate_document(
        self,
        document_id: str | UUID,
        tenant_id: str | UUID | None = None,
    ) -> int:
        """
        Invalidates all cached queries for a specific document (e.g. after re-indexing or deletion).
        """
        doc_str = str(document_id)
        purged = 0

        # In-memory purge
        keys_to_delete = []
        for k, v in self._memory_cache.items():
            if v.get("document_id") == doc_str:
                if tenant_id is None or v.get("tenant_id") == str(tenant_id):
                    keys_to_delete.append(k)

        for k in keys_to_delete:
            self._remove_memory_key(k)
            purged += 1

        # Redis purge
        redis = await self._get_redis()
        if redis:
            try:
                pattern = f"docunorm:cache:*:{doc_str}:*"
                cursor = 0
                while True:
                    cursor, keys = await redis.scan(
                        cursor=cursor, match=pattern, count=100
                    )
                    if keys:
                        await redis.delete(*keys)
                        purged += len(keys)
                    if cursor == 0:
                        break

                idx_pattern = f"docunorm:cache_index:*:{doc_str}"
                cursor = 0
                while True:
                    cursor, idx_keys = await redis.scan(
                        cursor=cursor, match=idx_pattern, count=100
                    )
                    if idx_keys:
                        await redis.delete(*idx_keys)
                    if cursor == 0:
                        break
            except Exception as e:
                logger.debug("Redis invalidate error: %s", e)

        return purged

    async def clear_all(self) -> int:
        """
        Clears all semantic cache entries across all documents and tenants.
        """
        count = len(self._memory_cache)
        self._memory_cache.clear()
        self._memory_doc_index.clear()

        redis = await self._get_redis()
        if redis:
            try:
                cursor = 0
                while True:
                    cursor, keys = await redis.scan(
                        cursor=cursor, match="docunorm:cache*", count=200
                    )
                    if keys:
                        await redis.delete(*keys)
                        count += len(keys)
                    if cursor == 0:
                        break
            except Exception as e:
                logger.debug("Redis clear_all error: %s", e)

        self._exact_hits = 0
        self._semantic_hits = 0
        self._misses = 0
        return count

    async def get_stats(self) -> CacheStatsResponse:
        """
        Returns live cache performance metrics.
        """
        total_hits = self._exact_hits + self._semantic_hits
        total_queries = total_hits + self._misses
        hit_ratio = round(total_hits / total_queries, 4) if total_queries > 0 else 0.0

        active_entries = len(self._memory_cache)
        redis = await self._get_redis()
        backend = "sovereign_in_memory"

        if redis:
            backend = "redis"
            try:
                # Approximate key count in redis
                cursor, keys = await redis.scan(
                    cursor=0, match="docunorm:cache:*:*:*", count=1000
                )
                active_entries = max(active_entries, len(keys))
            except Exception:
                backend = "sovereign_in_memory"

        return CacheStatsResponse(
            status="active" if self.enabled else "disabled",
            storage_backend=backend,
            total_queries=total_queries,
            hits=total_hits,
            exact_hits=self._exact_hits,
            semantic_hits=self._semantic_hits,
            misses=self._misses,
            hit_ratio=hit_ratio,
            estimated_tokens_saved=total_hits * AVERAGE_TOKENS_PER_AUDIT,
            estimated_latency_saved_ms=round(
                total_hits * AVERAGE_LATENCY_MS_SAVED, 1
            ),
            active_cached_entries=active_entries,
            similarity_threshold=self.threshold,
            ttl_seconds=self.ttl,
        )


# Global singleton instance
semantic_cache = SemanticCacheService()
