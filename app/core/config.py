from functools import lru_cache

from pydantic import BaseModel


class Settings(BaseModel):
    app_name: str = "FastAPI Tutorial Project"
    debug: bool = True
    max_page_size: int = 50
    allowed_origins: list[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    # Postgres async URL (Docker Compose will provide env vars).
    pg_database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/appdb"
    sqlite_database_url: str = "sqlite+aiosqlite:///./app.db"
    redis_url: str = "redis://redis:6379"


@lru_cache
def get_settings() -> Settings:
    # In a real app, populate from env vars or files.
    return Settings()
