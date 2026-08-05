from __future__ import annotations
import time
from typing import Optional
from groq import Groq

from app.config import settings
from app.llm.base import BaseLLM
from app.llm.response import LLMResponse
from app.llm.utils import clean_response, get_live_setting
from app.utils.exceptions import LLMProviderError
from app.utils.logger import logger


class GroqLLM(BaseLLM):
    """Production-grade Groq LLM provider supporting Qwen and Llama models with live configuration hot-reloading."""

    _client: Optional[Groq] = None
    client: Optional[Groq] = None
    _api_key_used: str = ""

    def __init__(self):
        api_key = get_live_setting("GROQ_API_KEY", "")
        if GroqLLM._client is None or GroqLLM._api_key_used != api_key:
            if not api_key:
                logger.warning("GROQ_API_KEY is not set. Groq client calls may fail.")
            else:
                logger.info("Initializing Groq client SDK...")
                GroqLLM._client = Groq(api_key=api_key)
                GroqLLM._api_key_used = api_key
                logger.success("Groq client initialized successfully.")
        self.client = GroqLLM._client

    def generate(self, prompt: str) -> LLMResponse:
        """Generate response from Groq API with retries and automatic candidate model fallbacks."""
        api_key = get_live_setting("GROQ_API_KEY", "")
        if self.client is None or GroqLLM._api_key_used != api_key:
            if api_key:
                GroqLLM._client = Groq(api_key=api_key)
                GroqLLM._api_key_used = api_key
                self.client = GroqLLM._client
            else:
                raise LLMProviderError("Groq API Key missing")

        active_client = self.client
        if active_client is None:
            raise LLMProviderError("Groq client uninitialized")

        # Dynamically read current GROQ_MODEL from .env
        configured_model = get_live_setting("GROQ_MODEL", "llama-3.3-70b-versatile")

        candidate_models = [configured_model, "llama-3.3-70b-versatile", "qwen/qwen3.6-27b", "llama-3.1-8b-instant"]
        candidate_models = list(dict.fromkeys(candidate_models))

        for model_name in candidate_models:
            logger.info(f"Sending generation request to Groq model '{model_name}'...")

            for attempt in range(settings.MAX_RETRIES):
                try:
                    response = active_client.chat.completions.create(
                        model=model_name,
                        messages=[{"role": "user", "content": prompt}],
                        temperature=settings.TEMPERATURE,
                        top_p=settings.TOP_P,
                        max_tokens=settings.MAX_OUTPUT_TOKENS,
                    )

                    choice = response.choices[0]
                    raw_text = choice.message.content or ""
                    cleaned = clean_response(raw_text)

                    prompt_tokens = response.usage.prompt_tokens if response.usage else 0
                    completion_tokens = response.usage.completion_tokens if response.usage else 0
                    total_tokens = response.usage.total_tokens if response.usage else (prompt_tokens + completion_tokens)

                    logger.success(f"Received valid response from Groq model '{model_name}' (Tokens: {total_tokens})")

                    return LLMResponse(
                        answer=cleaned,
                        model_name=model_name,
                        prompt_tokens=prompt_tokens,
                        completion_tokens=completion_tokens,
                        total_tokens=total_tokens,
                    )

                except Exception as e:
                    err_msg = str(e)
                    logger.warning(f"Groq API attempt {attempt + 1}/{settings.MAX_RETRIES} for '{model_name}' failed: {err_msg[:120]}")

                    if "404" in err_msg or "model_decommissioned" in err_msg or "not_found" in err_msg:
                        logger.info(f"Model '{model_name}' decommissioned/unavailable. Falling back to next model...")
                        break

                    if "429" in err_msg or "rate_limit" in err_msg:
                        sleep_time = 2 * (attempt + 1)
                        logger.info(f"Rate limit hit on Groq. Sleeping {sleep_time}s before retry...")
                        time.sleep(sleep_time)

        raise LLMProviderError("Groq LLM Provider failed across all models and retry attempts")
