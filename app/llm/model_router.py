"""
PHASE 1: Model Router

Routes LLM requests to appropriate models:
- General queries: Groq (llama-3.3-70b) or Gemini (gemini-2.0-flash)
- Code generation (SQL/DuckDB): Qwen Coder (optimized for structured query generation)

Environment Variables:
- LLM_PROVIDER: "groq" | "gemini" (for general queries)
- LLM_CODEGEN_MODEL_PROVIDER: "groq" | "gemini" (for code generation)
- LLM_CODEGEN_MODEL: model name (e.g., "qwen2.5-coder-32b-instruct")
- LLM_CODEGEN_TEMPERATURE: temperature for codegen (default: 0.1, more deterministic)
"""

from typing import Literal, Optional
from app.config import settings
from app.llm.base import BaseLLM
from app.utils.logger import logger


ModelType = Literal["general", "codegen"]


class ModelRouter:
    """Routes LLM requests to appropriate models based on task type."""
    
    def __init__(self):
        self._general_model: Optional[BaseLLM] = None
        self._codegen_model: Optional[BaseLLM] = None
    
    def get_model(self, model_type: ModelType = "general") -> BaseLLM:
        """
        Get the appropriate model for the task.
        
        Args:
            model_type: "general" for chat/semantic tasks, "codegen" for SQL generation
        
        Returns:
            Configured LLM instance
        """
        if model_type == "general":
            return self._get_general_model()
        elif model_type == "codegen":
            return self._get_codegen_model()
        else:
            raise ValueError(f"Unknown model_type: {model_type}")
    
    def _get_general_model(self) -> BaseLLM:
        """Get general-purpose LLM for chat and semantic queries."""
        if self._general_model is None:
            provider = getattr(settings, "LLM_PROVIDER", "groq").lower()
            
            if provider == "groq":
                from app.llm.groq import GroqLLM
                self._general_model = GroqLLM()
                logger.info(f"Initialized general model: Groq/{settings.GROQ_MODEL}")
            elif provider == "gemini":
                from app.llm.gemini import GeminiLLM
                self._general_model = GeminiLLM()
                logger.info(f"Initialized general model: Gemini/{settings.GEMINI_MODEL}")
            else:
                # Default to Groq
                from app.llm.groq import GroqLLM
                self._general_model = GroqLLM()
                logger.warning(f"Unknown LLM_PROVIDER '{provider}', defaulting to Groq")
        
        return self._general_model
    
    def _get_codegen_model(self) -> BaseLLM:
        """Get code generation LLM optimized for SQL/DuckDB queries."""
        if self._codegen_model is None:
            # Check for codegen-specific settings
            codegen_provider = getattr(settings, "LLM_CODEGEN_MODEL_PROVIDER", None)
            codegen_model = getattr(settings, "LLM_CODEGEN_MODEL", None)
            codegen_temperature = getattr(settings, "LLM_CODEGEN_TEMPERATURE", 0.1)
            
            # If no codegen-specific model configured, use general model
            if not codegen_provider or not codegen_model:
                logger.info("No codegen-specific model configured, using general model")
                return self._get_general_model()
            
            # Initialize codegen-specific model
            if codegen_provider.lower() == "groq":
                from app.llm.groq import GroqLLM
                self._codegen_model = GroqLLM(
                    model_override=codegen_model,
                    temperature_override=codegen_temperature,
                )
                logger.info(f"Initialized codegen model: Groq/{codegen_model} (temp={codegen_temperature})")
            elif codegen_provider.lower() == "gemini":
                from app.llm.gemini import GeminiLLM
                self._codegen_model = GeminiLLM(
                    model_override=codegen_model,
                    temperature_override=codegen_temperature,
                )
                logger.info(f"Initialized codegen model: Gemini/{codegen_model} (temp={codegen_temperature})")
            else:
                logger.warning(f"Unknown codegen provider '{codegen_provider}', using general model")
                return self._get_general_model()
        
        return self._codegen_model
    
    def reset(self):
        """Reset cached model instances (useful for testing or config changes)."""
        self._general_model = None
        self._codegen_model = None
        logger.info("Model router cache cleared")


# Global singleton instance
_model_router = ModelRouter()


def get_model(model_type: ModelType = "general") -> BaseLLM:
    """
    Get the appropriate model for the task.
    
    Args:
        model_type: "general" for chat/semantic tasks, "codegen" for SQL generation
    
    Returns:
        Configured LLM instance
    """
    return _model_router.get_model(model_type)


def reset_router():
    """Reset the global model router (useful for testing)."""
    _model_router.reset()
