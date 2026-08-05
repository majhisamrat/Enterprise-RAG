import hashlib
import re
from datetime import datetime, timezone
from typing import Generator, List, TypeVar

T = TypeVar("T")


def sanitize_filename(filename: str) -> str:
    """Sanitize a filename by removing unsafe characters."""
    filename = re.sub(r"[^\w\s.-]", "", filename).strip()
    return re.sub(r"\s+", "_", filename)


def calculate_checksum(content: bytes) -> str:
    """Calculate SHA256 checksum for byte content."""
    return hashlib.sha256(content).hexdigest()


def format_bytes(size: int) -> str:
    """Format size in bytes into human-readable string (KB, MB, GB)."""
    if size < 1024:
        return f"{size} B"
    num = float(size)
    for unit in ["KB", "MB", "GB", "TB"]:
        num /= 1024.0
        if num < 1024:
            return f"{num:.2f} {unit}"
    return f"{num:.2f} PB"


def chunk_list(items: List[T], batch_size: int) -> Generator[List[T], None, None]:
    """Yield successive batches from a list."""
    for i in range(0, len(items), batch_size):
        yield items[i : i + batch_size]


def get_utc_now() -> datetime:
    """Return current UTC datetime with timezone info."""
    return datetime.now(timezone.utc)
