"""FastAPI dependency injection for authentication & authorization."""

from collections.abc import Callable
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from jose import JWTError

from config import settings
from database import get_db
from models.user import User, UserRole

from .utils import decode_token

security = HTTPBearer()

# --- Error constants ---
ERROR_UNAUTHORIZED = 1001
ERROR_FORBIDDEN = 1002


# Demo-mode sentinel token (used by the frontend when the backend is offline)
_DEMO_TOKEN = "demo-token"


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Decode the Bearer token, look up the user, and return it.

    Raises:
        HTTPException(401): Token is missing, malformed, or expired.
    """
    token = credentials.credentials
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail={"code": ERROR_UNAUTHORIZED, "message": "无效的认证凭证"},
    )

    # --- Demo-mode: bypass JWT verification ---
    if token == _DEMO_TOKEN:
        demo_user = User(
            id=UUID("00000000-0000-0000-0000-000000000001"),
            username="demo",
            email="demo@demo.com",
            password_hash="",
            role=UserRole.ADMIN,
            is_active=True,
        )
        return demo_user

    try:
        payload = decode_token(token)
        user_id: str | None = payload.get("sub")
        token_type: str | None = payload.get("type")
        if user_id is None or token_type != "access":
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    result = await db.execute(select(User).where(User.id == UUID(user_id)))
    user = result.scalar_one_or_none()
    if user is None or not user.is_active:
        raise credentials_exception
    return user


def require_role(*roles: UserRole) -> Callable:
    """Return a dependency that enforces the current user has one of the given roles."""

    async def _check_role(
        current_user: User = Depends(get_current_user),
    ) -> User:
        if current_user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={"code": ERROR_FORBIDDEN, "message": "权限不足"},
            )
        return current_user

    return _check_role


# Pre-built role guards
require_admin = require_role(UserRole.ADMIN)
require_approver = require_role(
    UserRole.ADMIN, UserRole.APPROVER, UserRole.SUPERVISOR
)
