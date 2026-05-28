"""尽调任务管理路由."""

from __future__ import annotations

import logging
from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from auth.dependencies import get_current_user, require_approver
from database import get_db
from models.task import TaskStatus
from schemas.task import CreateTaskRequest, ScanProgressResponse, TaskListAPIResponse, TaskResponse, UpdateTaskRequest
from services.task_service import TaskService

logger = logging.getLogger(__name__)

router = APIRouter()
task_service = TaskService()


def _success(data: Any, message: str = "success") -> dict:
    return {"code": 0, "message": message, "data": data}


# ---------------------------------------------------------------------------
# 创建任务
# ---------------------------------------------------------------------------

@router.post("/tasks", response_model=None)
async def create_task(
    req: CreateTaskRequest,
    current_user=Depends(require_approver),
    db: AsyncSession = Depends(get_db),
):
    """创建尽调任务."""
    try:
        task = await task_service.create_task(
            db=db,
            company_name=req.company_name,
            unified_social_credit_code=req.unified_social_credit_code,
            creator_id=str(current_user.id),
            remark=getattr(req, 'remark', None),
        )
        return _success(TaskResponse(**task).model_dump(mode="json"))
    except Exception as exc:
        logger.exception("创建任务失败: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))


# ---------------------------------------------------------------------------
# 任务列表
# ---------------------------------------------------------------------------

@router.get("/tasks", response_model=None)
async def list_tasks(
    status: TaskStatus | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user=Depends(require_approver),
    db: AsyncSession = Depends(get_db),
):
    """获取任务列表."""
    try:
        result = await task_service.list_tasks(
            db=db,
            status=status,
            creator_id=str(current_user.id) if current_user else None,
            page=page,
            page_size=page_size,
        )
        return _success(result)
    except Exception as exc:
        logger.exception("获取任务列表失败: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))


# ---------------------------------------------------------------------------
# 获取任务详情
# ---------------------------------------------------------------------------

@router.get("/tasks/{task_id}", response_model=None)
async def get_task(
    task_id: UUID,
    current_user=Depends(require_approver),
    db: AsyncSession = Depends(get_db),
):
    """获取单个任务详情."""
    try:
        task = await task_service.get_task(db, str(task_id))
        return _success(TaskResponse(**task).model_dump(mode="json"))
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        logger.exception("获取任务详情失败: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))


# ---------------------------------------------------------------------------
# 启动扫描
# ---------------------------------------------------------------------------

@router.post("/tasks/{task_id}/scan", response_model=None)
async def start_scan(
    task_id: UUID,
    current_user=Depends(require_approver),
    db: AsyncSession = Depends(get_db),
):
    """启动尽调扫描."""
    try:
        task = await task_service.start_scan(db, str(task_id))
        return _success(TaskResponse(**task).model_dump(mode="json"), message="扫描已启动")
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        logger.exception("启动扫描失败: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))


# ---------------------------------------------------------------------------
# 扫描进度
# ---------------------------------------------------------------------------

@router.get("/tasks/{task_id}/progress", response_model=None)
async def get_scan_progress(
    task_id: UUID,
    current_user=Depends(require_approver),
    db: AsyncSession = Depends(get_db),
):
    """获取扫描进度."""
    try:
        progress = await task_service.get_scan_progress(db, str(task_id))
        return _success(ScanProgressResponse(**progress).model_dump(mode="json"))
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        logger.exception("获取扫描进度失败: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))


# ---------------------------------------------------------------------------
# 取消任务
# ---------------------------------------------------------------------------

@router.post("/tasks/{task_id}/cancel", response_model=None)
async def cancel_task(
    task_id: UUID,
    current_user=Depends(require_approver),
    db: AsyncSession = Depends(get_db),
):
    """取消尽调任务."""
    try:
        task = await task_service.get_task(db, str(task_id))
        if task["status"] not in ("pending", "running"):
            raise HTTPException(status_code=400, detail="仅能取消待处理或扫描中的任务")
        await task_service.update_progress(
            db, str(task_id), progress=task["progress"], status=TaskStatus.FAILED
        )
        return _success(message="任务已取消")
    except HTTPException:
        raise
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        logger.exception("取消任务失败: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))


# ---------------------------------------------------------------------------
# 重试任务
# ---------------------------------------------------------------------------

@router.post("/tasks/{task_id}/retry", response_model=None)
async def retry_task(
    task_id: UUID,
    current_user=Depends(require_approver),
    db: AsyncSession = Depends(get_db),
):
    """重试失败的尽调任务."""
    try:
        task = await task_service.get_task(db, str(task_id))
        if task["status"] != "failed":
            raise HTTPException(status_code=400, detail="仅能重试失败的任务")
        await task_service.update_progress(
            db, str(task_id), progress=0.0, status=TaskStatus.PENDING
        )
        return _success(message="任务已重置，可重新启动扫描")
    except HTTPException:
        raise
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        logger.exception("重试任务失败: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))
