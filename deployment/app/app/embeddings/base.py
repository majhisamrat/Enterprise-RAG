from abc import ABC, abstractmethod
from typing import List, Union
from app.ingestion.schemas import ChunkedDocument


class BaseEmbedder(ABC):
    """Abstract base class for all embedding generators."""

    @abstractmethod
    def embed(self, document: ChunkedDocument) -> ChunkedDocument:
        """Generate vector embeddings for document chunks."""
        pass

    @abstractmethod
    def embed_query(self, query: str) -> List[float]:
        """Generate vector embedding for a query string."""
        pass
