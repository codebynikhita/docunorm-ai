"""
DocuNorm AI — Day 36: Cross-Encoder Context Precision & Benchmark Suite.
Tests BM25 hybrid calibration, context compaction deduplication preserving statutory citations,
MRR/NDCG@5 precision metrics evaluation, and REST endpoints.
"""

from fastapi.testclient import TestClient

from app.main import app
from app.services.reranker import reranker_service


def test_bm25_score_computation():
    """
    Verifies BM25 term frequency saturation and query matching logic.
    """
    query = "BaFin KWG Auslagerung"
    matching_passage = "Gemäß § 25b KWG unterliegt jede wesentliche Auslagerung der Prüfung durch die BaFin."
    non_matching_passage = "Die Parteien vereinbaren einen monatlichen Abrechnungszyklus für Cloud-Ressourcen."

    score_match = reranker_service.compute_bm25_score(query, matching_passage)
    score_nomatch = reranker_service.compute_bm25_score(query, non_matching_passage)

    assert score_match > 0.4
    assert score_nomatch == 0.0
    assert score_match > score_nomatch


def test_context_window_compaction():
    """
    Verifies deduplication of repetitive legal clauses while preserving statutory citations.
    """
    repetitive_passages = [
        "Gemäß § 25b KWG ist der BaFin ein uneingeschränktes Prüfungsrecht einzuräumen.",
        "Gemäß § 25b KWG ist der BaFin ein uneingeschränktes Prüfungsrecht einzuräumen.",  # Exact duplicate
        "Die Parteien regeln die Vertraulichkeit. Alle Geschäftsgeheimnisse unterliegen strengster Geheimhaltung.",
        "Die Parteien regeln die Vertraulichkeit. Alle Geschäftsgeheimnisse unterliegen strengster Geheimhaltung.",  # Exact duplicate
        "DORA Art. 30 verlangt vertraglich verankerte Ausstiegsstrategien und Übergangsfristen.",
    ]

    res = reranker_service.compact_context_window(
        passages=repetitive_passages,
        preserve_citations=True,
    )

    assert res.tokens_saved > 0
    assert res.compression_ratio_pct > 0.0
    assert len(res.statutory_citations_preserved) >= 1
    assert "§ 25b" in res.compacted_context
    assert "DORA Art. 30" in res.compacted_context


def test_evaluate_precision_metrics():
    """
    Verifies MRR, NDCG@5, and Precision@3 metric calculation against gold standard labels.
    """
    query = "Kündigungsrecht nach DORA Art. 30"
    candidates = [
        "Präambel des Rahmenvertrags für Softwarebereitstellung.",  # Index 0: Not relevant
        "DORA Art. 30 Kündigungsrechte bei regulatorischer Weisung fristlos.",  # Index 1: Relevant!
        "Datenschutz und DSGVO Verpflichtungen.",  # Index 2: Less relevant
    ]

    eval_result = reranker_service.evaluate_precision(
        query=query,
        candidates=candidates,
        relevant_indices=[1],
    )

    assert eval_result.mrr > 0.0
    assert eval_result.ndcg_at_5 > 0.0
    assert eval_result.precision_at_3 > 0.0
    assert eval_result.statutory_boost_active is True
    assert eval_result.benchmark_verdict == "PRECISION_OPTIMIZED"


def test_rerank_evaluate_precision_endpoint():
    """
    Verifies POST /api/v1/rerank/evaluate-precision endpoint.
    """
    client = TestClient(app)
    payload = {
        "query": "Aufsichtsrechtliche Kündigung KWG § 25b",
        "candidates": [
            "Allgemeine Bestimmungen über Laufzeit und Kündigung.",
            "KWG § 25b Kündigungsrecht aus wichtigem Grund bei aufsichtsrechtlicher Anordnung der BaFin.",
            "Rechnungsstellung und Zahlungsbedingungen.",
        ],
        "relevant_indices": [1],
    }

    res = client.post("/api/v1/rerank/evaluate-precision", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["mrr"] == 1.0  # Reranker lifts the KWG § 25b clause to rank 1!
    assert data["statutory_boost_active"] is True
    assert data["benchmark_verdict"] == "PRECISION_OPTIMIZED"


def test_rerank_compact_context_endpoint():
    """
    Verifies POST /api/v1/rerank/compact-context endpoint.
    """
    client = TestClient(app)
    payload = {
        "passages": [
            "BaFin KWG § 25b Auslagerung Prüfung.",
            "BaFin KWG § 25b Auslagerung Prüfung.",
            "DORA Art. 30 Übergangsfristen.",
        ],
        "preserve_citations": True,
    }

    res = client.post("/api/v1/rerank/compact-context", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["tokens_saved"] > 0
    assert "§ 25b" in data["compacted_context"]
