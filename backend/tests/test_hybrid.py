import pytest
from app.services.hybrid import compute_rrf_score, merge_search_results


def test_compute_rrf_score_valid():
    """Rank 1 with k=60 should equal 1/61 = 0.016393"""
    score = compute_rrf_score(rank=1, k=60)
    assert score == pytest.approx(0.016393, rel=1e-4)


def test_compute_rrf_score_rejects_zero_or_negative():
    """Rank must be >= 1"""
    with pytest.raises(ValueError, match="Rank must be a positive integer starting at 1."):
        compute_rrf_score(rank=0)
    with pytest.raises(ValueError, match="Rank must be a positive integer starting at 1."):
        compute_rrf_score(rank=-2)


def test_merge_search_results_fuses_scores_correctly():
    """
    Chunk A is rank 1 in vector and rank 2 in keyword.
    Chunk B is rank 2 in vector only.
    Chunk C is rank 1 in keyword only.
    Chunk A must win because it appears in BOTH lists!
    """
    vector_ranks = {"chunk_A": 1, "chunk_B": 2}
    keyword_ranks = {"chunk_A": 2, "chunk_C": 1}

    fused = merge_search_results(vector_ranks, keyword_ranks, k=60)

    # Chunk A score = 1/61 + 1/62 = 0.016393 + 0.016129 = 0.032522
    assert "chunk_A" in fused
    assert "chunk_B" in fused
    assert "chunk_C" in fused

    # Chunk A must be the #1 result!
    sorted_keys = list(fused.keys())
    assert sorted_keys[0] == "chunk_A"
    assert fused["chunk_A"] > fused["chunk_B"]
    assert fused["chunk_A"] > fused["chunk_C"]
