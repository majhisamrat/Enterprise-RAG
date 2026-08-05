from abc import ABC, abstractmethod
from typing import Any


class BasePromptBuilder(ABC):
    """
    Base interface for prompt builders.
    """

    @abstractmethod
    def build(
        self,
        query: str,
        documents: list[dict[str, Any]],
    ) -> str:
        """
        Build the final prompt.
        """
        raise NotImplementedError