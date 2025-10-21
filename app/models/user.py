from pydantic import BaseModel, Field


class UserBase(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    full_name: str | None = None
    email: str | None = None
    is_active: bool = True
    scopes: list[str] = Field(
        default_factory=list, description="Authorization scopes, e.g., 'items:read'."
    )


class UserCreate(UserBase):
    password: str = Field(
        min_length=6, description="Plain-text password for signup (hashed at rest)."
    )


class UserRead(UserBase):
    id: int


class UserInDB(UserBase):
    hashed_password: str
