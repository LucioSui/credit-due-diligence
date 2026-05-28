"""Credit information routes (3.7 / 3.8).

API paths are mounted under /api/companies/{company_id}.
"""

import logging
import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from models.credit import CreditSource
from schemas.credit import (
    EnterpriseCreditCreate,
    EnterpriseCreditDetail,
    EnterpriseCreditUpdate,
    LegalPersonCreditCreate,
    LegalPersonCreditDetail,
    LegalPersonCreditUpdate,
)
from services.credit_service import CreditService

logger = logging.getLogger(__name__)

router = APIRouter()

ERR_CREDIT_VALIDATION_FAILED = 6001
ERR_FILE_UPLOAD_FAILED = 5001


def _api_success(data, message: str = "success") -> dict:
    return {"code": 0, "message": message, "data": data}


# ── Legal Person Credit ─────────────────────────────────────────────────


@router.post("/legal-person-credit/upload")
async def upload_legal_credit(
    file: UploadFile,
    company_id: str = Depends(lambda: None),
    db: AsyncSession = Depends(get_db),
):
    """Upload a legal person credit report file."""
    try:
        service = CreditService()
        entered_by = str(uuid.uuid4())  # placeholder
        record = await service.upload_legal_credit(db, company_id, file, entered_by)
        return _api_success(
            {
                "id": str(record.id),
                "company_id": str(record.company_id),
                "person_name": record.person_name,
                "credit_source": record.credit_source.value,
                "entered_at": record.entered_at.isoformat(),
            },
            message="法人征信报告上传成功",
        )
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("法人征信报告上传失败")
        raise HTTPException(status_code=ERR_FILE_UPLOAD_FAILED, detail=f"文件上传失败: {exc}")


@router.post("/legal-person-credit")
async def create_legal_credit(
    data: LegalPersonCreditCreate,
    company_id: str = Depends(lambda: None),
    db: AsyncSession = Depends(get_db),
):
    """Manual entry of legal person credit information."""
    try:
        service = CreditService()
        entered_by = str(uuid.uuid4())  # placeholder
        record = await service.create_legal_credit(db, company_id, data, entered_by)
        return _api_success(
            LegalPersonCreditDetail(
                id=str(record.id),
                company_id=str(record.company_id),
                person_name=record.person_name,
                person_id_type=record.person_id_type,
                person_id_no=record.person_id_no,
                credit_source=record.credit_source,
                credit_rating=record.credit_rating,
                loan_accounts=record.loan_accounts,
                credit_card_accounts=record.credit_card_accounts,
                guarantee_info=record.guarantee_info,
                overdue_records=record.overdue_records,
                default_records=record.default_records,
                report_snapshot=record.report_snapshot,
                entered_at=record.entered_at,
                updated_at=record.updated_at,
            ).model_dump(),
            message="法人征信录入成功",
        )
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("法人征信录入失败")
        raise HTTPException(
            status_code=ERR_CREDIT_VALIDATION_FAILED, detail=f"录入校验失败: {exc}"
        )


@router.get("/legal-person-credit")
async def list_legal_credit(
    company_id: str = Depends(lambda: None),
    db: AsyncSession = Depends(get_db),
):
    """List legal person credit records for a company."""
    service = CreditService()
    records = await service.list_legal_credit(db, company_id)
    items = []
    for r in records:
        items.append(LegalPersonCreditDetail(
            id=str(r.id),
            company_id=str(r.company_id),
            person_name=r.person_name,
            person_id_type=r.person_id_type,
            person_id_no=r.person_id_no,
            credit_source=r.credit_source,
            credit_rating=r.credit_rating,
            loan_accounts=r.loan_accounts,
            credit_card_accounts=r.credit_card_accounts,
            guarantee_info=r.guarantee_info,
            overdue_records=r.overdue_records,
            default_records=r.default_records,
            report_snapshot=r.report_snapshot,
            entered_at=r.entered_at,
            updated_at=r.updated_at,
        ))
    return _api_success({"items": [i.model_dump() for i in items], "total": len(items)})


@router.get("/legal-person-credit/{credit_id}")
async def get_legal_credit(
    credit_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get legal person credit detail."""
    service = CreditService()
    try:
        record = await service.get_legal_credit(db, credit_id)
        detail = LegalPersonCreditDetail(
            id=str(record.id),
            company_id=str(record.company_id),
            person_name=record.person_name,
            person_id_type=record.person_id_type,
            person_id_no=record.person_id_no,
            credit_source=record.credit_source,
            credit_rating=record.credit_rating,
            loan_accounts=record.loan_accounts,
            credit_card_accounts=record.credit_card_accounts,
            guarantee_info=record.guarantee_info,
            overdue_records=record.overdue_records,
            default_records=record.default_records,
            report_snapshot=record.report_snapshot,
            entered_at=record.entered_at,
            updated_at=record.updated_at,
        )
        return _api_success(detail.model_dump())
    except HTTPException:
        raise


@router.put("/legal-person-credit/{credit_id}")
async def update_legal_credit(
    credit_id: str,
    data: LegalPersonCreditUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update legal person credit record."""
    try:
        service = CreditService()
        record = await service.update_legal_credit(db, credit_id, data)
        return _api_success(
            LegalPersonCreditDetail(
                id=str(record.id),
                company_id=str(record.company_id),
                person_name=record.person_name,
                person_id_type=record.person_id_type,
                person_id_no=record.person_id_no,
                credit_source=record.credit_source,
                credit_rating=record.credit_rating,
                loan_accounts=record.loan_accounts,
                credit_card_accounts=record.credit_card_accounts,
                guarantee_info=record.guarantee_info,
                overdue_records=record.overdue_records,
                default_records=record.default_records,
                report_snapshot=record.report_snapshot,
                entered_at=record.entered_at,
                updated_at=record.updated_at,
            ).model_dump(),
            message="更新成功",
        )
    except HTTPException:
        raise


@router.delete("/legal-person-credit/{credit_id}")
async def delete_legal_credit(
    credit_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Delete a legal person credit record."""
    service = CreditService()
    try:
        await service.delete_legal_credit(db, credit_id)
        return _api_success(None, message="删除成功")
    except HTTPException:
        raise


# ── Enterprise Credit ───────────────────────────────────────────────────


@router.post("/enterprise-credit/upload")
async def upload_enterprise_credit(
    file: UploadFile,
    company_id: str = Depends(lambda: None),
    db: AsyncSession = Depends(get_db),
):
    """Upload an enterprise credit report file."""
    try:
        service = CreditService()
        entered_by = str(uuid.uuid4())  # placeholder
        record = await service.upload_enterprise_credit(db, company_id, file, entered_by)
        return _api_success(
            {
                "id": str(record.id),
                "company_id": str(record.company_id),
                "credit_source": record.credit_source.value,
                "entered_at": record.entered_at.isoformat(),
            },
            message="企业征信报告上传成功",
        )
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("企业征信报告上传失败")
        raise HTTPException(status_code=ERR_FILE_UPLOAD_FAILED, detail=f"文件上传失败: {exc}")


@router.post("/enterprise-credit")
async def create_enterprise_credit(
    data: EnterpriseCreditCreate,
    company_id: str = Depends(lambda: None),
    db: AsyncSession = Depends(get_db),
):
    """Manual entry of enterprise credit information."""
    try:
        service = CreditService()
        entered_by = str(uuid.uuid4())  # placeholder
        record = await service.create_enterprise_credit(db, company_id, data, entered_by)
        return _api_success(
            EnterpriseCreditDetail(
                id=str(record.id),
                company_id=str(record.company_id),
                credit_source=record.credit_source,
                total_credit_line=record.total_credit_line,
                used_credit_line=record.used_credit_line,
                remaining_credit_line=record.remaining_credit_line,
                loan_details=record.loan_details,
                guarantee_out=record.guarantee_out,
                guarantee_in=record.guarantee_in,
                overdue_info=record.overdue_info,
                attention_list=record.attention_list,
                multi_lending_flag=record.multi_lending_flag,
                lender_count=record.lender_count,
                report_snapshot=record.report_snapshot,
                entered_at=record.entered_at,
                updated_at=record.updated_at,
            ).model_dump(),
            message="企业征信录入成功",
        )
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("企业征信录入失败")
        raise HTTPException(
            status_code=ERR_CREDIT_VALIDATION_FAILED, detail=f"录入校验失败: {exc}"
        )


@router.get("/enterprise-credit")
async def get_enterprise_credit(
    company_id: str = Depends(lambda: None),
    db: AsyncSession = Depends(get_db),
):
    """Get enterprise credit detail (one record per company)."""
    service = CreditService()
    record = await service.get_enterprise_credit(db, company_id)
    if not record:
        return _api_success(None, message="暂无企业征信记录")
    detail = EnterpriseCreditDetail(
        id=str(record.id),
        company_id=str(record.company_id),
        credit_source=record.credit_source,
        total_credit_line=record.total_credit_line,
        used_credit_line=record.used_credit_line,
        remaining_credit_line=record.remaining_credit_line,
        loan_details=record.loan_details,
        guarantee_out=record.guarantee_out,
        guarantee_in=record.guarantee_in,
        overdue_info=record.overdue_info,
        attention_list=record.attention_list,
        multi_lending_flag=record.multi_lending_flag,
        lender_count=record.lender_count,
        report_snapshot=record.report_snapshot,
        entered_at=record.entered_at,
        updated_at=record.updated_at,
    )
    return _api_success(detail.model_dump())


@router.put("/enterprise-credit")
async def update_enterprise_credit(
    data: EnterpriseCreditUpdate,
    company_id: str = Depends(lambda: None),
    db: AsyncSession = Depends(get_db),
):
    """Update enterprise credit record."""
    try:
        service = CreditService()
        record = await service.update_enterprise_credit(db, company_id, data)
        return _api_success(
            EnterpriseCreditDetail(
                id=str(record.id),
                company_id=str(record.company_id),
                credit_source=record.credit_source,
                total_credit_line=record.total_credit_line,
                used_credit_line=record.used_credit_line,
                remaining_credit_line=record.remaining_credit_line,
                loan_details=record.loan_details,
                guarantee_out=record.guarantee_out,
                guarantee_in=record.guarantee_in,
                overdue_info=record.overdue_info,
                attention_list=record.attention_list,
                multi_lending_flag=record.multi_lending_flag,
                lender_count=record.lender_count,
                report_snapshot=record.report_snapshot,
                entered_at=record.entered_at,
                updated_at=record.updated_at,
            ).model_dump(),
            message="更新成功",
        )
    except HTTPException:
        raise
