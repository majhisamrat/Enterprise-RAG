import os
import re
from pathlib import Path

from app.config import settings


def get_live_setting(key: str, fallback: str = "") -> str:
    """Read configuration key directly from .env file to support live hot-reloading without server restarts."""
    env_file = Path(__file__).resolve().parent.parent.parent / ".env"
    if env_file.exists():
        try:
            for line in env_file.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if line.startswith(f"{key}="):
                    val = line.split("=", 1)[1].strip().strip('"').strip("'")
                    if val:
                        return val
        except Exception:
            pass
    val = os.getenv(key)
    if val:
        return val
    return str(getattr(settings, key, fallback) or fallback)


def clean_response(text: str) -> str:
    """Clean unnecessary whitespace from model output."""
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]+", " ", text)
    return text.strip()


def count_characters(text: str) -> int:
    """Count characters."""
    return len(text)


def truncate_prompt(prompt: str, max_characters: int = 30000) -> str:
    """Prevent overly long prompts."""
    if len(prompt) <= max_characters:
        return prompt
    return prompt[:max_characters]