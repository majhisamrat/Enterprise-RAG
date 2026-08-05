import time

try:
    from elasticsearch import Elasticsearch
    HAS_ELASTICSEARCH = True
except ImportError:
    Elasticsearch = None
    HAS_ELASTICSEARCH = False

from app.config.settings import settings


class ElasticConnection:
    """Singleton Elasticsearch client with circuit breaker for offline detection."""

    _client = None
    _offline = not HAS_ELASTICSEARCH
    _offline_since: float = 0.0
    _retry_interval = 60  # retry connecting every 60 seconds

    @classmethod
    def is_available(cls) -> bool:
        """Check if Elasticsearch is available (circuit breaker not tripped)."""
        if not HAS_ELASTICSEARCH:
            return False
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
        if not HAS_ELASTICSEARCH:
            return None
        if cls._client is None:
            es_url = settings.ELASTICSEARCH_URL or "http://localhost:9200"
            cls._client = Elasticsearch(
                hosts=[es_url],
                request_timeout=settings.SEARCH_CONNECT_TIMEOUT_SECONDS,
                max_retries=0,
            )
        return cls._client
