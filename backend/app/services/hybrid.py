def compute_rrf_score(rank: int, k: int = 60) -> float:
    if rank<=0: 
        raise ValueError("Rank must be a positive integer starting at 1.")
    rank=1.0 / (k + rank)
    return round(rank, 6)

def merge_search_results(
    vector_ranks: dict[str, int], 
    keyword_ranks: dict[str, int], 
    k: int = 60
) -> dict[str, float]:
    scores: dict[str, float] = {}

# Step 1: Loop over vector ranks and calculate their scores
    for chunk_id, rank in vector_ranks.items():
        score = compute_rrf_score(rank, k)
        scores[chunk_id] = scores.get(chunk_id, 0.0) + score
    # Step 2: Loop over keyword ranks and add their scores
    for chunk_id, rank in keyword_ranks.items():
        score = compute_rrf_score(rank, k)
        scores[chunk_id] = scores.get(chunk_id, 0.0) + score
    # Step 3: Sort chunks from highest score to lowest score
    sorted_scores = dict(sorted(scores.items(), key=lambda item: item[1], reverse=True))
    return sorted_scores

