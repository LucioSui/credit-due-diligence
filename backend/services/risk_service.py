"""风险扫描服务 — 诉讼、失信、限高、处罚."""

from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from typing import Any

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from models.company import Company
from models.company_risk import CompanyRisk, RiskLevel, RiskType

logger = logging.getLogger(__name__)

# 缓存 TTL（秒）
RISK_TTL = 12 * 3600  # 12 小时


class RiskService:
    """风险扫描服务 — 诉讼、失信、限高、处罚."""

    def __init__(self) -> None:
        self._qcc = __import__(
            "services.qcc_client", fromlist=["QCCClient"]
        ).QCCClient()

    # ------------------------------------------------------------------
    # 公开方法
    # ------------------------------------------------------------------

    async def get_risk_summary(
        self,
        db: AsyncSession,
        company: Company,
    ) -> dict[str, Any]:
        """获取全部风险汇总，含缓存（TTL 12h）."""
        await self._ensure_fresh_risks(db, company)

        stmt = select(CompanyRisk).where(CompanyRisk.company_id == company.id)
        result = await db.execute(stmt)
        all_risks = list(result.scalars().all())

        lawsuits = [r for r in all_risks if r.risk_type == RiskType.LAWSUIT]
        dishonest = [r for r in all_risks if r.risk_type == RiskType.DISHONEST]
        restrictions = [r for r in all_risks if r.risk_type == RiskType.RESTRICTION]
        penalties = [r for r in all_risks if r.risk_type == RiskType.PENALTY]

        high_count = sum(1 for r in all_risks if r.risk_level == RiskLevel.HIGH)
        medium_count = sum(1 for r in all_risks if r.risk_level == RiskLevel.MEDIUM)
        low_count = sum(1 for r in all_risks if r.risk_level == RiskLevel.LOW)

        def _to_dict(risk: CompanyRisk) -> dict[str, Any]:
            return {
                "id": str(risk.id),
                "risk_type": risk.risk_type.value,
                "risk_level": risk.risk_level.value,
                "risk_detail": risk.risk_detail,
                "detected_at": risk.detected_at.isoformat() if risk.detected_at else None,
            }

        return {
            "total_risks": len(all_risks),
            "high_count": high_count,
            "medium_count": medium_count,
            "low_count": low_count,
            "lawsuits": [_to_dict(r) for r in lawsuits],
            "dishonest": [_to_dict(r) for r in dishonest],
            "restrictions": [_to_dict(r) for r in restrictions],
            "penalties": [_to_dict(r) for r in penalties],
        }

    async def get_risks_by_type(
        self,
        db: AsyncSession,
        company: Company,
        risk_type: str,
    ) -> list[CompanyRisk]:
        """按类型获取风险（lawsuit/dishonest/restriction/penalty）."""
        await self._ensure_fresh_risks(db, company)

        try:
            rt = RiskType(risk_type)
        except ValueError:
            return []

        stmt = (
            select(CompanyRisk)
            .where(
                CompanyRisk.company_id == company.id,
                CompanyRisk.risk_type == rt,
            )
            .order_by(CompanyRisk.detected_at.desc())
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())

    # ------------------------------------------------------------------
    # 内部方法
    # ------------------------------------------------------------------

    async def _ensure_fresh_risks(
        self,
        db: AsyncSession,
        company: Company,
    ) -> None:
        """确保风险数据是新鲜的，过期则从企查查重新拉取."""
        stmt = select(CompanyRisk).where(CompanyRisk.company_id == company.id)
        result = await db.execute(stmt)
        existing = result.scalars().all()

        now = datetime.now(timezone.utc)
        if existing:
            latest = max(existing, key=lambda r: r.detected_at)
            if latest.detected_at and (now - latest.detected_at) < timedelta(
                seconds=RISK_TTL
            ):
                return

        await self._fetch_and_cache_risks(db, company)

    async def _fetch_and_cache_risks(
        self,
        db: AsyncSession,
        company: Company,
    ) -> None:
        """从企查查拉取全部风险数据并缓存."""
        from services.qcc_client import QCCClient

        qcc = QCCClient()
        risks_data = await qcc.get_risks(company.company_name)

        # 清除旧记录
        await db.execute(
            delete(CompanyRisk).where(CompanyRisk.company_id == company.id)
        )

        fetched_at = datetime.now(timezone.utc)

        # 失信、限高 → 高风险
        for item in risks_data.get("dishonest", []):
            db.add(
                CompanyRisk(
                    company_id=company.id,
                    risk_type=RiskType.DISHONEST,
                    risk_level=RiskLevel.HIGH,
                    risk_detail=item,
                    detected_at=fetched_at,
                )
            )

        for item in risks_data.get("restrictions", []):
            db.add(
                CompanyRisk(
                    company_id=company.id,
                    risk_type=RiskType.RESTRICTION,
                    risk_level=RiskLevel.HIGH,
                    risk_detail=item,
                    detected_at=fetched_at,
                )
            )

        # 重大诉讼 → 中风险 (金额 >= 100 万元)
        for item in risks_data.get("lawsuits", []):
            level = self._classify_lawsuit(item)
            db.add(
                CompanyRisk(
                    company_id=company.id,
                    risk_type=RiskType.LAWSUIT,
                    risk_level=level,
                    risk_detail=item,
                    detected_at=fetched_at,
                )
            )

        # 一般行政处罚 → 低风险
        for item in risks_data.get("penalties", []):
            db.add(
                CompanyRisk(
                    company_id=company.id,
                    risk_type=RiskType.PENALTY,
                    risk_level=RiskLevel.LOW,
                    risk_detail=item,
                    detected_at=fetched_at,
                )
            )

        await db.commit()

    @staticmethod
    def _classify_lawsuit(item: dict[str, Any]) -> RiskLevel:
        """根据诉讼金额判断风险等级."""
        amount_str = item.get("amount", "")
        if not amount_str:
            return RiskLevel.MEDIUM
        try:
            # 简化：提取数字，单位万元
            num = "".join(ch for ch in str(amount_str) if ch.isdigit() or ch == ".")
            amount = float(num)
            if amount >= 100:
                return RiskLevel.HIGH
        except (ValueError, TypeError):
            pass
        return RiskLevel.MEDIUM
