from pydantic import BaseModel, Field


class Pagination(BaseModel):
    page: int = Field(ge=1, default=1)
    page_size: int = Field(ge=1, le=100, default=10)
