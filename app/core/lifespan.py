from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI

from app.core.cache import init_cache
from app.core.rate_limit import init_rate_limiter
from app.db.sql import create_schema


# Example: pretend we initialize a metrics client or cache connection.
class MetricsClient:
    def __init__(self) -> None:
        self.enabled = False

    async def connect(self) -> None:
        self.enabled = True

    async def close(self) -> None:
        self.enabled = False


metrics_client = MetricsClient()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Application lifespan events."""
    # Startup
    await metrics_client.connect()
    await create_schema()  # Dev-only; remove if you use Alembic migrations.
    app.state.metrics = metrics_client
    await init_cache()  # Initialize cache (e.g., Redis)
    await init_rate_limiter()  # Initialize rate limiter (e.g., Redis)
    try:
        yield
    finally:
        # Shutdown
        await metrics_client.close()  # Shutdown
