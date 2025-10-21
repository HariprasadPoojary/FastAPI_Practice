from datetime import datetime

from pydantic import BaseModel, Field


class ItemBase(BaseModel):
    name: str = Field(
        min_length=2, max_length=50, description="Human-friendly item name."
    )
    description: str | None = Field(
        default=None, max_length=500, description="Optional details."
    )
    price: float = Field(ge=0, description="Unit price; must be non-negative.")
    tags: list[str] = Field(
        default_factory=list, description="Tags associated with the item."
    )
    in_stock: bool = Field(
        default=True, description="Whether the item is currently in stock."
    )


class ItemCreate(ItemBase):
    pass


class ItemRead(ItemBase):
    id: int
    created_at: datetime


class ItemUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=50)
    description: str | None = Field(default=None, max_length=500)
    price: float | None = Field(default=None, ge=0)
    tags: list[str] | None = None
    in_stock: bool | None = None


class ItemSummary(BaseModel):
    item: ItemRead
    price: float
    inventory: int
