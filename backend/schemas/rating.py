"""评级引擎 Pydantic 模型"""
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class Grade(str, Enum):
    A = "A"
    B = "B"
    C = "C"
    D = "D"


# ── 请求 ──────────────────────────────────────────────


class RatingRequest(BaseModel):
    """手动触发评级的请求"""

    task_id: Optional[str] = None  # 关联尽调任务，None 表示独立评级
    company_id: str = Field(..., description="企业UUID")
    reason: str = Field("手动评级", max_length=200, description="评级原因")


class ScanTaskRequest(BaseModel):
    """创建尽调任务并启动扫描"""

    company_name: str = Field(..., min_length=1, max_length=200, description="企业名称")
    unified_credit_code: Optional[str] = Field(None, max_length=18, description="统一社会信用代码")


# ── 响应 ──────────────────────────────────────────────


class DimensionScore(BaseModel):
    """单维度评分"""

    dimension: str = Field(..., description="维度名称")
    score: float = Field(..., ge=0, le=100, description="得分 (0-100)")
    weight: float = Field(..., description="权重 (%)")
    weighted_score: float = Field(..., description="加权得分")
    factors: list[dict] = Field(default_factory=list, description="扣分/加分明细")


class RatingResponse(BaseModel):
    """评级结果"""

    rating_id: str
    task_id: Optional[str] = None
    company_id: str
    company_name: str
    judicial_score: float
    financial_score: float
    credit_score: float
    operation_score: float
    equity_score: float
    compliance_score: float
    final_score: float
    grade: Grade
    dimension_scores: list[DimensionScore]
    rating_reason: str
    generated_at: datetime


class RatingSummary(BaseModel):
    """评级摘要（列表用）"""

    rating_id: str
    company_name: str
    final_score: float
    grade: Grade
    generated_at: datetime


# ── 统一响应包装 ──────────────────────────────────────


class RatingAPIResponse(BaseModel):
    code: int = 0
    message: str = "success"
    data: RatingResponse


class RatingListAPIResponse(BaseModel):
    code: int = 0
    message: str = "success"
    data: list[RatingSummary]
