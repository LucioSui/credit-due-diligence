"""Bank statement routes (3.6).

API paths are mounted under /api/companies/{company_id}.
"""

import logging
import uuid
from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from schemas.bank_statement import (
    BankStatementDetail,
    BankStatementFetchRequest,
    BankStatementListResponse,
)
from services.bank_statement_service import BankStatementService

logger = logging.getLogger(__name__)

router = APIRouter()

ERR_FILE_UPLOAD_FAILED = 5001


def _api_success(data, message: str = "success") -> dict:
    return {"code": 0, "message": message, "data": data}


@router.post("/bank-statements/fetch")
async def fetch_internal(
    body: BankStatementFetchRequest,
    company_id: str = Depends(lambda: None),
    db: AsyncSession = Depends(get_db),
):
    """Pull bank statement from internal bank system (MVP: simulated data)."""
    service = BankStatementService()
    uploaded_by = str(uuid.uuid4())  # placeholder
    record = await service.fetch_internal(
        db, company_id, body.account_no, body.start_date, body.end_date, uploaded_by
    )
    return _api_success(
        {
            "id": str(record.id),
            "account_no": record.account_no,
            "bank_name": record.bank_name,
            "statement_source": record.statement_source.value,
            "start_date": record.start_date.isoformat() if record.start_date else None,
            "end_date": record.end_date.isoformat() if record.end_date else None,
            "total_inflow": record.total_inflow,
            "total_outflow": record.total_outflow,
            "avg_daily_balance": record.avg_daily_balance,
            "ending_balance": record.ending_balance,
            "transaction_count": record.transaction_count,
            "transaction_summary": record.transaction_summary,
            "anomaly_flags": record.anomaly_flags,
            "parse_status": record.parse_status.value,
        },
        message="流水拉取成功",
    )


@router.post("/bank-statements/upload")
async def upload_statement(
    file: UploadFile,
    company_id: str = Depends(lambda: None),
    db: AsyncSession = Depends(get_db),
):
    """Upload a bank statement file."""
    try:
        service = BankStatementService()
        uploaded_by = str(uuid.uuid4())  # placeholder
        record = await service.upload_statement(db, company_id, file, uploaded_by)
        return _api_success(
            {
                "id": str(record.id),
                "company_id": str(record.company_id),
                "file_name": record.file_name,
                "parse_status": record.parse_status.value,
                "uploaded_at": record.uploaded_at.isoformat(),
            },
            message="流水文件上传成功",
        )
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("银行流水上传失败")
        raise HTTPException(status_code=ERR_FILE_UPLOAD_FAILED, detail=f"文件上传失败: {exc}")


@router.get("/bank-statements")
async def list_statements(
    company_id: str = Depends(lambda: None),
    db: AsyncSession = Depends(get_db),
):
    """List all bank statements for a company."""
    service = BankStatementService()
    records = await service.list_statements(db, company_id)
    items = []
    for r in records:
        items.append(BankStatementDetail(
            id=str(r.id),
            company_id=str(r.company_id),
            account_no=r.account_no,
            bank_name=r.bank_name,
            statement_source=r.statement_source,
            start_date=r.start_date,
            end_date=r.end_date,
            total_inflow=r.total_inflow,
            total_outflow=r.total_outflow,
            avg_daily_balance=r.avg_daily_balance,
            ending_balance=r.ending_balance,
            transaction_count=r.transaction_count,
            transaction_summary=r.transaction_summary,
            anomaly_flags=r.anomaly_flags,
            parse_status=r.parse_status,
            uploaded_at=r.uploaded_at,
            parsed_at=r.parsed_at,
        ))
    return _api_success(BankStatementListResponse(items=items, total=len(items)).model_dump())


@router.get("/bank-statements/{statement_id}")
async def get_statement(
    statement_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get bank statement detail with statistical analysis."""
    service = BankStatementService()
    try:
        record = await service.get_statement(db, statement_id)
        detail = BankStatementDetail(
            id=str(record.id),
            company_id=str(record.company_id),
            account_no=record.account_no,
            bank_name=record.bank_name,
            statement_source=record.statement_source,
            start_date=record.start_date,
            end_date=record.end_date,
            total_inflow=record.total_inflow,
            total_outflow=record.total_outflow,
            avg_daily_balance=record.avg_daily_balance,
            ending_balance=record.ending_balance,
            transaction_count=record.transaction_count,
            transaction_summary=record.transaction_summary,
            anomaly_flags=record.anomaly_flags,
            parse_status=record.parse_status,
            uploaded_at=record.uploaded_at,
            parsed_at=record.parsed_at,
        )
        return _api_success(detail.model_dump())
    except HTTPException:
        raise


@router.get("/bank-statements/summary")
async def get_summary(
    company_id: str = Depends(lambda: None),
    db: AsyncSession = Depends(get_db),
):
    """Multi-account summary for a company."""
    service = BankStatementService()
    summary = await service.get_summary(db, company_id)
    return _api_success(summary, message="汇总完成")


@router.delete("/bank-statements/{statement_id}")
async def delete_statement(
    statement_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Delete a bank statement."""
    service = BankStatementService()
    try:
        await service.delete_statement(db, statement_id)
        return _api_success(None, message="删除成功")
    except HTTPException:
        raise
