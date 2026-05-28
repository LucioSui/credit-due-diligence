"""评级引擎路由."""

from __future__ import annotations

import logging
from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from auth.dependencies import require_approver
from database import get_db
from schemas.rating import RatingAPIResponse, RatingListAPIResponse, RatingRequest, RatingResponse
from services.company_service import CompanyService
from services.rating_engine import RatingEngine
from services.risk_service import RiskService

logger = logging.getLogger(__name__)

router = APIRouter()
rating_engine = RatingEngine()
company_service = CompanyService()
risk_service = RiskService()


def _success(data: Any, message: str = "success") -> dict:
    return {"code": 0, "message": message, "data": data}


# ---------------------------------------------------------------------------
# 手动评级
# ---------------------------------------------------------------------------

@router.post("/rating", response_model=None)
async def create_rating(
    req: RatingRequest,
    current_user=Depends(require_approver),
    db: AsyncSession = Depends(get_db),
):
    """手动触发评级."""
    try:
        company = await company_service.get_company_info(db, req.company_id)
        risks = (await risk_service.get_risk_summary(db, company)) if hasattr(risk_service, 'get_risk_summary') else {}

        result = await rating_engine.calculate_rating(
            db=db,
            company=company,
            risks=risks if isinstance(risks, dict) else {},
        )
        return _success(RatingResponse(**result).model_dump(mode="json"))
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        logger.exception("评级失败: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))


# ---------------------------------------------------------------------------
# 评级历史
# ---------------------------------------------------------------------------

@router.get("/rating/company/{company_id}", response_model=None)
async def get_rating_history(
    company_id: UUID,
    current_user=Depends(require_approver),
    db: AsyncSession = Depends(get_db),
):
    """获取企业评级历史."""
    try:
        history = await rating_engine.get_rating_history(db, str(company_id))
        return _success(history)
    except Exception as exc:
        logger.exception("获取评级历史失败: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))
