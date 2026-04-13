from typing import Optional

import redis.asyncio as aioredis

from app.core.config import settings

redis_pool: Optional[aioredis.Redis] = None


async def init_redis() -> None:
    """Initialize Redis connection pool."""
    global redis_pool
    redis_pool = aioredis.from_url(
        settings.REDIS_URL,
        encoding="utf8",
        decode_responses=True,
    )


async def close_redis() -> None:
    """Close Redis connection pool."""
    global redis_pool
    if redis_pool:
        await redis_pool.close()


async def get_redis() -> aioredis.Redis:
    """Get Redis client for dependency injection."""
    if redis_pool is None:
        raise RuntimeError("Redis pool not initialized")
    return redis_pool
