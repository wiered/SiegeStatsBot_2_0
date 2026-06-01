import hashlib
import json
import logging
from typing import Any

import redis.asyncio as redis
from redis.exceptions import RedisError


logger = logging.getLogger(__name__)


def make_r6data_cache_key(params: dict[str, str]) -> str:
    request_type = params.get("type", "unknown")
    platform = params.get("platformType", "unknown").casefold()
    username = params.get("nameOnPlatform", "").strip().casefold()
    payload = json.dumps(params, sort_keys=True, separators=(",", ":"))
    digest = hashlib.sha256(payload.encode()).hexdigest()[:16]
    return f"r6data:v1:{request_type}:{platform}:{username}:{digest}"


class RedisJsonCache:
    def __init__(self, redis_url: str, default_ttl_seconds: int = 900) -> None:
        self.redis_url = redis_url
        self.default_ttl_seconds = default_ttl_seconds
        self._client: redis.Redis | None = None

    async def connect(self) -> None:
        if self._client is not None:
            return

        client: redis.Redis | None = None
        try:
            client = redis.from_url(self.redis_url, decode_responses=True)
            await client.ping()
        except (RedisError, ValueError):
            logger.exception("Redis cache is unavailable")
            if client is not None:
                await client.aclose()
            return

        self._client = client

    async def close(self) -> None:
        if self._client is None:
            return

        try:
            await self._client.aclose()
        except RedisError:
            logger.exception("Failed to close Redis cache connection")
        finally:
            self._client = None

    async def get_json(self, key: str) -> dict[str, Any] | None:
        if self._client is None:
            return None

        try:
            raw = await self._client.get(key)
        except RedisError:
            logger.exception("Failed to read Redis cache key %s", key)
            return None

        if raw is None:
            return None

        try:
            value = json.loads(raw)
        except json.JSONDecodeError:
            logger.exception("Redis cache key %s contains invalid JSON", key)
            return None

        return value if isinstance(value, dict) else None

    async def set_json(
        self,
        key: str,
        value: dict[str, Any],
        ttl_seconds: int | None = None,
    ) -> None:
        if self._client is None:
            return

        ttl = ttl_seconds if ttl_seconds is not None else self.default_ttl_seconds
        raw = json.dumps(value, separators=(",", ":"), ensure_ascii=False)
        try:
            await self._client.set(key, raw, ex=ttl)
        except RedisError:
            logger.exception("Failed to write Redis cache key %s", key)
