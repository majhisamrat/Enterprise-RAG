from pathlib import Path
from typing import Optional

ALLOWED_EXTENSIONS = {
    ".pdf",
    ".docx",
    ".pptx",
    ".txt",
    ".md",
    ".csv",
}


def validate_extension(filename: Optional[str]) -> str:
    """Validate file extension and return normalized lower-case extension string."""
    if not filename:
        raise ValueError("Filename cannot be empty")
    extension = Path(filename).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise ValueError(f"File extension '{extension}' is not supported. Supported extensions: {', '.join(sorted(ALLOWED_EXTENSIONS))}")

    return extension