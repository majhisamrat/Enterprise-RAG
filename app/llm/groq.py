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

    def __init__(self, model_override: Optional[str] = None, temperature_override: Optional[float] = None):
        """
        Initialize Groq LLM client.
        
        Args:
            model_override: Override the default model from settings
            temperature_override: Override the default temperature from settings
        """
        self.model_override = model_override
        self.temperature_override = temperature_override
        
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

        # Dynamically read current GROQ_MODEL from .env or use override
        configured_model = self.model_override or get_live_setting("GROQ_MODEL", "llama-3.2-90b-vision-preview")
        temperature = self.temperature_override if self.temperature_override is not None else settings.TEMPERATURE

        # Current working Groq models (verified available 2026-08-20)
        candidate_models = [
            configured_model,  
            "llama-3.1-70b-versatile",       # Stable fallback          
            "openai/gpt-oss-20b"
        ]
        candidate_models = list(dict.fromkeys(candidate_models))

        groq_error = None
        for model_name in candidate_models:
            logger.info(f"Sending generation request to Groq model '{model_name}'...")

            for attempt in range(settings.MAX_RETRIES):
                try:
                    response = active_client.chat.completions.create(
                        model=model_name,
                        messages=[{"role": "user", "content": prompt}],
                        temperature=temperature,
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
                    groq_error = err_msg
                    logger.warning(f"Groq API attempt {attempt + 1}/{settings.MAX_RETRIES} for '{model_name}' failed: {err_msg[:120]}")

                    if "404" in err_msg or "model_decommissioned" in err_msg or "not_found" in err_msg or "does not exist" in err_msg:
                        logger.info(f"Model '{model_name}' decommissioned/unavailable. Falling back to next model...")
                        break

                    if "429" in err_msg or "rate_limit" in err_msg:
                        sleep_time = 2 * (attempt + 1)
                        logger.info(f"Rate limit hit on Groq. Sleeping {sleep_time}s before retry...")
                        time.sleep(sleep_time)

        # Groq failed - try Gemini as fallback
        logger.warning(f"Groq LLM failed ({groq_error}). Attempting Gemini fallback...")
        try:
            from app.llm.gemini import GeminiLLM
            gemini_llm = GeminiLLM()
            return gemini_llm.generate(prompt)
        except Exception as gemini_err:
            logger.error(f"Gemini fallback also failed: {gemini_err}")
            raise LLMProviderError(f"All LLM providers failed. Groq: {groq_error}, Gemini: {gemini_err}")
