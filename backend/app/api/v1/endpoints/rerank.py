"""
DocuNorm AI — Cross-Encoder Re-Ranking REST Endpoints.
Provides two-stage high-precision passage scoring and retrieval diagnostics.
"""

from fastapi import APIRouter, status

from app.schemas.rerank import (
    ContextCompactorResponse,
    ContextCompactRequest,
    CrossEncoderModelInfo,
    PrecisionEvaluationRequest,
    PrecisionEvaluationResult,
    RerankRequest,
    RerankResponse,
)
from app.services.reranker import reranker_service

router = APIRouter(prefix="/rerank", tags=["Cross-Encoder Re-Ranking"])


@router.post(
    "",
    response_model=RerankResponse,
    status_code=status.HTTP_200_OK,
    summary="Re-Rank Candidate Passages Using Cross-Encoder Self-Attention (bge-reranker-large)",
)
async def rerank_passages_endpoint(payload: RerankRequest) -> RerankResponse:
    """
    Two-Stage Cross-Encoder Re-Ranking:
    Scores (query, passage) pairs using full joint cross-attention.
    Applies German legal statutory citation and operative domain weighting.
    """
    return reranker_service.rerank_passages(
        query=payload.query,
        documents=payload.documents,
        top_k=payload.top_k,
        boost_legal_terms=payload.boost_legal_terms,
    )


@router.get(
    "/models",
    response_model=CrossEncoderModelInfo,
    summary="Get Cross-Encoder Re-Ranker Architecture & Hardware Acceleration Info",
)
async def get_reranker_model_info() -> CrossEncoderModelInfo:
    """
    Returns diagnostic telemetry regarding cross-encoder execution tier
    (native HuggingFace/PyTorch vs. Sovereign German Legal Cross-Attention Engine).
    """
    return reranker_service.get_model_info()


@router.post(
    "/evaluate-precision",
    response_model=PrecisionEvaluationResult,
    summary="Benchmark Cross-Encoder Precision (NDCG@5, MRR, Precision@3)",
    description="Evaluates two-stage retrieval improvement over baseline dense vector search.",
)
async def evaluate_precision_endpoint(payload: PrecisionEvaluationRequest) -> PrecisionEvaluationResult:
    """Evaluate retrieval precision metrics."""
    return reranker_service.evaluate_precision(
        query=payload.query,
        candidates=payload.candidates,
        relevant_indices=payload.relevant_indices,
    )


@router.post(
    "/compact-context",
    response_model=ContextCompactorResponse,
    summary="Compact Retrieval Passages for Context Window Optimization",
    description="Eliminates redundant cross-chunk sentences while retaining statutory citations.",
)
async def compact_context_endpoint(payload: ContextCompactRequest) -> ContextCompactorResponse:
    """Compact context window."""
    return reranker_service.compact_context_window(
        passages=payload.passages,
        preserve_citations=payload.preserve_citations,
    )

