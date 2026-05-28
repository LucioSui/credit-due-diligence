"""Financial report data service (3.5)."""

import logging
from datetime import datetime
from typing import Optional

from fastapi import HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models.financial_report import (
    FileSource,
    ParseStatus,
    ReportType,
    UploadedFinancialReport,
)
from storage.file_storage import FileStorage
from services.file_parser import FileParser

logger = logging.getLogger(__name__)

ERR_FILE_UPLOAD_FAILED = 5001
ERR_FILE_PARSE_FAILED = 5002


class FinancialReportService:
    """Business logic for uploaded financial reports."""

    async def upload_report(
        self,
        db: AsyncSession,
        company_id: str,
        file: UploadFile,
        report_type: ReportType,
        uploaded_by: str,
    ) -> UploadedFinancialReport:
        """Upload a financial report file and create a DB record (parse_status=pending)."""
        content = await file.read()
        file_size = len(content)

        # Validate
        FileStorage.validate_file(file.filename or "unknown", "financial_report", file_size)

        # Determine source from extension
        file_source = FileStorage.get_file_source_from_filename(file.filename or "")
        file_source_enum = FileSource.PDF if file_source == "pdf" else FileSource.EXCEL

        # Save file
        save_path = FileStorage.get_upload_path(company_id, "financial_report", file.filename or "report")
        await FileStorage.save_file(content, save_path)

        # Create DB record
        report = UploadedFinancialReport(
            company_id=company_id,
            report_type=report_type,
            report_period=None,
            file_name=file.filename or "unknown",
            file_path=save_path,
            file_source=file_source_enum,
            parse_status=ParseStatus.PENDING,
            uploaded_by=uploaded_by,
        )
        db.add(report)
        await db.commit()
        await db.refresh(report)
        return report

    async def list_reports(
        self,
        db: AsyncSession,
        company_id: str,
    ) -> list[UploadedFinancialReport]:
        """Return all uploaded reports for a company, ordered by upload date descending."""
        stmt = (
            select(UploadedFinancialReport)
            .where(UploadedFinancialReport.company_id == company_id)
            .order_by(UploadedFinancialReport.uploaded_at.desc())
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def get_report(
        self,
        db: AsyncSession,
        report_id: str,
    ) -> UploadedFinancialReport:
        """Fetch a single report by id."""
        stmt = (
            select(UploadedFinancialReport)
            .where(UploadedFinancialReport.id == report_id)
        )
        result = await db.execute(stmt)
        report = result.scalar_one_or_none()
        if not report:
            raise HTTPException(status_code=404, detail="财报记录不存在")
        return report

    async def parse_report(
        self,
        db: AsyncSession,
        report_id: str,
    ) -> UploadedFinancialReport:
        """Trigger synchronous parsing of a report file (MVP)."""
        report = await self.get_report(db, report_id)
        if report.parse_status == ParseStatus.PARSED:
            return report

        parser = FileParser()
        try:
            file_type = "excel" if report.file_source == FileSource.EXCEL else "pdf"
            parsed = await parser.parse_financial_report(report.file_path, file_type)

            report.total_assets = parsed.get("total_assets")
            report.total_liabilities = parsed.get("total_liabilities")
            report.revenue = parsed.get("revenue")
            report.net_profit = parsed.get("net_profit")
            report.operating_cash_flow = parsed.get("operating_cash_flow")
            report.parsed_data = parsed
            report.parse_status = ParseStatus.PARSED
            report.parse_error = None
            report.parsed_at = datetime.now()
        except Exception as exc:
            logger.exception("Failed to parse financial report %s", report_id)
            report.parse_status = ParseStatus.FAILED
            report.parse_error = str(exc)
            report.parsed_at = None

        await db.commit()
        await db.refresh(report)
        return report

    async def compare_reports(
        self,
        db: AsyncSession,
        report_ids: list[str],
    ) -> dict:
        """Compare multiple reports and return per-indicator cross-period data."""
        reports = []
        for rid in report_ids:
            try:
                r = await self.get_report(db, rid)
                reports.append(r)
            except HTTPException:
                continue

        if not reports:
            return {"reports": [], "comparison": {}}

        indicators = [
            "total_assets",
            "total_liabilities",
            "revenue",
            "net_profit",
            "operating_cash_flow",
        ]

        comparison: dict[str, list[dict]] = {}
        for indicator in indicators:
            series = []
            for r in reports:
                val = getattr(r, indicator, None)
                series.append({
                    "report_id": str(r.id),
                    "report_period": r.report_period or r.file_name,
                    "value": val,
                })
            comparison[indicator] = series

        return {
            "reports": [
                {
                    "id": str(r.id),
                    "file_name": r.file_name,
                    "report_period": r.report_period,
                    "report_type": r.report_type.value,
                }
                for r in reports
            ],
            "comparison": comparison,
        }

    async def delete_report(
        self,
        db: AsyncSession,
        report_id: str,
    ) -> None:
        """Delete a financial report record and its file."""
        report = await self.get_report(db, report_id)
        if report.file_path:
            await FileStorage.delete_file(report.file_path)
        await db.delete(report)
        await db.commit()
