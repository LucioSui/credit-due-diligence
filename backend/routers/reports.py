"""报告生成路由."""

from __future__ import annotations

import logging
from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from auth.dependencies import require_approver
from database import get_db
from schemas.report import GenerateReportRequest, ReportAPIResponse, ReportSnapshot
from services.report_service import ReportService

logger = logging.getLogger(__name__)

router = APIRouter()
report_service = ReportService()


def _success(data: Any, message: str = "success") -> dict:
    return {"code": 0, "message": message, "data": data}


# ---------------------------------------------------------------------------
# 生成报告
# ---------------------------------------------------------------------------

@router.post("/reports", response_model=None)
async def generate_report(
    req: GenerateReportRequest,
    current_user=Depends(require_approver),
    db: AsyncSession = Depends(get_db),
):
    """根据任务生成尽调报告."""
    try:
        result = await report_service.generate_report(
            db=db,
            task_id=str(req.task_id),
            report_version=req.report_version,
        )
        return _success(ReportSnapshot(**result).model_dump(mode="json"), message="报告生成成功")
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        logger.exception("生成报告失败: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))


# ---------------------------------------------------------------------------
# 报告列表
# ---------------------------------------------------------------------------

@router.get("/reports", response_model=None)
async def list_reports(
    task_id: str | None = Query(None),
    current_user=Depends(require_approver),
    db: AsyncSession = Depends(get_db),
):
    """获取报告列表."""
    try:
        reports = await report_service.list_reports(db, task_id=task_id)
        return _success(reports)
    except Exception as exc:
        logger.exception("获取报告列表失败: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))


# ---------------------------------------------------------------------------
# 报告详情
# ---------------------------------------------------------------------------

@router.get("/reports/{report_id}", response_model=None)
async def get_report(
    report_id: UUID,
    current_user=Depends(require_approver),
    db: AsyncSession = Depends(get_db),
):
    """获取报告详情."""
    try:
        report = await report_service.get_report(db, str(report_id))
        return _success(ReportSnapshot(**report).model_dump(mode="json"))
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        logger.exception("获取报告详情失败: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))
