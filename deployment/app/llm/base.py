from __future__ import annotations
from abc import ABC, abstractmethod
from app.llm.response import LLMResponse


class BaseLLM(ABC):
    """Base interface for all LLM providers."""

    @abstractmethod
    def generate(self, prompt: str) -> LLMResponse:
        """Generate a response from the model."""
        raise NotImplementedError