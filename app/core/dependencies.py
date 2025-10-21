from typing import Annotated

from fastapi import Depends, Header, HTTPException, Path, Query, status
from fastapi.security import SecurityScopes
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings, get_settings

# from app.db.db import ITEM_DB, USER_DB, ItemDB, UserDB
from app.core.repositories import SQLItemRepo, SQLUserRepo
from app.core.security import ALGORITHM, SECRET_KEY, oauth2_scheme
from app.db.sql import get_session
from app.models.common import Pagination
from app.models.item import ItemRead
from app.models.user import UserRead

# def get_item_repo() -> ItemDB:
#     """Dependency that provides the item repository."""
#     return ITEM_DB


def get_item_repo(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> SQLItemRepo:
    return SQLItemRepo(session)


# def get_user_repo() -> UserDB:
#     """Dependency that provides the user repository."""
#     return USER_DB


def get_user_repo(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> SQLUserRepo:
    return SQLUserRepo(session)


def get_request_id(
    x_request_id: Annotated[
        str | None, Header(description="Optional request correlation ID.")
    ] = None,
) -> str | None:
    return x_request_id


def get_pagination(
    settings: Annotated[Settings, Depends(get_settings)],
    page: Annotated[int, Query(ge=1, description="Page number.")] = 1,
    page_size: Annotated[
        int | None, Query(ge=1, le=100, description="Page size.")
    ] = None,
) -> Pagination:
    chosen_size = page_size if page_size is not None else 10
    chosen_size = min(chosen_size, settings.max_page_size)
    return Pagination(page=page, page_size=chosen_size)


async def get_item_or_404(
    item_id: Annotated[int, Path(gt=0)],
    repo: Annotated[SQLItemRepo, Depends(get_item_repo)],
) -> ItemRead:
    item = await repo.get(item_id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Item not found."
        )
    return item


async def get_current_user(
    security_scopes: SecurityScopes,
    token: Annotated[str, Depends(oauth2_scheme)],
    repo: Annotated[SQLUserRepo, Depends(get_user_repo)],
) -> UserRead:
    """
    This security function is useful and commonly needed; you can keep it for auth-only endpoints or unify authorization by letting it enforce scopes too.

    Auth-only endpoint: Security(get_current_user) without scopes.
    Authorized endpoint: Security(get_current_user, scopes=[...]).

    401 if credentials invalid; 403 if scopes insufficient.
    """
    unauthorized_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    forbidden_exception = HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Insufficient scopes.",
        headers={
            "WWW-Authenticate": f'Bearer scope="{ " ".join(security_scopes.scopes) }"'
        },
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str | None = payload.get("sub")
        token_scopes: list[str] = payload.get("scopes") or []
        if username is None:
            print("Username not found in token payload")
            raise unauthorized_exception
    except JWTError as e:
        print("JWTError occurred:", e)
        raise unauthorized_exception

    # Enforce scopes only if requested by the endpoint.
    if security_scopes.scopes and not all(
        scope in token_scopes for scope in security_scopes.scopes
    ):
        print("Token scopes insufficient:", token_scopes)
        print("Required scopes:", security_scopes.scopes)
        raise forbidden_exception

    user_in_db = await repo.get_by_username(username)
    if not user_in_db or not user_in_db.is_active:
        print("User not found or inactive")
        raise unauthorized_exception
    return repo._to_in_db(user_in_db)
