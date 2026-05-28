"""股权穿透路由."""

from __future__ import annotations

import logging
from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from auth.dependencies import require_approver
from database import get_db
from schemas.equity import (
    EquityChainDetailResponse,
    EquityChainResponse,
    UBOResponse,
)
from services.company_service import CompanyService
from services.equity_service import EquityService

logger = logging.getLogger(__name__)

router = APIRouter()

company_service = CompanyService()
equity_service = EquityService()


def _success(data: Any, message: str = "success") -> dict:
    return {"code": 0, "message": message, "data": data}


# ---------------------------------------------------------------------------
# 完整股权穿透
# ---------------------------------------------------------------------------

@router.get("/companies/{company_id}/equity-chain", response_model=None)
async def get_equity_chain(
    company_id: UUID,
    current_user=Depends(require_approver),
    db: AsyncSession = Depends(get_db),
):
    """股权穿透路径（完整）."""
    try:
        company = await company_service.get_company_info(db, str(company_id))
        data = await equity_service.get_equity_chain(db, company)

        # 将 dict 转为 schema 对象再 dump
        response = EquityChainDetailResponse(
            upward_chains=[EquityChainResponse(**c) for c in data.get("upward_chains", [])],
            downward_chains=[EquityChainResponse(**c) for c in data.get("downward_chains", [])],
            ubos=data.get("ubos", []),
            controller=data.get("controller"),
        )
        return _success(response.model_dump(mode="json"))
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        logger.exception("获取股权穿透失败: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))


# ---------------------------------------------------------------------------
# 受益所有人
# ---------------------------------------------------------------------------

@router.get("/companies/{company_id}/ubo", response_model=None)
async def get_ubos(
    company_id: UUID,
    current_user=Depends(require_approver),
    db: AsyncSession = Depends(get_db),
):
    """受益所有人."""
    try:
        company = await company_service.get_company_info(db, str(company_id))
        ubos = await equity_service.get_ubos(db, company)
        items = [UBOResponse(**ubo).model_dump(mode="json") for ubo in ubos]
        return _success(items)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        logger.exception("获取受益所有人失败: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))


# ---------------------------------------------------------------------------
# 实际控制人
# ---------------------------------------------------------------------------

@router.get("/companies/{company_id}/controller", response_model=None)
async def get_controller(
    company_id: UUID,
    current_user=Depends(require_approver),
    db: AsyncSession = Depends(get_db),
):
    """实际控制人."""
    try:
        company = await company_service.get_company_info(db, str(company_id))
        controller = await equity_service.get_controller(db, company)
        if not controller:
            return _success(None, "未找到实际控制人信息")
        return _success(controller)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        logger.exception("获取实际控制人失败: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))
