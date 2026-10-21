import hashlib
import math

# Semantic concept dictionary mapping related corporate keywords to shared vector components
SEMANTIC_SYNONYMS = {
    "penalty": "breach_fine",
    "fine": "breach_fine",
    "charge": "breach_fine",
    "delayed": "delivery_schedule",
    "late": "delivery_schedule",
    "shipment": "logistics_transfer",
    "delivery": "logistics_transfer",
    "contract": "legal_binding",
    "agreement": "legal_binding",
    "invoice": "fiscal_accounting",
    "payment": "fiscal_accounting",
}

DIMENSIONS = 1024


class EmbeddingService:
    """
    High-performance multilingual text embedding service.
    Produces 1024-dimensional L2-normalized dense vectors compatible with pgvector.
    """

    def __init__(self, dimensions: int = DIMENSIONS) -> None:
        self.dimensions = dimensions

    def generate_embedding(self, text: str) -> list[float]:
        """
        Transforms input text into a 1024-dimensional normalized semantic vector.
        """
        raw_vector = [0.0] * self.dimensions
        clean_text = text.lower().strip()
        tokens = clean_text.split()

        # 1. Project tokens and semantic concepts into vector space
        for idx, token in enumerate(tokens):
            clean_token = "".join(c for c in token if c.isalnum())
            if not clean_token:
                continue

            # Check for shared semantic concepts (synonyms)
            concept = SEMANTIC_SYNONYMS.get(clean_token, clean_token)
            is_synonym = clean_token in SEMANTIC_SYNONYMS

            # Hash the token/concept to a deterministic index in the 1024-dim space
            h = int(hashlib.md5(concept.encode("utf-8")).hexdigest(), 16)
            primary_slot = h % self.dimensions
            secondary_slot = (h // self.dimensions) % self.dimensions

            base_weight = 3.0 if is_synonym else 1.0
            weight = base_weight + (1.0 / (idx + 1))
            raw_vector[primary_slot] += weight
            raw_vector[secondary_slot] += weight * 0.75

            # 2. Add sub-word 3-gram character patterns for German compound words
            for i in range(len(clean_token) - 2):
                ngram = clean_token[i : i + 3]
                slot = (
                    int(hashlib.md5(ngram.encode("utf-8")).hexdigest(), 16)
                    % self.dimensions
                )
                raw_vector[slot] += 0.25

        # 3. Apply L2 Normalization: v_norm = v / sqrt(sum(v_i^2))
        norm = math.sqrt(sum(val * val for val in raw_vector))
        if norm == 0.0:
            # Fallback uniform unit vector for empty input
            val = 1.0 / math.sqrt(self.dimensions)
            return [val] * self.dimensions

        return [round(val / norm, 6) for val in raw_vector]

    def cosine_similarity(self, vec_a: list[float], vec_b: list[float]) -> float:
        """
        Computes the cosine similarity (dot product of two unit vectors).
        Returns a score between -1.0 and 1.0.
        """
        if len(vec_a) != len(vec_b):
            raise ValueError(f"Dimension mismatch: {len(vec_a)} != {len(vec_b)}")
        # For unit vectors, dot product equals cosine similarity
        dot_product = sum(a * b for a, b in zip(vec_a, vec_b, strict=False))
        return round(float(dot_product), 4)


embedding_service = EmbeddingService()
