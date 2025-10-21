import logging

from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from redis.asyncio import Redis
from redis.exceptions import ConnectionError as RedisConnectionError

from app.core.config import get_settings

logger = logging.getLogger(__name__)


async def init_cache() -> None:
    settings = get_settings()
    try:
        redis = Redis.from_url(
            settings.redis_url, encoding="utf-8", decode_responses=True
        )
        FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")
        logger.info("Cache initialized successfully")
    except (RedisConnectionError, ConnectionRefusedError) as e:
        logger.warning(f"Failed to connect to Redis for caching: {e}")
        logger.warning(
            "Caching will be disabled. Install and start Redis to enable it."
        )
