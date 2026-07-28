from typing import Optional
from sentence_transformers import CrossEncoder
from app.utils.logger import logger


class RerankerModel:
    """Singleton loader for CrossEncoder reranker."""

    _model: Optional[CrossEncoder] = None

    @classmethod
    def load(
        cls,
        model_name: str = "BAAI/bge-reranker-large",
    ) -> CrossEncoder:

        if cls._model is None:
            logger.info(f"Loading reranker model: {model_name}")
            cls._model = CrossEncoder(
                model_name,
                trust_remote_code=True,
            )
            logger.success("Reranker model loaded successfully.")

        return cls._model