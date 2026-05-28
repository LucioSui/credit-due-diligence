"""报告生成 Pydantic 模型"""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


# ── 请求 ──────────────────────────────────────────────


class GenerateReportRequest(BaseModel):
    task_id: str = Field(..., description="尽调任务ID")
    report_version: str = Field("v1", max_length=20, description="报告版本号")


# ── 响应 ──────────────────────────────────────────────


class ReportSnapshot(BaseModel):
    report_id: str
    task_id: str
    company_name: str
    report_version: str
    report_content: str  # Markdown 全文
    pdf_url: Optional[str] = None
    generated_at: datetime


class ReportSummary(BaseModel):
    report_id: str
    task_id: str
    company_name: str
    report_version: str
    generated_at: datetime


# ── 统一响应包装 ──────────────────────────────────────


class ReportAPIResponse(BaseModel):
    code: int = 0
    message: str = "success"
    data: ReportSnapshot


class ReportListAPIResponse(BaseModel):
    code: int = 0
    message: str = "success"
    data: list[ReportSummary]
