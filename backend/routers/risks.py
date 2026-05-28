"""风险扫描路由."""

from __future__ import annotations

import logging
from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from auth.dependencies import require_approver
from database import get_db
from models.company_risk import RiskType
from schemas.risk import RiskListResponse, RiskResponse, RiskSummaryResponse
from services.company_service import CompanyService
from services.risk_service import RiskService

logger = logging.getLogger(__name__)

router = APIRouter()

company_service = CompanyService()
risk_service = RiskService()


def _success(data: Any, message: str = "success") -> dict:
    return {"code": 0, "message": message, "data": data}


# ---------------------------------------------------------------------------
# 风险汇总
# ---------------------------------------------------------------------------

@router.get("/companies/{company_id}/risks", response_model=None)
async def get_risk_summary(
    company_id: UUID,
    current_user=Depends(require_approver),
    db: AsyncSession = Depends(get_db),
):
    """全部风险汇总."""
    try:
        company = await company_service.get_company_info(db, str(company_id))
        summary = await risk_service.get_risk_summary(db, company)
        response = RiskSummaryResponse(**summary)
        return _success(response.model_dump(mode="json"))
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        logger.exception("获取风险汇总失败: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))


# ---------------------------------------------------------------------------
# 按类型获取风险
# ---------------------------------------------------------------------------

@router.get("/companies/{company_id}/risks/lawsuits", response_model=None)
async def get_lawsuits(
    company_id: UUID,
    current_user=Depends(require_approver),
    db: AsyncSession = Depends(get_db),
):
    """诉讼记录."""
    return await _get_risks_by_type(db, company_id, "lawsuit")


@router.get("/companies/{company_id}/risks/dishonest", response_model=None)
async def get_dishonest(
    company_id: UUID,
    current_user=Depends(require_approver),
    db: AsyncSession = Depends(get_db),
):
    """失信记录."""
    return await _get_risks_by_type(db, company_id, "dishonest")


@router.get("/companies/{company_id}/risks/restrictions", response_model=None)
async def get_restrictions(
    company_id: UUID,
    current_user=Depends(require_approver),
    db: AsyncSession = Depends(get_db),
):
    """限高记录."""
    return await _get_risks_by_type(db, company_id, "restriction")


@router.get("/companies/{company_id}/risks/penalties", response_model=None)
async def get_penalties(
    company_id: UUID,
    current_user=Depends(require_approver),
    db: AsyncSession = Depends(get_db),
):
    """行政处罚."""
    return await _get_risks_by_type(db, company_id, "penalty")


# ---------------------------------------------------------------------------
# 内部辅助
# ---------------------------------------------------------------------------

async def _get_risks_by_type(
    db: AsyncSession,
    company_id: UUID,
    risk_type: str,
):
    """通用: 按类型获取风险列表."""
    try:
        company = await company_service.get_company_info(db, str(company_id))
        risks = await risk_service.get_risks_by_type(db, company, risk_type)
        items = [RiskResponse.model_validate(r).model_dump(mode="json") for r in risks]
        response = RiskListResponse(items=items, total=len(items))
        return _success(response.model_dump(mode="json"))
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        logger.exception("获取风险列表失败: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))
