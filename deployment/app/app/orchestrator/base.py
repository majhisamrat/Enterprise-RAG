from abc import ABC, abstractmethod
from typing import Any, Dict


class BaseOrchestrator(ABC):
    """Base interface for RAG orchestrators."""

    @abstractmethod
    async def chat(self, query: str, **kwargs: Any) -> Dict[str, Any]:
        """Execute the complete async RAG pipeline."""
        raise NotImplementedError