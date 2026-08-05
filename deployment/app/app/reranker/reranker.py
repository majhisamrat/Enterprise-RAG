from typing import Any, List
from app.utils.logger import logger

from app.reranker.base import BaseReranker
from app.reranker.model import RerankerModel
from app.reranker.utils import validate_documents


class BGEReranker(BaseReranker):
    """Production-grade BGE CrossEncoder Reranker."""

    def __init__(
        self,
        model_name: str = "BAAI/bge-reranker-large",
    ) -> None:
        self.model: Any = RerankerModel.load(model_name)

    def rerank(
        self,
        query: str,
        documents: list[dict[str, Any]],
        top_k: int = 10,
    ) -> list[dict[str, Any]]:
        """Rerank retrieved documents using CrossEncoder pairs."""
        validate_documents(documents)

        if not documents:
            return []

        logger.info(f"Reranking {len(documents)} documents...")

        pairs: Any = [
            [query, str(doc.get("text") or doc.get("document") or "")]
            for doc in documents
        ]

        scores: Any = self.model.predict(
            pairs,
            batch_size=16,
            show_progress_bar=False,
        )

        for doc, score in zip(documents, scores):
            doc["rerank_score"] = float(score)

        documents.sort(
            key=lambda x: float(x.get("rerank_score", 0.0)),
            reverse=True,
        )

        logger.success(f"Top {min(top_k, len(documents))} documents selected.")

        return documents[:top_k]