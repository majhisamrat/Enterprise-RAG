import os

from app.config import settings
from app.llm.gemini import GeminiLLM
from app.llm.groq import GroqLLM
from app.llm.utils import get_live_setting


class LLMProvider:
    """Factory for loading the configured LLM provider with hot-reload support."""

    @staticmethod
    def load():
        provider = get_live_setting("LLM_PROVIDER", "groq").lower()

        if provider == "groq":
            return GroqLLM()
        if provider == "gemini":
            return GeminiLLM()

        return GroqLLM()