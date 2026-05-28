"""Schemas for uploaded financial reports (财报上传)."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from models.financial_report import FileSource, ParseStatus, ReportType


class FinancialReportUploadResponse(BaseModel):
    id: str
    company_id: str
    file_name: str
    file_source: FileSource
    parse_status: ParseStatus
    uploaded_at: datetime

    class Config:
        from_attributes = True


class FinancialReportDetail(FinancialReportUploadResponse):
    report_type: ReportType
    report_period: Optional[str] = None
    total_assets: Optional[float] = None
    total_liabilities: Optional[float] = None
    revenue: Optional[float] = None
    net_profit: Optional[float] = None
    operating_cash_flow: Optional[float] = None
    parsed_data: Optional[dict] = None
    parse_error: Optional[str] = None
    parsed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class FinancialReportCompareResponse(BaseModel):
    reports: list[FinancialReportDetail]
    comparison: dict  # 多期对比汇总


class FinancialReportListResponse(BaseModel):
    items: list[FinancialReportDetail]
    total: int
