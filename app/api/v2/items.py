import asyncio
from typing import Annotated

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Body,
    Depends,
    HTTPException,
    Query,
    Security,
    status,
)
from fastapi_cache import FastAPICache
from fastapi_cache.decorator import cache

from app.core.dependencies import (
    get_current_user,
    get_item_or_404,
    get_item_repo,
    get_pagination,
    get_request_id,
)
from app.core.rate_limit import limit_ip, limit_user
from app.core.repositories import SQLItemRepo
from app.models.common import Pagination
from app.models.item import ItemCreate, ItemRead, ItemSummary, ItemUpdate

router = APIRouter(prefix="/store/items")


# Helpers simulating async I/O.
async def fetch_price(item_id: int) -> float:
    await asyncio.sleep(0.1)
    return 100.0 + float(item_id)


async def fetch_inventory(item_id: int) -> int:
    await asyncio.sleep(0.2)
    return 10 + (item_id % 5)


def log_no_of_items_paged(paged_items: int) -> None:
    # Replace with real logging or queue in production.
    print(f"[log] paged items count={paged_items}")


# Keep 'paged' before '{item_id}' to avoid route collisions.
@router.get(
    "/paged",
    response_model=list[ItemRead],
    summary="List items (paged, v2).",
    dependencies=[Depends(limit_ip(times=3, seconds=60))],
)
@cache(expire=60)  # Cache for 60 seconds.
async def list_items_paged(
    pagination: Annotated[Pagination, Depends(get_pagination)],
    repo: Annotated[SQLItemRepo, Depends(get_item_repo)],
    current_user: Annotated[
        object, Security(get_current_user, scopes=["items:write", "items:read"])
    ],
    background_tasks: BackgroundTasks,
    request_id: Annotated[str | None, Depends(get_request_id)] = None,
) -> list[ItemRead]:
    items = await repo.list(limit=pagination.page_size)
    start = (pagination.page - 1) * pagination.page_size
    end = start + pagination.page_size
    # You might log the request_id for traceability.
    background_tasks.add_task(log_no_of_items_paged, end - start)
    return items[start:end]


@router.post(
    "",
    response_model=ItemRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create item (v2).",
)
async def create_item(
    payload: Annotated[ItemCreate, Body(description="Item data to create.")],
    repo: Annotated[SQLItemRepo, Depends(get_item_repo)],
    current_user: Annotated[object, Security(get_current_user, scopes=["items:write"])],
) -> ItemRead:
    item = await repo.create(payload)
    # Clear all cached responses (coarse-grained but simple).
    # * When data changes (create/update), clear related caches. The simplest approach is to clear all cached entries in the project namespace after a write.
    await FastAPICache.clear()
    return item


@router.post(
    "/bulk",
    response_model=list[ItemRead],
    status_code=status.HTTP_201_CREATED,
    summary="Create multiple items (v2).",
)
async def create_items_bulk(
    payloads: Annotated[list[ItemCreate], Body(description="List of item data to create.")],
    repo: Annotated[SQLItemRepo, Depends(get_item_repo)],
) -> list[ItemRead]:
    created_items = []
    for payload in payloads:
        created_item = await repo.create(payload)
        created_items.append(created_item)
    return created_items


@router.get(
    "",
    response_model=list[ItemRead],
    summary="List items (v2).",
    dependencies=[Depends(limit_ip(times=3, seconds=60))],
)
@cache(expire=60)  # Cache for 60 seconds.
async def list_items(
    repo: Annotated[SQLItemRepo, Depends(get_item_repo)],
    q: Annotated[
        str | None,
        Query(min_length=1, max_length=50, description="Filter by name substring."),
    ] = None,
    limit: Annotated[int, Query(ge=1, le=100, description="Max items to return.")] = 25,
) -> list[ItemRead]:
    items = await repo.list()
    if q:
        items = [i for i in items if q.lower() in i.name.lower()]
    return items[:limit]


@router.get(
    "/{item_id}",
    response_model=ItemRead,
    summary="Get item by ID (v2).",
    dependencies=[Depends(limit_ip(times=3, seconds=60))],
)
def read_item(item: Annotated[ItemRead, Depends(get_item_or_404)]) -> ItemRead:
    return item


@router.patch("/{item_id}", response_model=ItemRead, summary="Update item (v2).")
async def update_item(
    item: Annotated[ItemRead, Depends(get_item_or_404)],
    changes: Annotated[ItemUpdate, Body(description="Fields to update.")],
    repo: Annotated[SQLItemRepo, Depends(get_item_repo)],
) -> ItemRead:
    updated = await repo.update(item.id, changes)
    if not updated:
        # Should not happen due to loader, but safe guard.
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found.")
    # Clear all cached responses (coarse-grained but simple).
    # * When data changes (create/update), clear related caches. The simplest approach is to clear all cached entries in the project namespace after a write.
    await FastAPICache.clear()
    return updated


@router.get(
    "/{item_id}/summary",
    response_model=ItemSummary,
    summary="Async summary (concurrent I/O, v2).",
)
async def get_item_summary(
    item: Annotated[ItemRead, Depends(get_item_or_404)],
) -> ItemSummary:
    price, inventory = await asyncio.gather(fetch_price(item.id), fetch_inventory(item.id))
    return ItemSummary(item=item, price=price, inventory=inventory)


def log_purchase(item_id: int, amount: int) -> None:
    # Replace with real audit logging or queue in production.
    print(f"[audit] purchase item={item_id} amount={amount}")


@router.post("/{item_id}/purchase", summary="Queue an audit log via BackgroundTasks (v2).")
async def purchase_item(
    item: Annotated[ItemRead, Depends(get_item_or_404)],
    amount: Annotated[int, Body(ge=1, description="Units to purchase.")],
    background_tasks: BackgroundTasks,
) -> dict[str, str]:
    # Background tasks run after sending the response, improving client-perceived performance.
    background_tasks.add_task(log_purchase, item.id, amount)
    return {"status": "queued"}


"""
Advanced invalidation:

If you need fine-grained invalidation, you can build keys yourself and call FastAPICache.get_backend().clear(key).
Start with coarse invalidation until you profile hot paths.
"""
