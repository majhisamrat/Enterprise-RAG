from abc import ABC, abstractmethod


class BaseRetriever(ABC):

    @abstractmethod
    def retrieve(
        self,
        query: str,
        limit: int = 10,
    ):
        """
        Retrieve relevant chunks.
        """
        raise NotImplementedError