import time

from qdrant_client import QdrantClient

from app.config.settings import settings


class QdrantConnection:
    """Singleton Qdrant client with circuit breaker for offline detection."""

    _client = None
    _offline = False
    _offline_since: float = 0.0
    _retry_interval = 60  # retry connecting every 60 seconds

    @classmethod
    def is_available(cls) -> bool:
        """Check if Qdrant is available (circuit breaker not tripped)."""
        if not cls._offline:
            return True
        # Auto-retry after cooldown
        if time.time() - cls._offline_since > cls._retry_interval:
            cls._offline = False
            return True
        return False

    @classmethod
    def mark_offline(cls):
        """Trip the circuit breaker."""
        cls._offline = True
        cls._offline_since = time.time()

    @classmethod
    def get_client(cls):
        if cls._client is None:
            cls._client = QdrantClient(
                host=settings.QDRANT_HOST,
                port=settings.QDRANT_PORT,
                timeout=settings.SEARCH_CONNECT_TIMEOUT_SECONDS,
                check_compatibility=False,
            )
        return cls._client

