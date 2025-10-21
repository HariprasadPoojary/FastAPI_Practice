import datetime
from typing import TYPE_CHECKING

from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from passlib.context import CryptContext

from app.models.user import UserInDB

if TYPE_CHECKING:
    from app.core.repositories import SQLUserRepo

# Constants (store in secure config for production).
SECRET_KEY = "your-super-secret-key-that-is-long-and-random"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing context (bcrypt).
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme with scopes the app understands.
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/token",
    scopes={
        "items:read": "Read items.",
        "items:write": "Create/update items.",
    },
)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plaintext password against the hashed version."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a plaintext password."""
    return pwd_context.hash(password)


def create_access_token(
    data: dict, expires_minutes: int = ACCESS_TOKEN_EXPIRE_MINUTES
) -> str:
    """Create a JWT access token.
    data(dict): should include 'sub' (username) and optionally 'scopes' (list of scopes).
    expires_minutes(int): token expiry in minutes (default 5 mins).

    returns: str: encoded JWT token.
    """
    to_encode = data.copy()
    expire = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(
        minutes=expires_minutes
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


async def authenticate_user(
    repo: "SQLUserRepo", username: str, password: str
) -> UserInDB | None:
    user = await repo.get_by_username(username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user
