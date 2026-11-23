"""
DocuNorm AI — Cross-Encoder Re-Ranking Schemas & Two-Stage Retrieval Data Models.
Conforms to High-Precision European Regulatory Retrieval Standards (DORA, KWG § 25b, GDPR).
"""

from uuid import UUID

from pydantic import BaseModel, Field


class RerankRequest(BaseModel):
    query: str = Field(..., min_length=2, max_length=2000, description="Natural language search query or regulatory question")
    documents: list[str] = Field(..., min_length=1, max_length=100, description="Candidate passages to score and re-rank")
    top_k: int = Field(default=5, ge=1, le=50, description="Number of highest-scoring passages to return")
    model: str = Field(default="bge-reranker-large", description="Cross-encoder model identifier or sovereign fallback")
    boost_legal_terms: bool = Field(default=True, description="Apply German statutory citation (§, Abs., Art.) attention boost")


class RerankedPassage(BaseModel):
    index: int = Field(..., description="Original 0-based index in candidate input list")
    text: str = Field(..., description="Passage text content")
    score: float = Field(..., ge=0.0, le=1.0, description="Calibrated cross-attention relevance score (0.0 to 1.0)")
    initial_rank: int = Field(..., ge=1, description="Rank in stage-1 candidate pool (1-indexed)")
    reranked_rank: int = Field(..., ge=1, description="Rank after cross-encoder scoring (1-indexed)")
    rank_delta: int = Field(..., description="Position change: positive if moved up, negative if moved down, 0 if unchanged")
    legal_term_matches: list[str] = Field(default_factory=list, description="Matched German legal terms or statutory citations")
    explanation: str | None = Field(default=None, description="Diagnostic explanation of relevance scoring")


class RerankResponse(BaseModel):
    query: str
    model_used: str
    total_candidates: int
    top_k: int
    execution_time_ms: float
    results: list[RerankedPassage]


class DocumentSearchRerankRequest(BaseModel):
    query: str = Field(..., min_length=2, max_length=2000, description="Audit query or clause search string")
    candidate_pool_size: int = Field(default=25, ge=2, le=100, description="Number of stage-1 vector candidates to fetch")
    top_k: int = Field(default=5, ge=1, le=25, description="Final number of top re-ranked chunks to return")
    boost_legal_terms: bool = Field(default=True, description="Apply German legal taxonomy and citation attention weighting")


class RerankedChunkResult(BaseModel):
    chunk_id: UUID
    document_id: UUID
    page_number: int
    bounding_box: list[float] | None = None
    content: str
    initial_vector_score: float
    cross_encoder_score: float
    initial_rank: int
    final_rank: int
    rank_delta: int
    legal_term_matches: list[str] = Field(default_factory=list)


class DocumentRerankedSearchResponse(BaseModel):
    query: str
    document_id: UUID
    stage1_candidates_fetched: int
    stage2_reranked_returned: int
    model_used: str
    execution_time_ms: float
    results: list[RerankedChunkResult]


class CrossEncoderModelInfo(BaseModel):
    model_id: str
    architecture: str
    is_native_torch_available: bool
    sovereign_fallback_active: bool
    supported_languages: list[str]
    specialized_taxonomies: list[str]


class PrecisionEvaluationRequest(BaseModel):
    query: str = Field(..., min_length=2, max_length=2000)
    candidates: list[str] = Field(..., min_length=1, max_length=100)
    relevant_indices: list[int] | None = Field(default=None)


class ContextCompactRequest(BaseModel):
    passages: list[str] = Field(..., min_length=1, max_length=100)
    preserve_citations: bool = Field(default=True)


class PrecisionEvaluationResult(BaseModel):
    query: str
    mrr: float = Field(..., description="Mean Reciprocal Rank (0.0 to 1.0)")
    ndcg_at_5: float = Field(..., description="Normalized Discounted Cumulative Gain @ 5")
    precision_at_3: float = Field(..., description="Top-3 Precision Ratio")
    stage1_baseline_mrr: float
    precision_improvement_pct: float
    statutory_boost_active: bool = True
    benchmark_verdict: str = "PRECISION_OPTIMIZED"


class ContextCompactorResponse(BaseModel):
    original_token_count: int
    compacted_token_count: int
    tokens_saved: int
    compression_ratio_pct: float
    compacted_context: str
    statutory_citations_preserved: list[str] = Field(default_factory=list)

