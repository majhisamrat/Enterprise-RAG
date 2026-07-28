import json
import time
from typing import Any, Dict, Optional
import redis.asyncio as aioredis

from loguru import logger
from app.config import settings


class RedisManager:
    """Async Redis client wrapper with protocol v2 compatibility and in-memory fallback."""

    def __init__(self, redis_url: str = settings.REDIS_URL):
        self.redis_url = redis_url
        self._redis: Optional[aioredis.Redis] = None
        self._memory_cache: Dict[str, Dict[str, Any]] = {}

    async def get_client(self) -> Optional[aioredis.Redis]:
        if self._redis is None:
            try:
                self._redis = aioredis.from_url(
                    self.redis_url,
                    encoding="utf-8",
                    decode_responses=True,
                    protocol=2,  # Force RESP2 for compatibility with all Redis versions
                )
            except Exception as e:
                logger.warning(f"Failed to connect to Redis at {self.redis_url}: {e}. Falling back to in-memory store.")
                self._redis = None
        return self._redis

    async def set_cache(self, key: str, value: Any, ttl: Optional[int] = 3600) -> bool:
        """Set key-value in Redis cache (or in-memory fallback) with TTL."""
        val_str = json.dumps(value) if isinstance(value, (dict, list)) else str(value)
        try:
            client = await self.get_client()
            if client:
                if ttl:
                    await client.set(key, val_str, ex=ttl)
                else:
                    await client.set(key, val_str)
                return True
        except Exception as e:
            logger.warning(f"Redis SET fallback for key '{key}': {e}")

        # In-memory store fallback
        expire_at = time.time() + ttl if ttl else None
        self._memory_cache[key] = {"val": val_str, "expire_at": expire_at}
        return True

    async def get_cache(self, key: str) -> Optional[Any]:
        """Get value from Redis cache or in-memory fallback."""
        try:
            client = await self.get_client()
            if client:
                val = await client.get(key)
                if val is not None:
                    try:
                        return json.loads(val)
                    except (json.JSONDecodeError, TypeError):
                        return val
        except Exception as e:
            logger.warning(f"Redis GET fallback for key '{key}': {e}")

        # In-memory check
        entry = self._memory_cache.get(key)
        if entry:
            if entry["expire_at"] and time.time() > entry["expire_at"]:
                del self._memory_cache[key]
                return None
            try:
                return json.loads(entry["val"])
            except (json.JSONDecodeError, TypeError):
                return entry["val"]
        return None

    async def delete_cache(self, key: str) -> bool:
        """Delete key from Redis or in-memory cache."""
        try:
            client = await self.get_client()
            if client:
                await client.delete(key)
        except Exception as e:
            logger.warning(f"Redis DELETE fallback for key '{key}': {e}")

        self._memory_cache.pop(key, None)
        return True

    async def blacklist_token(self, token: str, expire_seconds: int) -> bool:
        """Blacklist a JWT token."""
        return await self.set_cache(f"blacklist:{token}", "1", ttl=expire_seconds)

    async def is_token_blacklisted(self, token: str) -> bool:
        """Check if JWT token is blacklisted."""
        res = await self.get_cache(f"blacklist:{token}")
        return res is not None

    async def close(self):
        """Close Redis connection pool."""
        if self._redis:
            try:
                await self._redis.close()
            except Exception:
                pass
            self._redis = None


redis_manager = RedisManager()
