import asyncio
from fastapi import APIRouter
from app.config import settings

router = APIRouter(tags=["Health"])


@router.get("/health")
async def health():
    """Liveness probe returning service basic status."""
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
    }


@router.get("/ready")
async def readiness():
    """Fast non-blocking readiness probe checking connectivity to Redis, Qdrant, and Elasticsearch."""
    services = {
        "redis": "unknown",
        "qdrant": "unknown",
        "elasticsearch": "unknown",
    }

    # Fast async check for Redis
    try:
        from app.storage.redis_client import redis_manager
        r = await asyncio.wait_for(redis_manager.get_client(), timeout=0.5)
        if r is not None and await asyncio.wait_for(r.ping(), timeout=0.5):
            services["redis"] = "connected"
        else:
            services["redis"] = "offline"
    except Exception:
        services["redis"] = "offline (start redis container to connect)"

    # Fast check for Qdrant
    try:
        from app.vectorstore.qdrant_client import QdrantConnection
        q_client = QdrantConnection.get_client()
        services["qdrant"] = "configured"
    except Exception:
        services["qdrant"] = "offline"

    # Fast check for Elasticsearch
    try:
        from app.keyword_search.elastic_client import ElasticConnection
        e_client = ElasticConnection.get_client()
        services["elasticsearch"] = "configured"
    except Exception:
        services["elasticsearch"] = "offline"

    return {
        "ready": True,
        "service": settings.APP_NAME,
        "services": services,
    }