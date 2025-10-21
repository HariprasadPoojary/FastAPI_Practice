# app/core/middleware.py
import time
import uuid

from fastapi import FastAPI, Request
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.gzip import GZipMiddleware

from app.core.config import get_settings


def setup_middleware(app: FastAPI) -> None:
    settings = get_settings()

    # 1) CORS: allow your frontend origins.
    app.add_middleware(
        CORSMiddleware,
        allow_origins=getattr(
            settings,
            "allowed_origins",
            ["http://localhost:3000", "http://127.0.0.1:3000"],
        ),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 2) GZip: compress JSON/text responses to save bandwidth.
    app.add_middleware(GZipMiddleware, minimum_size=512)

    # 3) Timing: add X-Process-Time to each response.
    @app.middleware("http")
    async def add_timing_header(request: Request, call_next):
        start = time.perf_counter()
        response = await call_next(request)
        duration = time.perf_counter() - start
        response.headers["X-Process-Time"] = f"{duration:.4f}s"
        return response

    # 4) Request ID: ensure every response has an X-Request-ID header.
    @app.middleware("http")
    async def ensure_request_id(request: Request, call_next):
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        response = await call_next(request)
        response.headers.setdefault("X-Request-ID", request_id)
        return response
