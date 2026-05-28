"""Credit information management service (3.7 / 3.8)."""

import logging
import re
from datetime import datetime
from typing import Optional

from fastapi import HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.credit import (
    CreditRating,
    CreditSource,
    EnterpriseCredit,
    LegalPersonCredit,
    PersonIdType,
)
from schemas.credit import (
    EnterpriseCreditCreate,
    EnterpriseCreditUpdate,
    LegalPersonCreditCreate,
    LegalPersonCreditUpdate,
)
from services.file_parser import FileParser
from storage.file_storage import FileStorage

logger = logging.getLogger(__name__)

ERR_CREDIT_VALIDATION_FAILED = 6001
ERR_FILE_UPLOAD_FAILED = 5001


class CreditService:
    """Business logic for legal person and enterprise credit records."""

    # ── Legal Person Credit ──────────────────────────────────────────────

    async def upload_legal_credit(
        self,
        db: AsyncSession,
        company_id: str,
        file: UploadFile,
        entered_by: str,
    ) -> LegalPersonCredit:
        """Upload a legal person credit report file."""
        content = await file.read()
        file_size = len(content)

        FileStorage.validate_file(file.filename or "unknown", "credit_report", file_size)

        save_path = FileStorage.get_upload_path(
            company_id, "credit_report", file.filename or "credit_report"
        )
        await FileStorage.save_file(content, save_path)

        # MVP: basic parsing to extract person name if possible
        parser = FileParser()
        parsed = await parser.parse_credit_report(save_path, "pdf")

        credit = LegalPersonCredit(
            company_id=company_id,
            person_name="待确认",
            person_id_type=PersonIdType.ID_CARD,
            person_id_no="待录入",
            credit_source=CreditSource.UPLOADED,
            report_snapshot=parsed,
            report_file_path=save_path,
            entered_by=entered_by,
        )
        db.add(credit)
        await db.commit()
        await db.refresh(credit)
        return credit

    async def create_legal_credit(
        self,
        db: AsyncSession,
        company_id: str,
        data: LegalPersonCreditCreate,
        entered_by: str,
    ) -> LegalPersonCredit:
        """Manual entry of legal person credit information."""
        # Validate ID number if provided
        if data.person_id_no:
            self._validate_id_number(data.person_id_no, data.person_id_type)

        credit = LegalPersonCredit(
            company_id=company_id,
            person_name=data.person_name,
            person_id_type=data.person_id_type,
            person_id_no=data.person_id_no or "未提供",
            credit_source=data.credit_source,
            loan_accounts=data.loan_accounts,
            credit_card_accounts=data.credit_card_accounts,
            guarantee_info=data.guarantee_info,
            overdue_records=data.overdue_records,
            default_records=data.default_records,
            entered_by=entered_by,
        )
        db.add(credit)
        await db.commit()
        await db.refresh(credit)
        return credit

    async def list_legal_credit(
        self,
        db: AsyncSession,
        company_id: str,
    ) -> list[LegalPersonCredit]:
        """Return all legal person credit records for a company."""
        stmt = (
            select(LegalPersonCredit)
            .where(LegalPersonCredit.company_id == company_id)
            .order_by(LegalPersonCredit.entered_at.desc())
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def get_legal_credit(
        self,
        db: AsyncSession,
        credit_id: str,
    ) -> LegalPersonCredit:
        """Fetch a single legal person credit record by id."""
        stmt = select(LegalPersonCredit).where(LegalPersonCredit.id == credit_id)
        result = await db.execute(stmt)
        record = result.scalar_one_or_none()
        if not record:
            raise HTTPException(status_code=404, detail="法人征信记录不存在")
        return record

    async def update_legal_credit(
        self,
        db: AsyncSession,
        credit_id: str,
        data: LegalPersonCreditUpdate,
    ) -> LegalPersonCredit:
        """Update a legal person credit record."""
        record = await self.get_legal_credit(db, credit_id)

        update_data = data.model_dump(exclude_unset=True)
        if "person_id_no" in update_data and update_data["person_id_no"]:
            self._validate_id_number(update_data["person_id_no"], record.person_id_type)

        for field, value in update_data.items():
            setattr(record, field, value)

        record.updated_at = datetime.now()
        await db.commit()
        await db.refresh(record)
        return record

    async def delete_legal_credit(
        self,
        db: AsyncSession,
        credit_id: str,
    ) -> None:
        """Delete a legal person credit record."""
        record = await self.get_legal_credit(db, credit_id)
        if record.report_file_path:
            await FileStorage.delete_file(record.report_file_path)
        await db.delete(record)
        await db.commit()

    # ── Enterprise Credit ────────────────────────────────────────────────

    async def upload_enterprise_credit(
        self,
        db: AsyncSession,
        company_id: str,
        file: UploadFile,
        entered_by: str,
    ) -> EnterpriseCredit:
        """Upload an enterprise credit report file."""
        content = await file.read()
        file_size = len(content)

        FileStorage.validate_file(file.filename or "unknown", "credit_report", file_size)

        save_path = FileStorage.get_upload_path(
            company_id, "credit_report", file.filename or "enterprise_credit"
        )
        await FileStorage.save_file(content, save_path)

        parser = FileParser()
        parsed = await parser.parse_credit_report(save_path, "pdf")

        credit = EnterpriseCredit(
            company_id=company_id,
            credit_source=CreditSource.UPLOADED,
            report_snapshot=parsed,
            report_file_path=save_path,
            entered_by=entered_by,
        )
        db.add(credit)
        await db.commit()
        await db.refresh(credit)
        return credit

    async def create_enterprise_credit(
        self,
        db: AsyncSession,
        company_id: str,
        data: EnterpriseCreditCreate,
        entered_by: str,
    ) -> EnterpriseCredit:
        """Manual entry of enterprise credit information."""
        # Validate: used <= total
        if (
            data.used_credit_line is not None
            and data.total_credit_line is not None
            and data.used_credit_line > data.total_credit_line
        ):
            raise HTTPException(
                status_code=ERR_CREDIT_VALIDATION_FAILED,
                detail="已用授信额度不能大于授信总额",
            )

        total = data.total_credit_line or 0
        used = data.used_credit_line or 0
        remaining = round(total - used, 2) if total and used else None

        credit = EnterpriseCredit(
            company_id=company_id,
            credit_source=data.credit_source,
            total_credit_line=data.total_credit_line,
            used_credit_line=data.used_credit_line,
            remaining_credit_line=remaining,
            loan_details=data.loan_details,
            guarantee_out=data.guarantee_out,
            guarantee_in=data.guarantee_in,
            overdue_info=data.overdue_info,
            attention_list=data.attention_list,
            entered_by=entered_by,
        )
        db.add(credit)
        await db.commit()
        await db.refresh(credit)
        return credit

    async def get_enterprise_credit(
        self,
        db: AsyncSession,
        company_id: str,
    ) -> Optional[EnterpriseCredit]:
        """Return the latest enterprise credit record for a company."""
        stmt = (
            select(EnterpriseCredit)
            .where(EnterpriseCredit.company_id == company_id)
            .order_by(EnterpriseCredit.entered_at.desc())
            .limit(1)
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def update_enterprise_credit(
        self,
        db: AsyncSession,
        company_id: str,
        data: EnterpriseCreditUpdate,
    ) -> EnterpriseCredit:
        """Update enterprise credit record."""
        credit = await self.get_enterprise_credit(db, company_id)
        if not credit:
            raise HTTPException(status_code=404, detail="企业征信记录不存在")

        update_data = data.model_dump(exclude_unset=True)

        # Validation: used <= total
        new_total = update_data.get("total_credit_line", credit.total_credit_line)
        new_used = update_data.get("used_credit_line", credit.used_credit_line)
        if (
            new_used is not None
            and new_total is not None
            and new_used > new_total
        ):
            raise HTTPException(
                status_code=ERR_CREDIT_VALIDATION_FAILED,
                detail="已用授信额度不能大于授信总额",
            )

        for field, value in update_data.items():
            setattr(credit, field, value)

        # Recalculate remaining
        if "total_credit_line" in update_data or "used_credit_line" in update_data:
            t = credit.total_credit_line or 0
            u = credit.used_credit_line or 0
            credit.remaining_credit_line = round(t - u, 2)

        credit.updated_at = datetime.now()
        await db.commit()
        await db.refresh(credit)
        return credit

    # ── Helpers ──────────────────────────────────────────────────────────

    @staticmethod
    def _validate_id_number(id_no: str, id_type: PersonIdType) -> None:
        """Basic ID number format validation."""
        if id_type == PersonIdType.ID_CARD:
            # Chinese ID: 18 chars (17 + checksum) or 15 chars (old)
            pattern = r"^\d{15}(\d{2}[0-9Xx])?$"
            if not re.match(pattern, id_no):
                raise HTTPException(
                    status_code=ERR_CREDIT_VALIDATION_FAILED,
                    detail="身份证号格式不正确（应为15或18位）",
                )
        elif id_type == PersonIdType.UNIFIED_SOCIAL_CODE:
            # 18 chars: starts with 91 or similar
            pattern = r"^[0-9A-HJ-NPQRTUWXY]\d{6}[0-9A-HJ-NPQRTUWXY]{10}$"
            if not re.match(pattern, id_no):
                raise HTTPException(
                    status_code=ERR_CREDIT_VALIDATION_FAILED,
                    detail="统一社会信用代码格式不正确（应为18位）",
                )
