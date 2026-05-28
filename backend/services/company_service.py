"""企业信息服务 — 搜索、核验、基本信息."""

from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.company import Company
from services.qcc_client import QCCClient

logger = logging.getLogger(__name__)

# 缓存 TTL（秒）
COMPANY_INFO_TTL = 24 * 3600  # 24 小时


class CompanyService:
    """企业信息服务 — 搜索、核验、基本信息."""

    def __init__(self) -> None:
        self._qcc = QCCClient()

    # ------------------------------------------------------------------
    # 公开方法
    # ------------------------------------------------------------------

    async def search_company(self, keyword: str) -> list[dict[str, Any]]:
        """企业模糊搜索，调用 QCCClient.search_company."""
        return await self._qcc.search_company(keyword)

    async def get_or_fetch_company(
        self,
        db: AsyncSession,
        company_name: str,
        credit_code: str | None = None,
    ) -> Company:
        """获取企业基本信息，先查本地缓存，过期则从企查查拉取."""
        # 1. 查本地 DB
        stmt = select(Company).where(Company.company_name == company_name)
        result = await db.execute(stmt)
        company = result.scalar_one_or_none()

        now = datetime.now(timezone.utc)

        # 2. 如果存在且未过期，直接返回
        if company is not None and company.expires_at is not None:
            if company.expires_at > now:
                return company
            # 过期了，需要刷新

        # 3. 从企查查拉取最新数据
        qcc_data = await self._qcc.get_company_info(company_name, credit_code)
        company = await self._upsert_company(db, qcc_data, now)
        await db.commit()
        await db.refresh(company)
        return company

    async def verify_company(self, name: str, credit_code: str) -> dict[str, Any]:
        """企业二要素核验: 名称 + 信用代码是否匹配."""
        qcc_data = await self._qcc.get_company_info(name, credit_code)
        matched = (
            qcc_data.get("company_name") == name
            and qcc_data.get("unified_credit_code") == credit_code
        )
        return {
            "matched": matched,
            "company": qcc_data if matched else None,
        }

    async def get_company_info(
        self,
        db: AsyncSession,
        company_id: str,
    ) -> Company:
        """获取企业详细信息（含缓存刷新逻辑）."""
        stmt = select(Company).where(Company.id == company_id)
        result = await db.execute(stmt)
        company = result.scalar_one_or_none()
        if company is None:
            raise ValueError(f"企业不存在: id={company_id}")

        now = datetime.now(timezone.utc)
        if company.expires_at is not None and company.expires_at <= now:
            qcc_data = await self._qcc.get_company_info(company.company_name)
            company = await self._upsert_company(db, qcc_data, now)
            await db.commit()
            await db.refresh(company)
        return company

    # ------------------------------------------------------------------
    # 内部方法
    # ------------------------------------------------------------------

    async def _upsert_company(
        self,
        db: AsyncSession,
        qcc_data: dict[str, Any],
        now: datetime,
    ) -> Company:
        """将企查查返回的企业数据写入或更新到数据库."""
        name = qcc_data["company_name"]
        credit_code = qcc_data.get("unified_credit_code")

        # 检查是否已存在
        stmt = select(Company).where(Company.company_name == name)
        result = await db.execute(stmt)
        company = result.scalar_one_or_none()

        expires_at = now + timedelta(seconds=COMPANY_INFO_TTL)
        est_date_raw = qcc_data.get("establish_date")
        est_date = None
        if est_date_raw:
            try:
                est_date = datetime.strptime(est_date_raw, "%Y-%m-%d")
            except (ValueError, TypeError):
                est_date = None

        industry_info = None
        if qcc_data.get("industry"):
            industry_info = {"industry": qcc_data["industry"]}

        if company is None:
            company = Company(
                company_name=name,
                unified_credit_code=credit_code,
                registration_no=qcc_data.get("registration_no"),
                legal_rep=qcc_data.get("legal_rep"),
                registered_capital=qcc_data.get("registered_capital"),
                est_date=est_date,
                company_status=qcc_data.get("company_status"),
                business_scope=qcc_data.get("business_scope"),
                address=qcc_data.get("address"),
                industry_info=industry_info,
                cached_at=now,
                expires_at=expires_at,
            )
            db.add(company)
        else:
            company.unified_credit_code = credit_code
            company.registration_no = qcc_data.get("registration_no")
            company.legal_rep = qcc_data.get("legal_rep")
            company.registered_capital = qcc_data.get("registered_capital")
            company.est_date = est_date
            company.company_status = qcc_data.get("company_status")
            company.business_scope = qcc_data.get("business_scope")
            company.address = qcc_data.get("address")
            company.industry_info = industry_info
            company.cached_at = now
            company.expires_at = expires_at

        return company
