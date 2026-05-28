"""Financial report data routes (3.5).

API paths are mounted under /api/companies/{company_id}.
"""

import logging
import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from models.financial_report import ReportType
from schemas.financial_report import (
    FinancialReportCompareResponse,
    FinancialReportDetail,
    FinancialReportListResponse,
)
from services.financial_report_service import FinancialReportService

logger = logging.getLogger(__name__)

router = APIRouter()

ERR_FILE_UPLOAD_FAILED = 5001
ERR_FILE_PARSE_FAILED = 5002

# ── Placeholder: replaced by real dependency after T02 ──────────────────
CurrentUser = Optional[dict]


def get_current_user_placeholder() -> CurrentUser:
    """Return None for now; will be replaced with real auth dependency."""
    return None


# current_user dependency is referenced inline via Depends(get_current_user_placeholder)


def _api_success(data, message: str = "success") -> dict:
    return {"code": 0, "message": message, "data": data}


def _api_error(code: int, message: str) -> dict:
    return {"code": code, "message": message, "data": None}


@router.post("/financial-reports/upload")
async def upload_report(
    file: UploadFile,
    report_type: ReportType = Query(ReportType.AUDIT),
    company_id: str = Depends(lambda: None),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user_placeholder),
):
    """Upload a financial report file (multipart/form-data)."""
    # company_id comes from the parent router prefix
    # For now we accept it as a query param fallback
    try:
        service = FinancialReportService()
        uploaded_by = str(uuid.uuid4())  # placeholder
        report = await service.upload_report(db, company_id, file, report_type, uploaded_by)
        return _api_success(
            {
                "id": str(report.id),
                "company_id": str(report.company_id),
                "file_name": report.file_name,
                "file_source": report.file_source.value,
                "parse_status": report.parse_status.value,
                "uploaded_at": report.uploaded_at.isoformat(),
            },
            message="财报上传成功",
        )
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("财报上传失败")
        raise HTTPException(status_code=ERR_FILE_UPLOAD_FAILED, detail=f"文件上传失败: {exc}")


@router.get("/financial-reports")
async def list_reports(
    company_id: str = Depends(lambda: None),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user_placeholder),
):
    """List all financial reports for a company."""
    service = FinancialReportService()
    reports = await service.list_reports(db, company_id)
    items = []
    for r in reports:
        items.append(FinancialReportDetail(
            id=str(r.id),
            company_id=str(r.company_id),
            file_name=r.file_name,
            file_source=r.file_source,
            parse_status=r.parse_status,
            uploaded_at=r.uploaded_at,
            report_type=r.report_type,
            report_period=r.report_period,
            total_assets=r.total_assets,
            total_liabilities=r.total_liabilities,
            revenue=r.revenue,
            net_profit=r.net_profit,
            operating_cash_flow=r.operating_cash_flow,
            parsed_data=r.parsed_data,
            parse_error=r.parse_error,
            parsed_at=r.parsed_at,
        ))
    return _api_success(FinancialReportListResponse(items=items, total=len(items)).model_dump())


@router.get("/financial-reports/{report_id}")
async def get_report(
    report_id: str,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user_placeholder),
):
    """Get financial report detail."""
    service = FinancialReportService()
    try:
        report = await service.get_report(db, report_id)
        detail = FinancialReportDetail(
            id=str(report.id),
            company_id=str(report.company_id),
            file_name=report.file_name,
            file_source=report.file_source,
            parse_status=report.parse_status,
            uploaded_at=report.uploaded_at,
            report_type=report.report_type,
            report_period=report.report_period,
            total_assets=report.total_assets,
            total_liabilities=report.total_liabilities,
            revenue=report.revenue,
            net_profit=report.net_profit,
            operating_cash_flow=report.operating_cash_flow,
            parsed_data=report.parsed_data,
            parse_error=report.parse_error,
            parsed_at=report.parsed_at,
        )
        return _api_success(detail.model_dump())
    except HTTPException:
        raise


@router.post("/financial-reports/{report_id}/parse")
async def parse_report(
    report_id: str,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user_placeholder),
):
    """Trigger parsing of a financial report."""
    service = FinancialReportService()
    try:
        report = await service.parse_report(db, report_id)
        return _api_success(
            {
                "id": str(report.id),
                "parse_status": report.parse_status.value,
                "total_assets": report.total_assets,
                "total_liabilities": report.total_liabilities,
                "revenue": report.revenue,
                "net_profit": report.net_profit,
                "operating_cash_flow": report.operating_cash_flow,
                "parse_error": report.parse_error,
                "parsed_at": report.parsed_at.isoformat() if report.parsed_at else None,
            },
            message="解析完成" if report.parse_status.value == "parsed" else "解析失败",
        )
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("财报解析失败")
        raise HTTPException(status_code=ERR_FILE_PARSE_FAILED, detail=f"解析失败: {exc}")


@router.get("/financial-reports/compare")
async def compare_reports(
    ids: str = Query(..., description="逗号分隔的财报ID列表"),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user_placeholder),
):
    """Compare multiple financial reports."""
    report_ids = [rid.strip() for rid in ids.split(",") if rid.strip()]
    if not report_ids:
        raise HTTPException(status_code=400, detail="请提供至少一个财报ID")
    service = FinancialReportService()
    result = await service.compare_reports(db, report_ids)
    return _api_success(result, message="对比完成")


@router.delete("/financial-reports/{report_id}")
async def delete_report(
    report_id: str,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user_placeholder),
):
    """Delete a financial report."""
    service = FinancialReportService()
    try:
        await service.delete_report(db, report_id)
        return _api_success(None, message="删除成功")
    except HTTPException:
        raise
