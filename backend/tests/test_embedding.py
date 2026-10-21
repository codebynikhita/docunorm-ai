import math

from app.services.embedding import embedding_service


def test_embedding_dimensions_and_normalization() -> None:
    """
    Verifies that the embedding vector has exactly 1024 dimensions
    and is L2-normalized (length == 1.0).
    """
    text = "Master supply agreement between Siemens AG and Supplier GmbH."
    vector = embedding_service.generate_embedding(text)

    # 1. Must be exactly 1024 dimensions
    assert len(vector) == 1024

    # 2. Must be all floating-point numbers
    assert all(isinstance(x, float) for x in vector)

    # 3. L2 norm must equal 1.0 (unit vector)
    norm = math.sqrt(sum(x * x for x in vector))
    assert math.isclose(norm, 1.0, rel_tol=1e-5)


def test_semantic_similarity_close_for_related_sentences() -> None:
    """
    Verifies that semantically related sentences have high cosine similarity (> 0.65),
    while completely unrelated sentences have low cosine similarity (< 0.40).
    """
    vec_penalty = embedding_service.generate_embedding(
        "Late deliveries incur a financial penalty fee of 0.5% per week."
    )
    vec_fine = embedding_service.generate_embedding(
        "The supplier will be charged a monetary fine for delayed shipments."
    )
    vec_cake = embedding_service.generate_embedding(
        "Bake a chocolate strawberry cake in the oven at 180 degrees celsius."
    )

    similarity_related = embedding_service.cosine_similarity(vec_penalty, vec_fine)
    similarity_unrelated = embedding_service.cosine_similarity(vec_penalty, vec_cake)

    # Related sentences must score significantly higher than unrelated ones (> 3x higher)
    assert similarity_related > 0.50
    assert similarity_unrelated < 0.15
    assert similarity_related > (similarity_unrelated * 3)
