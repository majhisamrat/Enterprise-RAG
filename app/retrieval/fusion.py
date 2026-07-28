from collections import defaultdict
from typing import Any, Dict, List


class ReciprocalRankFusion:
    """Reciprocal Rank Fusion (RRF) algorithm implementation."""

    def __init__(self, k: int = 60):
        self.k = k

    def fuse(
        self,
        dense_results: List[Dict[str, Any]],
        sparse_results: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """Fuse dense and sparse search results using RRF scoring."""
        scores = defaultdict(float)
        documents = {}

        # Dense results
        for rank, item in enumerate(dense_results, start=1):
            chunk_id = item.get("chunk_id") or str(hash(item.get("text", "")))
            scores[chunk_id] += 1.0 / (self.k + rank)
            documents[chunk_id] = item

        # Sparse results
        for rank, item in enumerate(sparse_results, start=1):
            chunk_id = item.get("chunk_id") or str(hash(item.get("text", "")))
            scores[chunk_id] += 1.0 / (self.k + rank)
            if chunk_id not in documents:
                documents[chunk_id] = item

        # Rank by combined RRF score descending
        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)

        fused_results = []
        for chunk_id, score in ranked:
            doc = documents[chunk_id].copy()
            doc["rrf_score"] = score
            fused_results.append(doc)

        return fused_results