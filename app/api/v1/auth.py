from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Security, status
from fastapi.security import OAuth2PasswordRequestForm

from app.core.dependencies import get_current_user, get_user_repo
from app.core.repositories import SQLUserRepo
from app.core.security import authenticate_user, create_access_token, get_password_hash
from app.models.user import UserCreate, UserRead

router = APIRouter(prefix="/auth", tags=["v1: auth"])


@router.post(
    "/signup",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new user.",
)
async def signup(
    payload: UserCreate,
    repo: Annotated[SQLUserRepo, Depends(get_user_repo)],
) -> UserRead:
    try:
        return await repo.create(payload)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists."
        )


@router.post("/token", summary="Obtain an access token (OAuth2 Password flow).")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    repo: Annotated[SQLUserRepo, Depends(get_user_repo)],
):
    user = await authenticate_user(repo, form_data.username, form_data.password)
    if not user:
        print("Authentication failed for user:", form_data.username)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password.",
        )
    # Use provided scopes (space-separated) from the OAuth2 form or fall back to user scopes in DB.
    requested_scopes = form_data.scopes or user.scopes
    access_token = create_access_token(
        {"sub": user.username, "scopes": requested_scopes}
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserRead, summary="Get current user (auth-only).")
def read_me(current_user: Annotated[UserRead, Security(get_current_user)]) -> UserRead:
    return current_user
