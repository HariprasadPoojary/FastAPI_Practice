from typing import Annotated

from fastapi import APIRouter, Body, Depends, HTTPException, Path, Query, status

from app.core.dependencies import get_item_repo, get_pagination
from app.core.repositories import SQLItemRepo
from app.models.common import Pagination
from app.models.item import ItemCreate, ItemRead, ItemUpdate

router = APIRouter(prefix="/store/items")

# Declare literal 'paged' before dynamic '{item_id}' to avoid route collisions.


@router.get("/paged", response_model=list[ItemRead], summary="List items (paged, v1).")
async def list_items_paged(
    pagination: Annotated[Pagination, Depends(get_pagination)],
    repo: Annotated[SQLItemRepo, Depends(get_item_repo)],
) -> list[ItemRead]:
    items = await repo.list()
    start = (pagination.page - 1) * pagination.page_size
    end = start + pagination.page_size
    return items[start:end]


@router.post(
    "",
    response_model=ItemRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create item (v1).",
)
async def create_item(
    payload: Annotated[ItemCreate, Body(description="Item data to create.")],
    repo: Annotated[SQLItemRepo, Depends(get_item_repo)],
) -> ItemRead:
    return await repo.create(payload)


@router.get("", response_model=list[ItemRead], summary="List items (v1).")
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


@router.get("/{item_id}", response_model=ItemRead, summary="Get item by ID (v1).")
async def read_item(
    item_id: Annotated[int, Path(gt=0)],
    repo: Annotated[SQLItemRepo, Depends(get_item_repo)],
) -> ItemRead:
    item = await repo.get(item_id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Item not found."
        )
    return item


@router.patch("/{item_id}", response_model=ItemRead, summary="Update item (v1).")
async def update_item(
    item_id: Annotated[int, Path(gt=0)],
    changes: Annotated[ItemUpdate, Body(description="Fields to update.")],
    repo: Annotated[SQLItemRepo, Depends(get_item_repo)],
) -> ItemRead:
    updated = await repo.update(item_id, changes)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Item not found."
        )
    return updated
