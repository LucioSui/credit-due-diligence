"""企业信息相关 Pydantic schemas."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict


# ---------------------------------------------------------------------------
# 搜索
# ---------------------------------------------------------------------------

class CompanySearchResponse(BaseModel):
    company_name: str
    unified_credit_code: str
    registration_no: Optional[str] = None
    legal_rep: Optional[str] = None
    company_status: Optional[str] = None


# ---------------------------------------------------------------------------
# 基本信息
# ---------------------------------------------------------------------------

class CompanyInfoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    company_name: str
    unified_credit_code: Optional[str] = None
    registration_no: Optional[str] = None
    legal_rep: Optional[str] = None
    registered_capital: Optional[str] = None
    est_date: Optional[str] = None
    company_status: Optional[str] = None
    business_scope: Optional[str] = None
    address: Optional[str] = None
    industry_info: Optional[dict[str, Any]] = None
    data_source: str = "qcc_api"
    cached_at: Optional[datetime] = None


# ---------------------------------------------------------------------------
# 股东 / 高管 / 投资
# ---------------------------------------------------------------------------

class ShareholderResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    shareholder_name: str
    shareholder_type: Optional[str] = None
    share_ratio: Optional[float] = None
    subscribe_capital: Optional[str] = None
    paid_in_capital: Optional[str] = None
    pledge_ratio: Optional[float] = None


class ExecutiveResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    position: Optional[str] = None


class InvestmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    invested_company: str
    invest_ratio: Optional[float] = None
    invest_amount: Optional[str] = None
    invest_date: Optional[str] = None
    status: Optional[str] = None


# ---------------------------------------------------------------------------
# 工商财报 (3.4)
# ---------------------------------------------------------------------------

class CompanyFinancialResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    year: int
    balance_sheet: Optional[dict[str, Any]] = None
    income_statement: Optional[dict[str, Any]] = None
    cash_flow: Optional[dict[str, Any]] = None
    key_indicators: Optional[dict[str, Any]] = None
    data_source: str = "qcc_api"


# ---------------------------------------------------------------------------
# 企业核验
# ---------------------------------------------------------------------------

class CompanyVerifyRequest(BaseModel):
    name: str
    credit_code: str


class CompanyVerifyResponse(BaseModel):
    matched: bool
    company: Optional[CompanyInfoResponse] = None
