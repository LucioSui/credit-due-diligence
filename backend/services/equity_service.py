"""股权穿透服务 — UBO、实控人、穿透链."""

from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from typing import Any

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from models.company import Company
from models.equity import ChainType, EquityChain

logger = logging.getLogger(__name__)

# 缓存 TTL（秒）
EQUITY_TTL = 24 * 3600  # 24 小时
# 股权穿透最大深度
MAX_CHAIN_DEPTH = 5


class EquityService:
    """股权穿透服务 — UBO、实控人、穿透链."""

    def __init__(self) -> None:
        self._qcc = __import__(
            "services.qcc_client", fromlist=["QCCClient"]
        ).QCCClient()

    # ------------------------------------------------------------------
    # 公开方法
    # ------------------------------------------------------------------

    async def get_equity_chain(
        self,
        db: AsyncSession,
        company: Company,
    ) -> dict[str, Any]:
        """获取完整股权穿透信息.

        Returns:
            {"upward_chains": [...], "downward_chains": [...], "ubos": [...], "controller": {...}}
        """
        await self._ensure_fresh_equity(db, company)

        # 查询穿透链
        stmt = (
            select(EquityChain)
            .where(EquityChain.company_id == company.id)
            .order_by(EquityChain.chain_type, EquityChain.chain_depth)
        )
        result = await db.execute(stmt)
        chains = list(result.scalars().all())

        upward_chains = [c for c in chains if c.chain_type == ChainType.UPWARD]
        downward_chains = [c for c in chains if c.chain_type == ChainType.DOWNWARD]

        # UBO 存储在 chain_type=UBO 的链数据中
        ubo_chains = [c for c in chains if c.chain_type == ChainType.UBO]
        ubos = []
        for uc in ubo_chains:
            if uc.chain_data:
                ubos.extend(uc.chain_data.get("owners", []))

        # 实控人也存储在 UBO 链数据中
        controller_data = {}
        for uc in ubo_chains:
            if uc.chain_data and uc.chain_data.get("controller"):
                controller_data = uc.chain_data["controller"]
                break

        def _chain_to_dict(chain: EquityChain) -> dict[str, Any]:
            return {
                "id": str(chain.id),
                "chain_type": chain.chain_type.value,
                "chain_depth": chain.chain_depth,
                "chain_data": chain.chain_data,
            }

        return {
            "upward_chains": [_chain_to_dict(c) for c in upward_chains],
            "downward_chains": [_chain_to_dict(c) for c in downward_chains],
            "ubos": ubos,
            "controller": controller_data if controller_data else None,
        }

    async def get_ubos(
        self,
        db: AsyncSession,
        company: Company,
    ) -> list[dict[str, Any]]:
        """获取受益所有人."""
        await self._ensure_fresh_equity(db, company)

        stmt = (
            select(EquityChain)
            .where(
                EquityChain.company_id == company.id,
                EquityChain.chain_type == ChainType.UBO,
            )
        )
        result = await db.execute(stmt)
        ubo_chains = list(result.scalars().all())

        ubos = []
        for uc in ubo_chains:
            if uc.chain_data:
                ubos.extend(uc.chain_data.get("owners", []))
        return ubos

    async def get_controller(
        self,
        db: AsyncSession,
        company: Company,
    ) -> dict[str, Any]:
        """获取实际控制人."""
        await self._ensure_fresh_equity(db, company)

        stmt = (
            select(EquityChain)
            .where(
                EquityChain.company_id == company.id,
                EquityChain.chain_type == ChainType.UBO,
            )
        )
        result = await db.execute(stmt)
        ubo_chains = list(result.scalars().all())

        for uc in ubo_chains:
            if uc.chain_data and uc.chain_data.get("controller"):
                return uc.chain_data["controller"]

        return {}

    # ------------------------------------------------------------------
    # 内部方法
    # ------------------------------------------------------------------

    async def _ensure_fresh_equity(
        self,
        db: AsyncSession,
        company: Company,
    ) -> None:
        """确保股权穿透数据是新鲜的，过期则从企查查重新拉取."""
        stmt = select(EquityChain).where(EquityChain.company_id == company.id)
        result = await db.execute(stmt)
        existing = result.scalars().all()

        now = datetime.now(timezone.utc)
        if existing:
            latest = max(existing, key=lambda r: r.fetched_at)
            if latest.fetched_at and (now - latest.fetched_at) < timedelta(
                seconds=EQUITY_TTL
            ):
                return

        await self._fetch_and_cache_equity(db, company)

    async def _fetch_and_cache_equity(
        self,
        db: AsyncSession,
        company: Company,
    ) -> None:
        """从企查查拉取股权穿透数据并缓存（TTL 24h）."""
        from services.qcc_client import QCCClient

        qcc = QCCClient()

        # 1. 股权穿透路径
        equity_data = await qcc.get_equity_chain(company.company_name)
        # 2. 实际控制人
        controller_data = await qcc.get_actual_controller(company.company_name)
        # 3. 受益所有人
        ubo_data = await qcc.get_beneficial_owners(company.company_name)

        # 清除旧记录
        await db.execute(
            delete(EquityChain).where(EquityChain.company_id == company.id)
        )

        fetched_at = datetime.now(timezone.utc)

        # 存储向上穿透链
        levels = equity_data.get("levels", [])
        chain_depth = min(len(levels) - 1, MAX_CHAIN_DEPTH)
        if levels:
            db.add(
                EquityChain(
                    company_id=company.id,
                    chain_type=ChainType.UPWARD,
                    chain_depth=chain_depth,
                    chain_data={"levels": levels, "chain_type": equity_data.get("chain_type")},
                    fetched_at=fetched_at,
                )
            )

        # 构建 UBO 记录
        ubo_owners = []
        for ubo_item in ubo_data:
            owner = {
                "name": ubo_item.get("name", ""),
                "id_type": ubo_item.get("id_type"),
                "id_number": ubo_item.get("id_number"),
                "ownership_percentage": self._parse_percentage(ubo_item.get("benefit_ratio")),
                "control_path": [],
            }
            # 从实控人信息中补充 control_path
            if controller_data.get("control_path"):
                owner["control_path"] = controller_data["control_path"].split(" → ")
            ubo_owners.append(owner)

        controller_response = None
        if controller_data.get("name"):
            control_ratio_str = controller_data.get("control_ratio")
            control_path = controller_data.get("control_path", "")
            control_path_list = control_path.split(" → ") if control_path else []
            controller_response = {
                "name": controller_data["name"],
                "control_type": "direct" if chain_depth <= 1 else "indirect",
                "control_percentage": self._parse_percentage(control_ratio_str),
                "control_path": control_path_list,
            }

        if ubo_owners or controller_response:
            db.add(
                EquityChain(
                    company_id=company.id,
                    chain_type=ChainType.UBO,
                    chain_depth=0,
                    chain_data={
                        "owners": ubo_owners,
                        "controller": controller_response,
                    },
                    fetched_at=fetched_at,
                )
            )

        await db.commit()

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
