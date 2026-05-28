"""Schemas for credit information (法人征信 & 企业征信)."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, field_validator

from models.credit import CreditRating, CreditSource, PersonIdType


# ── Legal Person Credit (法人征信) ──────────────────────────────────────


class LegalPersonCreditCreate(BaseModel):
    person_name: str
    person_id_type: PersonIdType = PersonIdType.ID_CARD
    person_id_no: Optional[str] = None
    credit_source: CreditSource = CreditSource.MANUAL
    loan_accounts: Optional[dict] = None
    credit_card_accounts: Optional[dict] = None
    guarantee_info: Optional[dict] = None
    overdue_records: Optional[dict] = None
    default_records: Optional[dict] = None


class LegalPersonCreditUpdate(BaseModel):
    person_id_no: Optional[str] = None
    credit_rating: Optional[CreditRating] = None
    loan_accounts: Optional[dict] = None
    credit_card_accounts: Optional[dict] = None
    guarantee_info: Optional[dict] = None
    overdue_records: Optional[dict] = None
    default_records: Optional[dict] = None


class LegalPersonCreditDetail(BaseModel):
    id: str
    company_id: str
    person_name: str
    person_id_type: PersonIdType
    person_id_no: str
    credit_source: CreditSource
    credit_rating: Optional[CreditRating] = None
    loan_accounts: Optional[dict] = None
    credit_card_accounts: Optional[dict] = None
    guarantee_info: Optional[dict] = None
    overdue_records: Optional[dict] = None
    default_records: Optional[dict] = None
    report_snapshot: Optional[dict] = None
    entered_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ── Enterprise Credit (企业征信) ────────────────────────────────────────


class EnterpriseCreditCreate(BaseModel):
    credit_source: CreditSource = CreditSource.MANUAL
    total_credit_line: Optional[float] = None
    used_credit_line: Optional[float] = None
    loan_details: Optional[dict] = None
    guarantee_out: Optional[dict] = None
    guarantee_in: Optional[dict] = None
    overdue_info: Optional[dict] = None
    attention_list: Optional[dict] = None

    @field_validator("used_credit_line")
    @classmethod
    def validate_used_line_not_exceed_total(cls, v: Optional[float], info) -> Optional[float]:
        if v is None:
            return v
        total = info.data.get("total_credit_line")
        if total is not None and v > total:
            raise ValueError("已用授信额度不能大于授信总额")
        return v


class EnterpriseCreditUpdate(BaseModel):
    total_credit_line: Optional[float] = None
    used_credit_line: Optional[float] = None
    loan_details: Optional[dict] = None
    guarantee_out: Optional[dict] = None
    guarantee_in: Optional[dict] = None
    overdue_info: Optional[dict] = None
    attention_list: Optional[dict] = None
    multi_lending_flag: Optional[bool] = None
    lender_count: Optional[int] = None


class EnterpriseCreditDetail(BaseModel):
    id: str
    company_id: str
    credit_source: CreditSource
    total_credit_line: Optional[float] = None
    used_credit_line: Optional[float] = None
    remaining_credit_line: Optional[float] = None
    loan_details: Optional[dict] = None
    guarantee_out: Optional[dict] = None
    guarantee_in: Optional[dict] = None
    overdue_info: Optional[dict] = None
    attention_list: Optional[dict] = None
    multi_lending_flag: bool
    lender_count: Optional[int] = None
    report_snapshot: Optional[dict] = None
    entered_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
