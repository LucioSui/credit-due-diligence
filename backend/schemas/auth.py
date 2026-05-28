"""Authentication request/response schemas."""

from pydantic import BaseModel

from models.user import UserRole


class LoginRequest(BaseModel):
    """Login request payload."""

    username: str
    password: str


class TokenResponse(BaseModel):
    """Token response after login or refresh."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    """User info returned to the client."""

    id: str
    username: str
    email: str
    role: UserRole
    real_name: str | None = None
    is_active: bool

    model_config = {"from_attributes": True}


class RefreshRequest(BaseModel):
    """Refresh token request payload."""

    refresh_token: str
