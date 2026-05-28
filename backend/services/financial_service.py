"""工商财报数据服务(3.4) — 来自企查查 API."""

from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from typing import Any

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from models.company import Company
from models.company_financial import CompanyFinancial

logger = logging.getLogger(__name__)

# 缓存 TTL（秒）
FINANCIAL_TTL = 72 * 3600  # 72 小时


class FinancialService:
    """工商财报数据服务(3.4) — 来自企查查 API."""

    def __init__(self) -> None:
        self._qcc = __import__(
            "services.qcc_client", fromlist=["QCCClient"]
        ).QCCClient()

    # ------------------------------------------------------------------
    # 公开方法
    # ------------------------------------------------------------------

    async def get_financials(
        self,
        db: AsyncSession,
        company: Company,
        year: str | None = None,
    ) -> list[CompanyFinancial]:
        """获取工商财报数据，含缓存（TTL 72h）。

        Args:
            db: 数据库会话。
            company: 目标企业。
            year: 可选，指定年份（如 "2023"）则过滤。
        """
        await self._ensure_fresh_financials(db, company)

        stmt = (
            select(CompanyFinancial)
            .where(CompanyFinancial.company_id == company.id)
            .order_by(CompanyFinancial.year.desc())
        )
        if year is not None:
            try:
                year_int = int(year)
                stmt = stmt.where(CompanyFinancial.year == year_int)
            except ValueError:
                pass
        result = await db.execute(stmt)
        return list(result.scalars().all())

    # ------------------------------------------------------------------
    # 内部方法
    # ------------------------------------------------------------------

    async def _ensure_fresh_financials(
        self,
        db: AsyncSession,
        company: Company,
    ) -> None:
        """确保财报数据是新鲜的，过期则从企查查重新拉取."""
        stmt = select(CompanyFinancial).where(
            CompanyFinancial.company_id == company.id
        )
        result = await db.execute(stmt)
        existing = result.scalars().all()

        now = datetime.now(timezone.utc)
        if existing:
            latest = max(existing, key=lambda r: r.fetched_at)
            if latest.fetched_at and (now - latest.fetched_at) < timedelta(
                seconds=FINANCIAL_TTL
            ):
                return

        await self._fetch_and_cache_financials(db, company)

    async def _fetch_and_cache_financials(
        self,
        db: AsyncSession,
        company: Company,
    ) -> None:
        """从企查查拉取财报数据并缓存."""
        from services.qcc_client import QCCClient

        qcc = QCCClient()
        financial_data = await qcc.get_financials(company.company_name)

        # 清除旧记录
        await db.execute(
            delete(CompanyFinancial).where(
                CompanyFinancial.company_id == company.id
            )
        )

        fetched_at = datetime.now(timezone.utc)

        for item in financial_data:
            balance_sheet = {
                "total_assets": item.get("total_assets"),
                "total_liabilities": item.get("total_liabilities"),
                "net_assets": item.get("net_assets"),
            }
            income_statement = {
                "revenue": item.get("revenue"),
                "net_profit": item.get("net_profit"),
                "total_revenue": item.get("total_revenue"),
            }
            cash_flow = None  # 模拟数据暂无现金流明细
            key_indicators = {
                "asset_liability_ratio": self._calc_ratio(
                    item.get("total_liabilities"), item.get("total_assets")
                ),
                "roe": self._calc_ratio(
                    item.get("net_profit"), item.get("net_assets")
                ),
            }

            try:
                fy = int(item.get("year", 0))
            except (ValueError, TypeError):
                fy = 0

            record = CompanyFinancial(
                company_id=company.id,
                year=fy,
                balance_sheet=balance_sheet,
                income_statement=income_statement,
                cash_flow=cash_flow,
                key_indicators=key_indicators,
                fetched_at=fetched_at,
            )
            db.add(record)

        await db.commit()

    @staticmethod
    def _calc_ratio(numerator: Any, denominator: Any) -> str | None:
        """从字符串如 '100万元' 中提取数字并计算比率百分比."""
        if numerator is None or denominator is None:
            return None
        try:
            num = float("".join(ch for ch in str(numerator) if ch.isdigit() or ch == "."))
            den = float("".join(ch for ch in str(denominator) if ch.isdigit() or ch == "."))
            if den == 0:
                return None
            return f"{(num / den) * 100:.2f}%"
        except (ValueError, TypeError):
            return None
