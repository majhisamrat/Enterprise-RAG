import numpy as np


def embedding_dimension(embedding: list[float]) -> int:
    """Return the vector dimension of the embedding."""
    return len(embedding)


def cosine_similarity(a: list[float], b: list[float]) -> float:
    """Calculate cosine similarity between two vector embeddings."""
    arr_a = np.array(a, dtype=np.float32)
    arr_b = np.array(b, dtype=np.float32)

    norm_a = float(np.linalg.norm(arr_a))
    norm_b = float(np.linalg.norm(arr_b))

    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0

    return float(np.dot(arr_a, arr_b) / (norm_a * norm_b))