from __future__ import annotations
import time
from typing import Optional
from google import genai
from google.genai.types import GenerateContentConfig

from app.config import settings
from app.llm.base import BaseLLM
from app.llm.response import LLMResponse
from app.llm.utils import clean_response
from app.utils.exceptions import LLMProviderError
from app.utils.logger import logger


class GeminiLLM(BaseLLM):
    """Production-grade Gemini LLM provider using modern google-genai SDK."""

    _client: Optional[genai.Client] = None
    client: Optional[genai.Client] = None

    def __init__(self):
        if GeminiLLM._client is None:
            if not settings.GEMINI_API_KEY:
                logger.warning("GEMINI_API_KEY is not set. Gemini client calls may fail.")
            else:
                logger.info("Initializing Gemini client with google-genai SDK...")
                GeminiLLM._client = genai.Client(api_key=settings.GEMINI_API_KEY)
                logger.success("Gemini client initialized successfully.")
        self.client = GeminiLLM._client

    def generate(self, prompt: str) -> LLMResponse:
        """Generate response from Gemini API with automatic model fallback and rate limit retry backoff."""
        if self.client is None:
            if settings.GEMINI_API_KEY:
                GeminiLLM._client = genai.Client(api_key=settings.GEMINI_API_KEY)
                self.client = GeminiLLM._client
            else:
                raise LLMProviderError("Gemini API Key missing")

        active_client = self.client
        if active_client is None:
            raise LLMProviderError("Gemini client uninitialized")

        # Candidate models ordered by priority
        candidate_models = [settings.GEMINI_MODEL, "gemini-2.0-flash", "gemini-2.0-flash-lite", "gemini-1.5-flash"]
        # Deduplicate preserving order
        candidate_models = list(dict.fromkeys(candidate_models))

        for model_name in candidate_models:
            logger.info(f"Attempting generation with Gemini model '{model_name}'...")

            for attempt in range(settings.MAX_RETRIES):
                try:
                    response = active_client.models.generate_content(
                        model=model_name,
                        contents=prompt,
                        config=GenerateContentConfig(
                            temperature=settings.TEMPERATURE,
                            top_p=settings.TOP_P,
                            max_output_tokens=settings.MAX_OUTPUT_TOKENS,
                        ),
                    )

                    raw_text = response.text or ""
                    cleaned = clean_response(raw_text)

                    # Extract token metrics if available
                    prompt_tokens = getattr(response.usage_metadata, "prompt_token_count", 0) if hasattr(response, "usage_metadata") else 0
                    completion_tokens = getattr(response.usage_metadata, "candidates_token_count", 0) if hasattr(response, "usage_metadata") else 0

                    logger.success(f"Received valid response from Gemini model '{model_name}' (Tokens: {prompt_tokens + completion_tokens})")

                    return LLMResponse(
                        answer=cleaned,
                        model_name=model_name,
                        prompt_tokens=prompt_tokens,
                        completion_tokens=completion_tokens,
                        total_tokens=prompt_tokens + completion_tokens,
                    )

                except Exception as e:
                    err_msg = str(e)
                    logger.warning(f"Gemini API attempt {attempt + 1}/{settings.MAX_RETRIES} for '{model_name}' failed: {err_msg[:120]}")

                    # If model not found (404), break immediately to try next model in candidate_models
                    if "404" in err_msg or "NOT_FOUND" in err_msg or "not available" in err_msg:
                        logger.info(f"Model '{model_name}' unavailable (404). Falling back to next candidate model...")
                        break

                    # If rate limited (429), exponential backoff sleep before retrying
                    if "429" in err_msg or "RESOURCE_EXHAUSTED" in err_msg:
                        sleep_time = 2 * (attempt + 1)
                        logger.info(f"Rate limit encountered. Sleeping {sleep_time}s before retry...")
                        time.sleep(sleep_time)

        # Fallback response if API rate limits persist
        logger.warning("All Gemini API models rate limited. Returning fallback response.")
        return LLMResponse(
            answer="I am currently experiencing high API demand from Gemini rate limits. Please try your request again in a few moments.",
            model_name=settings.GEMINI_MODEL,
        )