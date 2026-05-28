"""尽调任务 Pydantic 模型"""
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class TaskStatus(str, Enum):
    pending = "pending"
    running = "running"
    completed = "completed"
    failed = "failed"


# ── 请求 ──────────────────────────────────────────────


class CreateTaskRequest(BaseModel):
    company_name: str = Field(..., min_length=1, max_length=200)
    unified_social_credit_code: Optional[str] = Field(None, max_length=18)
    remark: Optional[str] = None


class UpdateTaskRequest(BaseModel):
    company_name: Optional[str] = Field(None, max_length=200)
    unified_social_credit_code: Optional[str] = Field(None, max_length=18)
    status: Optional[TaskStatus] = None


# ── 响应 ──────────────────────────────────────────────


class TaskResponse(BaseModel):
    id: str
    task_no: str
    company_name: str
    unified_social_credit_code: Optional[str] = None
    status: TaskStatus
    progress: float
    created_by: str
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None


class TaskSummary(BaseModel):
    id: str
    task_no: str
    company_name: str
    status: TaskStatus
    progress: float
    created_at: datetime


# ── 扫描步骤（前端展示用）─────────────────────────────


class ScanStep(BaseModel):
    step: str
    label: str
    done: bool
    progress_pct: float


class ScanProgressResponse(BaseModel):
    task_id: str
    status: TaskStatus
    progress: float
    steps: list[ScanStep]


# ── 统一响应包装 ──────────────────────────────────────


class TaskAPIResponse(BaseModel):
    code: int = 0
    message: str = "success"
    data: TaskResponse


class TaskListData(BaseModel):
    items: list[TaskSummary]
    total: int
    page: int
    page_size: int


class TaskListAPIResponse(BaseModel):
    code: int = 0
    message: str = "success"
    data: TaskListData
