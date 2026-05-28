"""Authentication router — login, refresh, logout, me."""

import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from models.user import User

from .dependencies import get_current_user
from .utils import (
    create_access_token,
    create_refresh_token,
    decode_token,
    verify_password,
)
from schemas.auth import LoginRequest, RefreshRequest, TokenResponse, UserResponse

router = APIRouter(prefix="/api/auth", tags=["auth"])

# --- Error constants ---
ERROR_UNAUTHORIZED = 1001


def _api_response(data=None, message: str = "success", code: int = 0):
    """Uniform API response envelope."""
    return {"code": code, "message": message, "data": data}


def _user_to_response(user: User) -> dict:
    """Convert a User model to a response dict."""
    return UserResponse(
        id=str(user.id),
        username=user.username,
        email=user.email,
        role=user.role,
        real_name=user.real_name,
        is_active=user.is_active,
    ).model_dump()


# --- Endpoints -----------------------------------------------------------


@router.post("/login")
async def login(payload: LoginRequest, db: AsyncSession = Depends(get_db)):
    """Authenticate user and return access + refresh tokens."""
    try:
        result = await db.execute(
            select(User).where(User.username == payload.username)
        )
        user = result.scalar_one_or_none()

        if user is None or not verify_password(payload.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=_api_response(
                    code=ERROR_UNAUTHORIZED,
                    message="用户名或密码错误",
                ),
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=_api_response(
                    code=ERROR_UNAUTHORIZED,
                    message="账号已被禁用",
                ),
            )

        token_data = {"sub": str(user.id), "username": user.username}
        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token(token_data)

        return _api_response(
            data={
                **TokenResponse(
                    access_token=access_token,
                    refresh_token=refresh_token,
                ).model_dump(),
                "user": _user_to_response(user),
            },
            message="登录成功",
        )
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=_api_response(code=5000, message=f"内部错误: {exc}"),
        )


@router.post("/refresh")
async def refresh(payload: RefreshRequest):
    """Use a refresh token to obtain a new access token."""
    try:
        payload_decoded = decode_token(payload.refresh_token)
        token_type = payload_decoded.get("type")
        if token_type != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=_api_response(
                    code=ERROR_UNAUTHORIZED, message="无效的刷新令牌"
                ),
            )

        user_id = payload_decoded.get("sub")
        username = payload_decoded.get("username")
        token_data = {"sub": user_id, "username": username}
        new_access = create_access_token(token_data)
        new_refresh = create_refresh_token(token_data)

        return _api_response(
            data=TokenResponse(
                access_token=new_access, refresh_token=new_refresh
            ).model_dump(),
            message="刷新成功",
        )
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=_api_response(
                code=ERROR_UNAUTHORIZED, message=f"令牌无效: {exc}"
            ),
        )


@router.post("/logout")
async def logout(current_user: User = Depends(get_current_user)):
    """Logout — JWT is stateless; just return 200 for now."""
    return _api_response(message="退出成功")


@router.get("/me")
async def me(current_user: User = Depends(get_current_user)):
    """Return current authenticated user info."""
    return _api_response(data=_user_to_response(current_user))
