"""工商数据服务 — 股东、高管、对外投资."""

from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from typing import Any

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from models.company import (
    Company,
    CompanyExecutive,
    CompanyInvestment,
    CompanyShareholder,
)
from services.qcc_client import QCCClient

logger = logging.getLogger(__name__)

# 缓存 TTL（秒）
SHAREHOLDING_TTL = 24 * 3600  # 24 小时


class ShareholdingService:
    """工商数据服务 — 股东、高管、对外投资."""

    def __init__(self) -> None:
        self._qcc = QCCClient()

    # ------------------------------------------------------------------
    # 公开方法
    # ------------------------------------------------------------------

    async def get_shareholders(
        self,
        db: AsyncSession,
        company: Company,
    ) -> list[CompanyShareholder]:
        """获取股东信息，含缓存."""
        records = await self._fetch_and_cache(
            db, company, "shareholders", CompanyShareholder
        )
        return records  # type: ignore[return-value]

    async def get_executives(
        self,
        db: AsyncSession,
        company: Company,
    ) -> list[CompanyExecutive]:
        """获取高管信息，含缓存."""
        records = await self._fetch_and_cache(
            db, company, "executives", CompanyExecutive
        )
        return records  # type: ignore[return-value]

    async def get_investments(
        self,
        db: AsyncSession,
        company: Company,
    ) -> list[CompanyInvestment]:
        """获取对外投资，含缓存."""
        records = await self._fetch_and_cache(
            db, company, "investments", CompanyInvestment
        )
        return records  # type: ignore[return-value]

    # ------------------------------------------------------------------
    # 内部方法
    # ------------------------------------------------------------------

    async def _fetch_and_cache(
        self,
        db: AsyncSession,
        company: Company,
        data_type: str,
        model_cls: type[CompanyShareholder] | type[CompanyExecutive] | type[CompanyInvestment],
    ) -> list[Any]:
        """通用缓存刷新逻辑：查本地 → 过期则调企查查 → 写回."""
        stmt = select(model_cls).where(model_cls.company_id == company.id)
        result = await db.execute(stmt)
        existing = result.scalars().all()

        # 简单策略：如果已有记录且最近 24h 内拉取过，直接返回
        now = datetime.now(timezone.utc)
        if existing:
            latest = max(existing, key=lambda r: r.fetched_at)  # type: ignore[attr-defined]
            if latest.fetched_at and (now - latest.fetched_at) < timedelta(  # type: ignore[operator]
                seconds=SHAREHOLDING_TTL
            ):
                return list(existing)

        # 调用企查查
        qcc_data: list[dict[str, Any]] = []
        if data_type == "shareholders":
            qcc_data = await self._qcc.get_shareholders(company.company_name)
        elif data_type == "executives":
            qcc_data = await self._qcc.get_executives(company.company_name)
        elif data_type == "investments":
            qcc_data = await self._qcc.get_investments(company.company_name)

        # 清除旧记录
        await db.execute(delete(model_cls).where(model_cls.company_id == company.id))

        # 写入新记录
        fetched_at = now
        for item in qcc_data:
            if data_type == "shareholders":
                record = CompanyShareholder(
                    company_id=company.id,
                    shareholder_name=item.get("name", ""),
                    shareholder_type=item.get("type"),
                    share_ratio=self._parse_percentage(item.get("ratio")),
                    subscribe_capital=item.get("amount"),
                    paid_in_capital=item.get("paid_in_amount"),
                    pledge_ratio=None,
                    fetched_at=fetched_at,
                )
            elif data_type == "executives":
                record = CompanyExecutive(
                    company_id=company.id,
                    name=item.get("name", ""),
                    position=item.get("title"),
                    fetched_at=fetched_at,
                )
            elif data_type == "investments":
                invest_date_raw = item.get("invest_date")
                invest_date = None
                if invest_date_raw:
                    try:
                        invest_date = datetime.strptime(invest_date_raw, "%Y-%m-%d")
                    except (ValueError, TypeError):
                        invest_date = None
                record = CompanyInvestment(
                    company_id=company.id,
                    invested_company=item.get("company_name", ""),
                    invest_ratio=self._parse_percentage(item.get("ratio")),
                    invest_amount=item.get("amount"),
                    invest_date=invest_date,
                    status=item.get("status"),
                    fetched_at=fetched_at,
                )
            else:
                continue
            db.add(record)

        await db.commit()

        # 重新查询并返回
        stmt = select(model_cls).where(model_cls.company_id == company.id)
        result = await db.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    def _parse_percentage(value: Any) -> float | None:
        """将百分比字符串 (如 "60.0%") 转为浮点数."""
        if value is None:
            return None
        if isinstance(value, (int, float)):
            return float(value)
        try:
            return float(str(value).rstrip("%"))
        except (ValueError, TypeError):
            return None
