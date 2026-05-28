"""企业信息路由 — 搜索、基本信息、工商数据、财报."""

from __future__ import annotations

import logging
from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from auth.dependencies import require_approver
from database import get_db
from models.company import Company
from schemas.company import (
    CompanyFinancialResponse,
    CompanyInfoResponse,
    CompanySearchResponse,
    CompanyVerifyResponse,
    ExecutiveResponse,
    InvestmentResponse,
    ShareholderResponse,
)
from services.company_service import CompanyService
from services.financial_service import FinancialService
from services.shareholding_service import ShareholdingService

logger = logging.getLogger(__name__)

router = APIRouter()

company_service = CompanyService()
shareholding_service = ShareholdingService()
financial_service = FinancialService()


def _success(data: Any, message: str = "success") -> dict:
    return {"code": 0, "message": message, "data": data}


def _error(message: str, code: int = 400) -> dict:
    return {"code": code, "message": message, "data": None}


# ---------------------------------------------------------------------------
# 企业搜索
# ---------------------------------------------------------------------------

@router.get("/companies/search", response_model=None)
async def search_companies(
    q: str = Query(..., min_length=1, description="搜索关键词"),
    current_user=Depends(require_approver),
    db: AsyncSession = Depends(get_db),
):
    """企业模糊搜索."""
    try:
        results = await company_service.search_company(q)
        return _success([CompanySearchResponse(**r).model_dump(mode="json") for r in results])
    except Exception as exc:
        logger.exception("企业搜索失败: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))


# ---------------------------------------------------------------------------
# 企业基本信息
# ---------------------------------------------------------------------------

@router.get("/companies/{company_id}", response_model=None)
async def get_company(
    company_id: UUID,
    current_user=Depends(require_approver),
    db: AsyncSession = Depends(get_db),
):
    """企业基本信息."""
    try:
        company = await company_service.get_company_info(db, str(company_id))
        result = CompanyInfoResponse.model_validate(company).model_dump(mode="json")
        return _success(result)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        logger.exception("获取企业信息失败: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))


# ---------------------------------------------------------------------------
# 股东 / 高管 / 投资
# ---------------------------------------------------------------------------

@router.get("/companies/{company_id}/shareholders", response_model=None)
async def list_shareholders(
    company_id: UUID,
    current_user=Depends(require_approver),
    db: AsyncSession = Depends(get_db),
):
    """股东信息."""
    try:
        company = await company_service.get_company_info(db, str(company_id))
        shareholders = await shareholding_service.get_shareholders(db, company)
        items = [ShareholderResponse.model_validate(s).model_dump(mode="json") for s in shareholders]
        return _success(items)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        logger.exception("获取股东信息失败: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/companies/{company_id}/executives", response_model=None)
async def list_executives(
    company_id: UUID,
    current_user=Depends(require_approver),
    db: AsyncSession = Depends(get_db),
):
    """高管信息."""
    try:
        company = await company_service.get_company_info(db, str(company_id))
        executives = await shareholding_service.get_executives(db, company)
        items = [ExecutiveResponse.model_validate(e).model_dump(mode="json") for e in executives]
        return _success(items)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        logger.exception("获取高管信息失败: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/companies/{company_id}/investments", response_model=None)
async def list_investments(
    company_id: UUID,
    current_user=Depends(require_approver),
    db: AsyncSession = Depends(get_db),
):
    """对外投资."""
    try:
        company = await company_service.get_company_info(db, str(company_id))
        investments = await shareholding_service.get_investments(db, company)
        items = [InvestmentResponse.model_validate(inv).model_dump(mode="json") for inv in investments]
        return _success(items)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        logger.exception("获取对外投资失败: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))


# ---------------------------------------------------------------------------
# 工商财报 (3.4)
# ---------------------------------------------------------------------------

@router.get("/companies/{company_id}/financials", response_model=None)
async def list_financials(
    company_id: UUID,
    year: str | None = Query(None, description="指定年份，如 2023"),
    current_user=Depends(require_approver),
    db: AsyncSession = Depends(get_db),
):
    """工商财报数据(3.4)."""
    try:
        company = await company_service.get_company_info(db, str(company_id))
        financials = await financial_service.get_financials(db, company, year=year)
        items = [CompanyFinancialResponse.model_validate(f).model_dump(mode="json") for f in financials]
        return _success(items)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        logger.exception("获取工商财报失败: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))


# ---------------------------------------------------------------------------
# 企业核验
# ---------------------------------------------------------------------------

@router.get("/companies/{company_id}/verify", response_model=None)
async def verify_company(
    company_id: UUID,
    name: str = Query(..., description="企业名称"),
    credit_code: str = Query(..., description="统一社会信用代码"),
    current_user=Depends(require_approver),
    db: AsyncSession = Depends(get_db),
):
    """企业身份核验 (名称 + 信用代码二要素)."""
    try:
        # 先确认公司存在
        await company_service.get_company_info(db, str(company_id))
        result = await company_service.verify_company(name, credit_code)
        company_data = None
        if result.get("company"):
            company_data = CompanyInfoResponse(
                **result["company"],
                id="",  # 核验接口没有 DB 记录
            ).model_dump(mode="json")
            company_data["id"] = str(company_id)
        response = CompanyVerifyResponse(
            matched=result["matched"],
            company=company_data if result["matched"] else None,
        )
        return _success(response.model_dump(mode="json"))
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        logger.exception("企业核验失败: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))
