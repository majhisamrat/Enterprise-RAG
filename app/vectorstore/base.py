from abc import ABC, abstractmethod

from app.ingestion.schemas import ChunkedDocument


class BaseVectorStore(ABC):

    @abstractmethod
    def index(
        self,
        document: ChunkedDocument,
    ):
        raise NotImplementedError

    @abstractmethod
    def search(
        self,
        query_embedding: list[float],
        limit: int = 5,
    ):
        raise NotImplementedError