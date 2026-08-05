from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class LLMResponse(BaseModel):
    """Standardized Pydantic response format for LLM outputs."""

    answer: str
    model_name: str = "gemini-2.5-flash"
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    sources: List[Dict[str, Any]] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    @classmethod
    def build(
        cls,
        answer: str,
        sources: Optional[List[Dict[str, Any]]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        return {
            "answer": answer,
            "sources": sources or [],
            "metadata": metadata or {},
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }