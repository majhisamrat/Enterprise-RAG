from abc import ABC, abstractmethod

from app.ingestion.schemas import ChunkedDocument


class BaseKeywordSearch(ABC):

    @abstractmethod
    def index(
        self,
        document: ChunkedDocument,
    ):
        raise NotImplementedError

    @abstractmethod
    def search(
        self,
        query: str,
        limit: int = 10,
    ):
        raise NotImplementedError