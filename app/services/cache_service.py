"""Caching service with in-memory and optional Redis support."""

import hashlib
import json
import logging
import time
from typing import Any, Optional

from app.config import Settings, get_settings

logger = logging.getLogger(__name__)


class CacheService:
    """Caching service with TTL support."""

    def __init__(self, settings: Optional[Settings] = None):
        """
        Initialize cache service.

        Args:
            settings: Application settings (optional)

        Example:
            ```python
            cache = CacheService()
            await cache.set("key", "value", ttl=3600)
            ```
        """
        self.settings = settings or get_settings()
        self._cache: dict = {}
        self._redis_client: Optional[Any] = None
        self._use_redis = False

        if self.settings.ENABLE_CACHE and self.settings.REDIS_URL:
            try:
                import redis.asyncio as redis

                self._redis_client = redis.from_url(
                    self.settings.REDIS_URL, decode_responses=True
                )
                self._use_redis = True
                logger.info("Redis cache enabled")
            except ImportError:
                logger.warning("Redis not available, using in-memory cache")
            except Exception as e:
                logger.warning(f"Failed to connect to Redis: {e}, using in-memory cache")

        if not self._use_redis:
            logger.info("Using in-memory cache")

    def _generate_key(self, *args: Any, **kwargs: Any) -> str:
        """
        Generate cache key from arguments.

        Args:
            *args: Positional arguments
            **kwargs: Keyword arguments

        Returns:
            str: Cache key
        """
        key_data = {"args": args, "kwargs": kwargs}
        key_str = json.dumps(key_data, sort_keys=True)
        return hashlib.md5(key_str.encode()).hexdigest()

    async def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache.

        Args:
            key: Cache key

        Returns:
            Optional[Any]: Cached value or None

        Example:
            ```python
            value = await cache.get("my_key")
            ```
        """
        if not self.settings.ENABLE_CACHE:
            return None

        try:
            if self._use_redis and self._redis_client:
                value = await self._redis_client.get(key)
                if value:
                    return json.loads(value)
            else:
                entry = self._cache.get(key)
                if entry:
                    if time.time() < entry["expires_at"]:
                        return entry["value"]
                    else:
                        # Expired, remove it
                        del self._cache[key]
        except Exception as e:
            logger.warning(f"Cache get failed for key {key}: {e}")

        return None

    async def set(
        self, key: str, value: Any, ttl: Optional[int] = None
    ) -> None:
        """
        Set value in cache.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds (uses default if None)

        Example:
            ```python
            await cache.set("my_key", {"data": "value"}, ttl=3600)
            ```
        """
        if not self.settings.ENABLE_CACHE:
            return

        ttl = ttl or self.settings.CACHE_TTL_SECONDS

        try:
            if self._use_redis and self._redis_client:
                await self._redis_client.setex(
                    key, ttl, json.dumps(value)
                )
            else:
                self._cache[key] = {
                    "value": value,
                    "expires_at": time.time() + ttl,
                }
                # Clean up old entries if cache is too large
                if len(self._cache) > self.settings.CACHE_MAX_SIZE:
                    self._cleanup_expired()
        except Exception as e:
            logger.warning(f"Cache set failed for key {key}: {e}")

    async def delete(self, key: str) -> None:
        """
        Delete value from cache.

        Args:
            key: Cache key

        Example:
            ```python
            await cache.delete("my_key")
            ```
        """
        try:
            if self._use_redis and self._redis_client:
                await self._redis_client.delete(key)
            else:
                self._cache.pop(key, None)
        except Exception as e:
            logger.warning(f"Cache delete failed for key {key}: {e}")

    async def clear(self) -> None:
        """
        Clear all cache entries.

        Example:
            ```python
            await cache.clear()
            ```
        """
        try:
            if self._use_redis and self._redis_client:
                await self._redis_client.flushdb()
            else:
                self._cache.clear()
        except Exception as e:
            logger.warning(f"Cache clear failed: {e}")

    def _cleanup_expired(self) -> None:
        """Remove expired entries from in-memory cache."""
        current_time = time.time()
        expired_keys = [
            key
            for key, entry in self._cache.items()
            if entry["expires_at"] < current_time
        ]
        for key in expired_keys:
            del self._cache[key]

    async def close(self) -> None:
        """Close cache connections."""
        if self._use_redis and self._redis_client:
            await self._redis_client.close()


# Global cache service instance
_cache_service: Optional[CacheService] = None


def get_cache_service(settings: Optional[Settings] = None) -> CacheService:
    """
    Get global cache service instance.

    Args:
        settings: Application settings (optional)

    Returns:
        CacheService: Cache service instance

    Example:
        ```python
        cache = get_cache_service()
        ```
    """
    global _cache_service
    if _cache_service is None:
        _cache_service = CacheService(settings)
    return _cache_service

