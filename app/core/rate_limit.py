import logging

from fastapi import Request
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
from jose import JWTError, jwt
from redis.asyncio import Redis
from redis.exceptions import ConnectionError as RedisConnectionError

from app.core.config import get_settings
from app.core.security import ALGORITHM, SECRET_KEY

logger = logging.getLogger(__name__)


async def init_rate_limiter() -> None:
    settings = get_settings()
    try:
        redis = Redis.from_url(
            settings.redis_url, encoding="utf-8", decode_responses=True
        )
        await FastAPILimiter.init(redis)
        logger.info("Rate limiter initialized successfully")
    except (RedisConnectionError, ConnectionRefusedError) as e:
        logger.warning(f"Failed to connect to Redis for rate limiting: {e}")
        logger.warning(
            "Rate limiting will be disabled. Install and start Redis to enable it."
        )


def limit_ip(times: int = 20, seconds: int = 60) -> RateLimiter:
    """Limit requests by IP address."""
    # Default identifier is client IP + path.
    return RateLimiter(times=times, seconds=seconds)


def _user_identifier(request: Request) -> str:
    # Derive user identity from JWT Bearer token subject; fallback to IP if absent/invalid.
    auth = request.headers.get("Authorization", "")
    if auth.startswith("Bearer "):
        token = auth.split(" ", 1)[1]
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            sub = payload.get("sub") or "anonymous"
            return f"user:{sub}:{request.url.path}"
        except JWTError:
            pass
    # Fallback: rate limit by IP for unauthenticated or invalid tokens.
    client_ip = request.client.host if request.client else "unknown"
    return f"ip:{client_ip}:{request.url.path}"


def limit_user(times: int = 10, seconds: int = 60) -> RateLimiter:
    return RateLimiter(times=times, seconds=seconds, identifier=_user_identifier)
