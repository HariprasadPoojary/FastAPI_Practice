from fastapi import FastAPI

from app.api.v1.auth import router as v1_auth_router
from app.api.v1.items import router as v1_items_router
from app.api.v2.items import router as v2_items_router
from app.api.v2.stream import router as v2_stream_router
from app.api.v2.system import router as v2_system_router
from app.api.v2.uploads import router as v2_uploads_router
from app.api.v2.web_sockets import router as v2_ws_router
from app.core.errors import register_exception_handlers
from app.core.lifespan import lifespan
from app.core.middleware import setup_middleware

app = FastAPI(
    title="FastAPI docs",
    version="0.2.0",
    description="Modular, versioned FastAPI project with routers, models, dependencies, caching and a simple DB.",
    lifespan=lifespan,
)

# Install middleware.
setup_middleware(app)
# Register exception handlers.
register_exception_handlers(app)


@app.get("/", tags=["root"])
def read_root() -> dict[str, str]:
    return {"message": "Hello from FastAPI (modular)!"}


# Include routers with API version prefixes.
# v1
app.include_router(v1_items_router, prefix="/api/v1", tags=["v1: items"])
app.include_router(v1_auth_router, prefix="/api/v1", tags=["v1: auth"])

# v2
app.include_router(v2_items_router, prefix="/api/v2", tags=["v2: items"])
app.include_router(v2_system_router, prefix="/api/v2", tags=["v2: system"])
app.include_router(v2_stream_router, prefix="/api/v2", tags=["v2: stream"])
app.include_router(v2_uploads_router, prefix="/api/v2", tags=["v2: files"])
app.include_router(v2_ws_router, prefix="/api/v2", tags=["v2: websockets"])
