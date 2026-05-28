"""Schemas for bank statements (银行流水)."""

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel

from models.bank_statement import BankStatementParseStatus, StatementSource


class BankStatementFetchRequest(BaseModel):
    account_no: str
    start_date: date
    end_date: date


class BankStatementDetail(BaseModel):
    id: str
    company_id: str
    account_no: Optional[str] = None
    bank_name: Optional[str] = None
    statement_source: StatementSource
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    total_inflow: Optional[float] = None
    total_outflow: Optional[float] = None
    avg_daily_balance: Optional[float] = None
    ending_balance: Optional[float] = None
    transaction_count: Optional[int] = None
    transaction_summary: Optional[dict] = None
    anomaly_flags: Optional[dict] = None
    parse_status: BankStatementParseStatus
    uploaded_at: datetime
    parsed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class BankStatementSummary(BaseModel):
    total_accounts: int
    total_inflow: float
    total_outflow: float
    total_ending_balance: float
    accounts: list[dict]


class BankStatementListResponse(BaseModel):
    items: list[BankStatementDetail]
    total: int
