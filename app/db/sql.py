from typing import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import get_settings
from app.db.models import Base

_settings = get_settings()
engine = create_async_engine(
    _settings.sqlite_database_url,
    echo=_settings.debug,
    pool_size=5,
    max_overflow=10,
)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)


async def get_session() -> AsyncIterator[AsyncSession]:
    async with SessionLocal() as session:
        yield session


# Optional: one-time schema creation (dev only). Prefer Alembic in prod.
async def create_schema() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
