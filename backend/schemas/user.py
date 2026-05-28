"""User management request/response schemas."""

from pydantic import BaseModel

from models.user import UserRole

from .auth import UserResponse


class UserCreate(BaseModel):
    """Create a new user."""

    username: str
    email: str
    password: str
    role: UserRole = UserRole.VIEWER
    real_name: str | None = None


class UserUpdate(BaseModel):
    """Update an existing user — all fields optional."""

    email: str | None = None
    role: UserRole | None = None
    real_name: str | None = None
    is_active: bool | None = None
    password: str | None = None  # optional password change


class UserListResponse(BaseModel):
    """Paginated user list."""

    items: list[UserResponse]
    total: int
    page: int
    page_size: int
