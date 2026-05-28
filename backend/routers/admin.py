"""User management router — admin only."""

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from models.user import User, UserRole

from auth.dependencies import require_admin
from auth.utils import hash_password
from schemas.user import UserCreate, UserUpdate, UserListResponse, UserResponse

router = APIRouter(prefix="/admin", tags=["admin"])

# --- Error constants ---
ERROR_FORBIDDEN = 1002


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


@router.get("/users")
async def list_users(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页条数"),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
):
    """Paginated user list."""
    try:
        # Count total
        count_result = await db.execute(select(func.count(User.id)))
        total = count_result.scalar() or 0

        # Fetch page
        result = await db.execute(
            select(User)
            .order_by(User.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        users = result.scalars().all()

        return _api_response(
            data=UserListResponse(
                items=[_user_to_response(u) for u in users],
                total=total,
                page=page,
                page_size=page_size,
            ).model_dump(),
        )
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=_api_response(code=5000, message=f"内部错误: {exc}"),
        )


@router.post("/users")
async def create_user(
    payload: UserCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
):
    """Create a new user."""
    try:
        # Check uniqueness
        existing = await db.execute(
            select(User).where(
                (User.username == payload.username)
                | (User.email == payload.email)
            )
        )
        if existing.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=_api_response(
                    code=400, message="用户名或邮箱已存在"
                ),
            )

        user = User(
            id=uuid.uuid4(),
            username=payload.username,
            email=payload.email,
            password_hash=hash_password(payload.password),
            role=payload.role,
            real_name=payload.real_name,
            is_active=True,
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)

        return _api_response(
            data=_user_to_response(user), message="用户创建成功"
        )
    except HTTPException:
        raise
    except Exception as exc:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=_api_response(code=5000, message=f"内部错误: {exc}"),
        )


@router.put("/users/{user_id}")
async def update_user(
    user_id: uuid.UUID,
    payload: UserUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
):
    """Update an existing user."""
    try:
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=_api_response(code=404, message="用户不存在"),
            )

        update_data = payload.model_dump(exclude_unset=True)

        # Handle unique constraints for username/email
        if "email" in update_data and update_data["email"] != user.email:
            email_exists = await db.execute(
                select(User).where(
                    User.email == update_data["email"], User.id != user_id
                )
            )
            if email_exists.scalar_one_or_none():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=_api_response(code=400, message="邮箱已被使用"),
                )

        # Hash password if provided
        if "password" in update_data and update_data["password"]:
            update_data["password_hash"] = hash_password(update_data.pop("password"))

        for field, value in update_data.items():
            setattr(user, field, value)

        await db.commit()
        await db.refresh(user)

        return _api_response(
            data=_user_to_response(user), message="用户更新成功"
        )
    except HTTPException:
        raise
    except Exception as exc:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=_api_response(code=5000, message=f"内部错误: {exc}"),
        )


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
):
    """Soft-delete a user (set is_active=False)."""
    try:
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=_api_response(code=404, message="用户不存在"),
            )

        user.is_active = False
        await db.commit()

        return _api_response(message="用户已禁用")
    except HTTPException:
        raise
    except Exception as exc:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=_api_response(code=5000, message=f"内部错误: {exc}"),
        )
