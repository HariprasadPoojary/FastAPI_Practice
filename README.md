# FastAPI Project - Technical Documentation

**Version:** 0.2.0  
**Last Updated:** October 14, 2025

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Architecture](#architecture)
3. [Technology Stack](#technology-stack)
4. [Project Structure](#project-structure)
5. [Core Modules](#core-modules)
6. [Database Layer](#database-layer)
7. [API Endpoints](#api-endpoints)
8. [Authentication & Authorization](#authentication--authorization)
9. [Middleware & Error Handling](#middleware--error-handling)
10. [Caching & Rate Limiting](#caching--rate-limiting)
11. [Advanced Features](#advanced-features)
12. [Deployment Guide](#deployment-guide)

---

## 1. Project Overview

This is a **modular, production-ready FastAPI application** with comprehensive features including:

- ✅ **API Versioning** (v1 and v2 endpoints)
- ✅ **JWT-based Authentication & Authorization** with OAuth2 scopes
- ✅ **SQLAlchemy ORM** with async support (SQLite/PostgreSQL)
- ✅ **Redis-based Caching** using fastapi-cache2
- ✅ **Rate Limiting** with fastapi-limiter
- ✅ **WebSocket Support** for real-time communication
- ✅ **File Upload/Download** capabilities
- ✅ **Streaming Responses** for large datasets
- ✅ **Background Tasks** for async operations
- ✅ **Custom Error Handling** with domain-specific exceptions
- ✅ **Comprehensive Middleware** (CORS, GZip, Timing, Request ID)

---

## 2. Architecture

### High-Level Architecture Diagram

```mermaid
graph TB
    Client[Client Application]
    
    subgraph "FastAPI Application"
        MW[Middleware Layer]
        Router[API Routers]
        Core[Core Services]
        DB[Database Layer]
        Cache[Cache Layer]
        RL[Rate Limiter]
    end
    
    subgraph "External Services"
        Redis[(Redis)]
        SQLite[(SQLite/PostgreSQL)]
    end
    
    Client -->|HTTP/WS| MW
    MW --> Router
    Router --> Core
    Core --> DB
    Core --> Cache
    Core --> RL
    Cache -.->|Connection| Redis
    RL -.->|Connection| Redis
    DB -.->|Connection| SQLite
    
    style Client fill:#e1f5fe
    style MW fill:#fff3e0
    style Router fill:#f3e5f5
    style Core fill:#e8f5e9
    style DB fill:#fce4ec
    style Cache fill:#fff9c4
    style RL fill:#ffe0b2
```

### Request Flow Architecture

```mermaid
sequenceDiagram
    participant C as Client
    participant M as Middleware
    participant A as Auth Layer
    participant RL as Rate Limiter
    participant R as Router
    participant D as Dependencies
    participant DB as Database
    participant Cache as Redis Cache
    
    C->>M: HTTP Request
    M->>M: CORS Check
    M->>M: Add Request ID
    M->>M: Start Timer
    M->>A: Validate JWT Token
    A->>A: Verify Signature
    A->>A: Check Scopes
    A-->>M: User Context
    M->>RL: Check Rate Limit
    RL->>Cache: Query Counter
    Cache-->>RL: Limit Status
    RL-->>M: Allow/Deny
    M->>R: Route to Handler
    R->>D: Inject Dependencies
    D->>DB: Query Data
    DB-->>D: Result
    D-->>R: Processed Data
    R->>Cache: Store Response
    R-->>M: Response
    M->>M: Add Process Time
    M->>M: Compress (GZip)
    M-->>C: HTTP Response
```

---

## 3. Technology Stack

### Core Framework & Libraries

| Category | Technology | Version | Purpose |
|----------|-----------|---------|---------|
| **Web Framework** | FastAPI | 0.118.0 | Async web framework |
| **ASGI Server** | Uvicorn | 0.37.0 | Production ASGI server |
| **Data Validation** | Pydantic | 2.12.0 | Request/response validation |
| **ORM** | SQLAlchemy | 2.0.44 | Async database ORM |
| **Database Driver** | aiosqlite / asyncpg | 0.21.0 / 0.30.0 | Async DB drivers |
| **Caching** | fastapi-cache2 | 0.2.2 | Redis-based caching |
| **Rate Limiting** | fastapi-limiter | 0.1.6 | Request rate limiting |
| **Redis Client** | redis | 6.4.0 | Async Redis client |
| **Authentication** | python-jose | 3.5.0 | JWT token handling |
| **Password Hashing** | passlib + bcrypt | 1.7.4 / 4.0.1 | Secure password hashing |
| **File Uploads** | python-multipart | 0.0.20 | Multipart form handling |
| **WebSockets** | websockets | 15.0.1 | WebSocket support |
| **Date/Time** | pendulum | 3.1.0 | Advanced datetime handling |
| **Environment** | python-dotenv | 1.1.1 | Environment variable management |

### Development Tools

- **Database Migrations:** Alembic 1.16.5
- **HTTP Protocol:** httptools 0.6.4, h11 0.16.0
- **Event Loop:** uvloop 0.21.0 (production performance)
- **Hot Reload:** watchfiles 1.1.0 (development)

---

## 4. Project Structure

```
FastAPI_prac/
│
├── app/
│   ├── main.py                 # Application entry point
│   │
│   ├── api/                    # API route handlers
│   │   ├── v1/                 # Version 1 endpoints
│   │   │   ├── __init__.py
│   │   │   ├── auth.py         # Authentication endpoints
│   │   │   └── items.py        # Basic CRUD for items
│   │   │
│   │   └── v2/                 # Version 2 endpoints (enhanced)
│   │       ├── __init__.py
│   │       ├── items.py        # Advanced item operations
│   │       ├── stream.py       # Streaming responses
│   │       ├── system.py       # System utilities
│   │       ├── uploads.py      # File operations
│   │       └── web_sockets.py  # WebSocket endpoints
│   │
│   ├── core/                   # Core business logic
│   │   ├── __init__.py
│   │   ├── cache.py            # Redis cache initialization
│   │   ├── config.py           # Application settings
│   │   ├── dependencies.py     # FastAPI dependencies
│   │   ├── errors.py           # Custom exception handlers
│   │   ├── lifespan.py         # App startup/shutdown
│   │   ├── middleware.py       # Custom middleware
│   │   ├── rate_limit.py       # Rate limiting logic
│   │   ├── repositories.py     # Data access layer
│   │   └── security.py         # Auth & security utils
│   │
│   ├── db/                     # Database layer
│   │   ├── __init__.py
│   │   ├── db.py               # (Legacy/alternative DB)
│   │   ├── models.py           # SQLAlchemy ORM models
│   │   └── sql.py              # Database session management
│   │
│   └── models/                 # Pydantic models
│       ├── __init__.py
│       ├── common.py           # Shared models (Pagination)
│       ├── item.py             # Item schemas
│       └── user.py             # User schemas
│
├── _files/                     # File upload directory
├── requirements.txt            # Python dependencies
└── app.db                      # SQLite database (dev)
```

### Directory Responsibilities

```mermaid
graph LR
    A[main.py] --> B[api/]
    A --> C[core/]
    A --> D[db/]
    A --> E[models/]
    
    B --> B1[v1/]
    B --> B2[v2/]
    
    C --> C1[Middleware]
    C --> C2[Security]
    C --> C3[Dependencies]
    C --> C4[Cache/Rate Limit]
    
    D --> D1[ORM Models]
    D --> D2[Sessions]
    
    E --> E1[Request/Response Schemas]
    
    style A fill:#ffcdd2
    style B fill:#f8bbd0
    style C fill:#e1bee7
    style D fill:#d1c4e9
    style E fill:#c5cae9
```

---

## 5. Core Modules

### 5.1 Configuration Management (`core/config.py`)

```python
class Settings(BaseModel):
    app_name: str = "FastAPI Tutorial Project"
    debug: bool = True
    max_page_size: int = 50
    allowed_origins: list[str] = ["http://localhost:3000"]
    pg_database_url: str = "postgresql+asyncpg://..."
    sqlite_database_url: str = "sqlite+aiosqlite:///./app.db"
    redis_url: str = "redis://localhost:6379/0"
```

**Features:**
- Pydantic-based configuration with type validation
- LRU cached settings retrieval
- Environment-based overrides support
- Database URL configuration (SQLite/PostgreSQL)

### 5.2 Application Lifespan (`core/lifespan.py`)

**Startup Sequence:**
```mermaid
graph TD
    Start([App Start]) --> A[Connect Metrics Client]
    A --> B[Create Database Schema]
    B --> C[Initialize Redis Cache]
    C --> D[Initialize Rate Limiter]
    D --> E[Application Ready]
    E --> F{Shutdown Event?}
    F -->|Yes| G[Close Metrics Client]
    F -->|No| E
    G --> End([App Stop])
    
    style Start fill:#c8e6c9
    style End fill:#ffcdd2
    style E fill:#fff9c4
```

**Responsibilities:**
- Database schema creation (development)
- Redis connection initialization
- Metrics client setup
- Graceful shutdown handling

### 5.3 Middleware Stack (`core/middleware.py`)

```mermaid
graph TB
    Request[Incoming Request] --> CORS[CORS Middleware]
    CORS --> GZip[GZip Compression]
    GZip --> Timing[Process Time Tracker]
    Timing --> ReqID[Request ID Generator]
    ReqID --> Handler[Route Handler]
    Handler --> Response[Response]
    
    style Request fill:#e3f2fd
    style Response fill:#e8f5e9
    style CORS fill:#fff3e0
    style GZip fill:#fce4ec
    style Timing fill:#f3e5f5
    style ReqID fill:#e0f2f1
```

**Middleware Components:**

1. **CORS Middleware**
   - Allows specified origins
   - Supports credentials
   - All methods and headers allowed

2. **GZip Middleware**
   - Compresses responses > 512 bytes
   - Reduces bandwidth usage

3. **Timing Middleware**
   - Adds `X-Process-Time` header
   - Tracks request processing duration

4. **Request ID Middleware**
   - Generates unique request IDs
   - Preserves client-provided IDs
   - Adds `X-Request-ID` header

### 5.4 Dependency Injection (`core/dependencies.py`)

**Key Dependencies:**

| Dependency | Purpose | Returns |
|------------|---------|---------|
| `get_settings()` | App configuration | `Settings` |
| `get_session()` | Database session | `AsyncSession` |
| `get_item_repo()` | Item data access | `SQLItemRepo` |
| `get_user_repo()` | User data access | `SQLUserRepo` |
| `get_pagination()` | Pagination params | `Pagination` |
| `get_item_or_404()` | Item loader | `ItemRead` |
| `get_current_user()` | Auth verification | `UserRead` |

**Dependency Flow:**
```mermaid
graph LR
    A[Route Handler] --> B[get_current_user]
    A --> C[get_item_repo]
    A --> D[get_pagination]
    
    B --> B1[oauth2_scheme]
    B --> B2[get_user_repo]
    
    C --> C1[get_session]
    B2 --> C1
    
    D --> D1[get_settings]
    
    style A fill:#e1f5fe
    style B fill:#f3e5f5
    style C fill:#e8f5e9
    style D fill:#fff9c4
```

---

## 6. Database Layer

### 6.1 ORM Models (`db/models.py`)

**Entity Relationship Diagram:**

```mermaid
erDiagram
    ITEMS {
        int id PK
        string name
        text description
        float price
        json tags
        boolean in_stock
        datetime created_at
    }
    
    USERS {
        int id PK
        string username UK
        string full_name
        string email
        boolean is_active
        json scopes
        string hashed_password
    }
```

**ORM Model Features:**
- SQLAlchemy 2.0 Mapped columns syntax
- Async-compatible with aiosqlite/asyncpg
- JSON field support for tags and scopes
- Automatic timestamp with `server_default=func.now()`
- Indexed username for fast lookups

### 6.2 Repository Pattern (`core/repositories.py`)

**Architecture:**

```mermaid
classDiagram
    class SQLItemRepo {
        -session: AsyncSession
        +create(ItemCreate) ItemRead
        +list(q, limit) List~ItemRead~
        +get(item_id) ItemRead|None
        +update(item_id, ItemUpdate) ItemRead|None
        -_to_read(Items) ItemRead
    }
    
    class SQLUserRepo {
        -session: AsyncSession
        +create(UserCreate) UserRead
        +get_by_username(username) UserInDB|None
        -_to_read(Users) UserRead
        -_to_in_db(Users) UserInDB
    }
    
    class AsyncSession {
        +add(obj)
        +flush()
        +commit()
        +execute(stmt)
    }
    
    SQLItemRepo --> AsyncSession
    SQLUserRepo --> AsyncSession
```

**Key Features:**
- Encapsulates data access logic
- Converts ORM models to Pydantic schemas
- Async database operations
- Transaction management (commit/rollback)

### 6.3 Database Connection (`db/sql.py`)

```python
# Async engine creation
engine = create_async_engine(
    sqlite_database_url,
    echo=debug,
    pool_size=5,
    max_overflow=10
)

# Session factory
SessionLocal = async_sessionmaker(
    engine, 
    expire_on_commit=False
)
```

**Connection Pooling:**
- Pool size: 5 active connections
- Max overflow: 10 additional connections
- Async context manager for automatic cleanup

---

## 7. API Endpoints

### 7.1 API Versioning Strategy

```mermaid
graph TB
    Root[/ - Root] --> V1[/api/v1/]
    Root --> V2[/api/v2/]
    
    V1 --> V1A[/auth - Authentication]
    V1 --> V1I[/store/items - Basic CRUD]
    
    V2 --> V2I[/store/items - Advanced Items]
    V2 --> V2S[/stream - Streaming]
    V2 --> V2Sys[/compute, /health]
    V2 --> V2F[/files - Uploads/Downloads]
    V2 --> V2W[/ws - WebSockets]
    
    style Root fill:#ffebee
    style V1 fill:#e3f2fd
    style V2 fill:#e8f5e9
```

### 7.2 V1 Endpoints

#### Authentication (`/api/v1/auth`)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/signup` | Create new user | ❌ |
| POST | `/token` | Obtain JWT token | ❌ |
| GET | `/me` | Get current user info | ✅ |

**OAuth2 Flow:**
```mermaid
sequenceDiagram
    participant C as Client
    participant A as /auth/token
    participant DB as Database
    participant J as JWT Service
    
    C->>A: POST username + password
    A->>DB: Verify credentials
    DB-->>A: User + scopes
    A->>J: Generate token
    J-->>A: JWT with scopes
    A-->>C: {access_token, token_type}
    
    C->>A: GET /me (Bearer token)
    A->>J: Validate token
    J-->>A: User context
    A->>DB: Fetch user
    DB-->>A: User data
    A-->>C: User profile
```

#### Items CRUD (`/api/v1/store/items`)

| Method | Endpoint | Description | Query Params |
|--------|----------|-------------|--------------|
| GET | `/` | List items | `?q=search&limit=25` |
| GET | `/paged` | Paginated list | `?page=1&page_size=10` |
| GET | `/{item_id}` | Get single item | - |
| POST | `/` | Create item | - |
| PATCH | `/{item_id}` | Update item | - |

### 7.3 V2 Endpoints (Enhanced)

#### Advanced Items (`/api/v2/store/items`)

**Additional Features:**
- ✅ Redis caching with automatic invalidation
- ✅ Rate limiting (IP and user-based)
- ✅ Scope-based authorization
- ✅ Background task processing
- ✅ Bulk operations
- ✅ Concurrent I/O operations

| Method | Endpoint | Auth Scopes | Rate Limit |
|--------|----------|-------------|------------|
| GET | `/paged` | `items:read`, `items:write` | 3 req/60s (IP) |
| POST | `/` | `items:write` | Default |
| POST | `/bulk` | - | Default |
| GET | `/{item_id}/summary` | - | Default |
| POST | `/{item_id}/purchase` | - | Default |

**Caching Strategy:**
```mermaid
graph LR
    A[Request] --> B{Cache Hit?}
    B -->|Yes| C[Return Cached]
    B -->|No| D[Query DB]
    D --> E[Store in Cache]
    E --> F[Return Response]
    
    G[Create/Update] --> H[Clear Cache]
    H --> I[Invalidate All]
    
    style A fill:#e3f2fd
    style C fill:#c8e6c9
    style D fill:#fff9c4
    style G fill:#ffcdd2
```

#### Streaming Endpoints (`/api/v2/stream`)

| Method | Endpoint | Content-Type | Description |
|--------|----------|--------------|-------------|
| GET | `/items.csv` | text/csv | Stream CSV export (10k rows) |
| GET | `/items.txt` | text/plain | Stream text export |
| GET | `/items.json` | application/json | Stream JSON array |

**Streaming Architecture:**
```python
def generate_csv(rows: int) -> Iterator[bytes]:
    yield b"id,name\n"
    for i in range(1, rows + 1):
        yield f"{i},Item {i}\n".encode("utf-8")

return StreamingResponse(
    generate_csv(10000),
    media_type="text/csv"
)
```

#### System Utilities (`/api/v2`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/compute` | CPU-heavy task (Fibonacci) using thread pool |
| GET | `/health` | Health check with custom headers |

#### File Operations (`/api/v2/files`)

| Method | Endpoint | Description | Request Body |
|--------|----------|-------------|--------------|
| POST | `/upload` | Upload file | multipart/form-data |
| GET | `/download/{filename}` | Download file | - |
| GET | `/list` | List uploaded files | - |

**File Upload Flow:**
```mermaid
sequenceDiagram
    participant C as Client
    participant E as /files/upload
    participant FS as File System
    
    C->>E: POST multipart/form-data
    E->>E: Validate file
    E->>FS: Save in chunks (1MB)
    FS-->>E: File saved
    E-->>C: {filename, size}
```

#### WebSocket (`/api/v2/ws`)

| Endpoint | Protocol | Description |
|----------|----------|-------------|
| `/echo` | WebSocket | Bidirectional echo server |

**WebSocket Communication:**
```mermaid
sequenceDiagram
    participant C as Client
    participant W as WebSocket /echo
    
    C->>W: Connect (ws://)
    W->>W: Accept connection
    
    loop Message Exchange
        C->>W: Send: "Hello"
        W->>C: Send: "echo: Hello"
    end
    
    C->>W: Disconnect
    W->>W: Handle WebSocketDisconnect
```

---

## 8. Authentication & Authorization

### 8.1 Security Architecture

```mermaid
graph TB
    A[Client Request] --> B{Has Bearer Token?}
    B -->|No| C[401 Unauthorized]
    B -->|Yes| D[Extract JWT]
    D --> E{Valid Signature?}
    E -->|No| C
    E -->|Yes| F[Decode Payload]
    F --> G[Extract sub & scopes]
    G --> H{User Exists & Active?}
    H -->|No| C
    H -->|Yes| I{Scopes Match?}
    I -->|No| J[403 Forbidden]
    I -->|Yes| K[Allow Access]
    
    style A fill:#e3f2fd
    style C fill:#ffcdd2
    style J fill:#ffe0b2
    style K fill:#c8e6c9
```

### 8.2 JWT Token Structure

```json
{
  "sub": "username",
  "scopes": ["items:read", "items:write"],
  "exp": 1729123456
}
```

**Token Configuration:**
- **Algorithm:** HS256
- **Expiration:** 30 minutes
- **Secret Key:** Configurable (secure in production)

### 8.3 Password Security

**Hashing Strategy:**
```python
# Using bcrypt with passlib
pwd_context = CryptContext(
    schemes=["bcrypt"], 
    deprecated="auto"
)

# Hash password
hashed = pwd_context.hash(plain_password)

# Verify password
is_valid = pwd_context.verify(plain, hashed)
```

### 8.4 Scope-Based Authorization

**Available Scopes:**

| Scope | Description | Endpoints |
|-------|-------------|-----------|
| `items:read` | Read item data | GET /store/items/* |
| `items:write` | Create/update items | POST/PATCH /store/items/* |

**Enforcement Example:**
```python
@router.get("/paged")
async def list_items_paged(
    current_user: Annotated[
        object, 
        Security(get_current_user, scopes=["items:read", "items:write"])
    ]
):
    # Both scopes required
    ...
```

---

## 9. Middleware & Error Handling

### 9.1 Error Response Format

```json
{
  "error": {
    "code": "domain_error",
    "message": "Detailed error message"
  },
  "path": "/api/v2/store/items/999"
}
```

### 9.2 Custom Exception Types

```python
class DomainError(Exception):
    def __init__(
        self, 
        message: str, 
        code: str = "domain_error", 
        status_code: int = 400
    ):
        self.message = message
        self.code = code
        self.status_code = status_code
```

**Registered Handlers:**
- `DomainError` → Custom error response
- `404` → Not found error
- `500` → Internal server error

### 9.3 Response Headers

**Standard Headers Added:**

| Header | Source | Example |
|--------|--------|---------|
| `X-Process-Time` | Timing middleware | `0.0234s` |
| `X-Request-ID` | Request ID middleware | `550e8400-e29b-41d4-a716-446655440000` |
| `Content-Encoding` | GZip middleware | `gzip` |
| `Access-Control-Allow-Origin` | CORS middleware | `http://localhost:3000` |

---

## 10. Caching & Rate Limiting

### 10.1 Redis Cache Architecture

```mermaid
graph LR
    A[FastAPI App] --> B[FastAPICache]
    B --> C[RedisBackend]
    C --> D[(Redis Server)]
    
    E[GET Request] --> F{Cache Hit?}
    F -->|Yes| G[Return from Redis]
    F -->|No| H[Query Database]
    H --> I[Store in Redis]
    I --> J[Return Response]
    
    style A fill:#e3f2fd
    style D fill:#ffcdd2
    style G fill:#c8e6c9
    style H fill:#fff9c4
```

**Cache Configuration:**
```python
# Initialize at startup
await init_cache()

# Use decorator for caching
@cache(expire=60)  # Cache for 60 seconds
async def cached_endpoint():
    ...

# Manual invalidation
await FastAPICache.clear()
```

### 10.2 Rate Limiting Strategy

**Rate Limit Types:**

1. **IP-based Rate Limiting:**
```python
@router.get(
    "/paged",
    dependencies=[Depends(limit_ip(times=3, seconds=60))]
)
```

2. **User-based Rate Limiting:**
```python
@router.post(
    "/create",
    dependencies=[Depends(limit_user(times=10, seconds=60))]
)
```

**Rate Limit Flow:**
```mermaid
sequenceDiagram
    participant C as Client
    participant RL as Rate Limiter
    participant R as Redis
    
    C->>RL: Request
    RL->>R: GET counter key
    R-->>RL: Current count
    RL->>RL: Check limit
    
    alt Under limit
        RL->>R: INCR counter
        RL-->>C: Allow (200)
    else Over limit
        RL-->>C: Reject (429)
    end
```

**Identifier Strategy:**
```python
def _user_identifier(request: Request) -> str:
    # Try JWT token first
    if bearer_token:
        return f"user:{username}:{path}"
    # Fallback to IP
    return f"ip:{client_ip}:{path}"
```

---

## 11. Advanced Features

### 11.1 Background Tasks

**Use Cases:**
- Audit logging
- Email notifications
- Data processing

**Implementation:**
```python
def log_purchase(item_id: int, amount: int):
    print(f"[audit] purchase item={item_id} amount={amount}")

@router.post("/{item_id}/purchase")
async def purchase_item(
    background_tasks: BackgroundTasks
):
    background_tasks.add_task(log_purchase, item_id, amount)
    return {"status": "queued"}
```

**Execution Flow:**
```mermaid
sequenceDiagram
    participant C as Client
    participant H as Handler
    participant BG as Background Task Queue
    
    C->>H: POST request
    H->>BG: Queue task
    H-->>C: Response (immediate)
    BG->>BG: Execute after response
```

### 11.2 Concurrent I/O Operations

**Parallel Execution:**
```python
async def get_item_summary(item: ItemRead):
    # Fetch price and inventory concurrently
    price, inventory = await asyncio.gather(
        fetch_price(item.id),
        fetch_inventory(item.id)
    )
    return ItemSummary(item=item, price=price, inventory=inventory)
```

**Performance Benefit:**
```mermaid
gantt
    title Sequential vs Concurrent Execution
    dateFormat X
    axisFormat %L
    
    section Sequential
    Fetch Price (100ms)   :0, 100
    Fetch Inventory (200ms) :100, 300
    
    section Concurrent
    Fetch Price (100ms)   :0, 100
    Fetch Inventory (200ms) :0, 200
```

### 11.3 Streaming Responses

**Benefits:**
- Lower memory footprint
- Faster time-to-first-byte
- Handle large datasets efficiently

**Streaming CSV Example:**
```python
def generate_csv(rows: int) -> Iterator[bytes]:
    yield b"id,name\n"
    for i in range(1, rows + 1):
        yield f"{i},Item {i}\n".encode("utf-8")

return StreamingResponse(
    generate_csv(10000),
    media_type="text/csv"
)
```

### 11.4 Thread Pool Execution

**CPU-Bound Operations:**
```python
from fastapi.concurrency import run_in_threadpool

@router.get("/compute")
async def compute(n: int):
    # Run CPU-heavy task in thread pool
    result = await run_in_threadpool(cpu_heavy, n)
    return {"fib": result}
```

**Why Thread Pool?**
- Prevents blocking the async event loop
- Maintains application responsiveness
- Utilizes multiple CPU cores

---

## 12. Deployment Guide

### 12.1 Production Checklist

```mermaid
graph TB
    Start([Deployment Start]) --> A[Environment Variables]
    A --> B[Database Migration]
    B --> C[Redis Setup]
    C --> D[SSL/TLS Certificates]
    D --> E[Process Manager]
    E --> F[Reverse Proxy]
    F --> G[Monitoring]
    G --> End([Production Ready])
    
    style Start fill:#c8e6c9
    style End fill:#81c784
```

### 12.2 Environment Variables

```bash
# .env file
APP_NAME=FastAPI Production
DEBUG=false
SECRET_KEY=your-super-secure-random-secret-key
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/proddb
REDIS_URL=redis://localhost:6379/0
ALLOWED_ORIGINS=https://yourdomain.com,https://app.yourdomain.com
```

### 12.3 Running with Uvicorn

**Development:**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Production:**
```bash
uvicorn app.main:app \
  --host 0.0.0.0 \
  --port 8000 \
  --workers 4 \
  --loop uvloop \
  --log-level info
```

**Using Gunicorn (Recommended):**
```bash
gunicorn app.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --timeout 120
```

### 12.4 Database Migrations

**Using Alembic:**
```bash
# Initialize
alembic init alembic

# Create migration
alembic revision --autogenerate -m "Initial schema"

# Apply migration
alembic upgrade head
```

### 12.5 Docker Deployment

**Dockerfile:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Docker Compose:**
```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/appdb
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis

  db:
    image: postgres:15
    environment:
      POSTGRES_DB: appdb
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

volumes:
  postgres_data:
```

### 12.6 Reverse Proxy (Nginx)

```nginx
upstream fastapi_backend {
    server localhost:8000;
}

server {
    listen 80;
    server_name api.yourdomain.com;

    location / {
        proxy_pass http://fastapi_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # WebSocket support
    location /api/v2/ws/ {
        proxy_pass http://fastapi_backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

### 12.7 Monitoring & Logging

**Structured Logging:**
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)
logger.info("Application started")
```

**Health Check Endpoint:**
```python
@router.get("/health")
def health_check():
    return {
        "status": "healthy",
        "version": "0.2.0",
        "timestamp": datetime.now().isoformat()
    }
```

### 12.8 Security Best Practices

1. **Use HTTPS in production**
2. **Rotate SECRET_KEY regularly**
3. **Implement rate limiting on all public endpoints**
4. **Validate and sanitize all inputs**
5. **Use environment variables for secrets**
6. **Enable CORS only for trusted origins**
7. **Implement request size limits**
8. **Regular security audits**

---

## API Testing Guide

### Using cURL

**Get Token:**
```bash
curl -X POST http://localhost:8000/api/v1/auth/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=testuser&password=testpass123"
```

**Create Item (Authenticated):**
```bash
curl -X POST http://localhost:8000/api/v2/store/items \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Laptop",
    "description": "Gaming laptop",
    "price": 1299.99,
    "tags": ["electronics", "gaming"],
    "in_stock": true
  }'
```

**WebSocket Test:**
```bash
# Using websocat
websocat ws://localhost:8000/api/v2/ws/echo
# Type messages and see echoed responses
```

---

## Performance Optimization Tips

### 1. Database Query Optimization
```python
# Use select() with specific columns
stmt = select(Items.id, Items.name).where(Items.in_stock == True)

# Use indexes on frequently queried columns
username: Mapped[str] = mapped_column(String(50), index=True)
```

### 2. Caching Strategy
```python
# Cache GET endpoints with appropriate TTL
@cache(expire=300)  # 5 minutes for relatively static data

# Invalidate cache on write operations
await FastAPICache.clear()  # or clear specific namespace
```

### 3. Connection Pooling
```python
engine = create_async_engine(
    url,
    pool_size=10,        # Increase for high traffic
    max_overflow=20,     # Allow burst capacity
    pool_pre_ping=True   # Verify connections before use
)
```

### 4. Async All The Way
```python
# Always use async versions
import aiofiles  # For file I/O
import httpx     # For HTTP requests
```

---

## Troubleshooting

### Common Issues

**1. Redis Connection Failed**
```bash
# Check Redis is running
redis-cli ping

# Start Redis
redis-server

# Check logs
tail -f /var/log/redis/redis-server.log
```

**2. Database Migration Issues**
```bash
# Reset migrations (dev only!)
alembic downgrade base
alembic upgrade head
```

**3. Rate Limit Not Working**
- Ensure Redis is running
- Check `init_rate_limiter()` is called in lifespan
- Verify Redis URL in settings

**4. CORS Errors**
- Add frontend origin to `allowed_origins` in config
- Check middleware setup in `main.py`

---

## Appendix: Data Flow Summary

```mermaid
flowchart TB
    subgraph Client
        A[Browser/Mobile App]
    end
    
    subgraph "API Gateway"
        B[Nginx Reverse Proxy]
    end
    
    subgraph "FastAPI Application"
        C[Middleware Stack]
        D[Authentication Layer]
        E[Rate Limiter]
        F[Route Handlers]
        G[Business Logic]
        H[Repository Layer]
    end
    
    subgraph "Data Layer"
        I[(PostgreSQL/SQLite)]
        J[(Redis Cache)]
    end
    
    subgraph "External Services"
        K[File Storage]
        L[Metrics/Logging]
    end
    
    A <-->|HTTP/WS| B
    B <-->|Proxy| C
    C --> D
    D --> E
    E --> F
    F --> G
    G --> H
    H <-->|SQL| I
    H <-->|Cache| J
    F -.->|Background| K
    F -.->|Logs| L
    
    style A fill:#e3f2fd
    style I fill:#fff9c4
    style J fill:#ffcdd2
    style F fill:#e8f5e9
```

---

## Conclusion

This FastAPI project demonstrates a **production-ready architecture** with:

✅ **Scalability** - Async operations, caching, connection pooling  
✅ **Security** - JWT authentication, scope-based authorization, rate limiting  
✅ **Maintainability** - Modular design, repository pattern, dependency injection  
✅ **Performance** - Redis caching, streaming responses, concurrent I/O  
✅ **Developer Experience** - Type hints, auto-generated docs, clear error messages  

**Access Interactive API Documentation:**
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

---

**Document Version:** 1.0  
**Last Updated:** October 14, 2025  
**Maintained by:** Development Team
