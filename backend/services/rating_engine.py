"""六维评级引擎服务."""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.company import Company
from models.rating import Grade, RatingRecord
from models.task import Task

logger = logging.getLogger(__name__)

# ── 权重与阈值 ────────────────────────────────────────

DIMENSIONS = {
    "司法风险": 0.20,
    "财务健康": 0.20,
    "征信状况": 0.20,
    "经营稳定性": 0.15,
    "股权结构": 0.15,
    "合规状况": 0.10,
}

GRADE_THRESHOLDS = [
    (80, Grade.A),
    (60, Grade.B),
    (40, Grade.C),
    (0, Grade.D),
]


def _determine_grade(score: float) -> Grade:
    for threshold, grade in GRADE_THRESHOLDS:
        if score >= threshold:
            return grade
    return Grade.D


# ── 评分因子 ─────────────────────────────────────────


class _Factor:
    """单一评分因子"""

    @staticmethod
    def score_judicial(risks: dict[str, list[dict]]) -> tuple[float, list[dict]]:
        """司法风险评分 — 基准 100 分，按风险项扣分"""
        score = 100.0
        factors: list[dict] = []

        lawsuits = risks.get("lawsuits", [])
        for ls in lawsuits:
            deduction = 5.0
            factors.append({"item": f"诉讼: {ls.get('cause', '未知')}", "deduction": deduction})
            score -= deduction

        dishonest = risks.get("dishonest", [])
        for d in dishonest:
            deduction = 20.0
            factors.append({"item": "失信被执行人", "deduction": deduction})
            score -= deduction

        restrictions = risks.get("restrictions", [])
        for r in restrictions:
            deduction = 15.0
            factors.append({"item": "限高", "deduction": deduction})
            score -= deduction

        penalties = risks.get("penalties", [])
        for p in penalties:
            deduction = 5.0
            factors.append({"item": f"行政处罚: {p.get('reason', '未知')}", "deduction": deduction})
            score -= deduction

        return max(score, 0.0), factors

    @staticmethod
    def score_financial(financials: list[dict]) -> tuple[float, list[dict]]:
        """财务健康评分 — 基于资产规模、负债率、盈利能力"""
        score = 100.0
        factors: list[dict] = []

        if not financials:
            factors.append({"item": "无财务数据", "deduction": 30.0})
            return max(score - 30.0, 0.0), factors

        latest = financials[0]
        revenue = latest.get("revenue", "0元")
        net_profit = latest.get("net_profit", "0元")

        # 简化：有近两年数据的加分
        if len(financials) >= 2:
            factors.append({"item": "连续两年财报", "bonus": 5.0})
            score += 5.0

        # 简化：净亏损扣分
        if "亏损" in net_profit or "-" in str(net_profit):
            factors.append({"item": "净利润亏损", "deduction": 20.0})
            score -= 20.0

        return min(max(score, 0.0), 100.0), factors

    @staticmethod
    def score_credit(bank_statements: list[dict], credit_records: list[dict]) -> tuple[float, list[dict]]:
        """征信状况评分 — 基于银行流水与信贷记录"""
        score = 100.0
        factors: list[dict] = []

        if not bank_statements and not credit_records:
            factors.append({"item": "无征信数据", "deduction": 20.0})
            score -= 20.0

        for cr in credit_records:
            status = cr.get("status", "")
            if "逾期" in status or "违约" in status:
                deduction = 15.0
                factors.append({"item": f"信贷逾期/违约: {status}", "deduction": deduction})
                score -= deduction

        return min(max(score, 0.0), 100.0), factors

    @staticmethod
    def score_operation(company: Company, financials: list[dict]) -> tuple[float, list[dict]]:
        """经营稳定性评分 — 基于成立年限、变更记录"""
        score = 100.0
        factors: list[dict] = []

        # 成立年限加分
        if company.establish_date:
            years = (datetime.now(timezone.utc) - company.establish_date).days / 365.25
            if years >= 10:
                factors.append({"item": f"成立 {years:.0f} 年（≥10年）", "bonus": 10.0})
                score += 10.0
            elif years >= 5:
                factors.append({"item": f"成立 {years:.0f} 年（≥5年）", "bonus": 5.0})
                score += 5.0

        # 经营状态异常扣分
        if company.company_status and company.company_status != "存续":
            factors.append({"item": f"经营状态: {company.company_status}", "deduction": 30.0})
            score -= 30.0

        return min(max(score, 0.0), 100.0), factors

    @staticmethod
    def score_equity(
        shareholders: list[dict], equity_chain: dict, controller: dict
    ) -> tuple[float, list[dict]]:
        """股权结构评分 — 基于股权集中度、实控人"""
        score = 100.0
        factors: list[dict] = []

        if not shareholders:
            factors.append({"item": "无股东信息", "deduction": 15.0})
            score -= 15.0
        else:
            # 股权分散加分
            if len(shareholders) >= 5:
                factors.append({"item": "股东数量 ≥ 5", "bonus": 5.0})
                score += 5.0

        if controller and controller.get("name"):
            factors.append({"item": f"实控人: {controller['name']}", "bonus": 0})

        levels = equity_chain.get("levels", [])
        if len(levels) <= 3:
            factors.append({"item": "股权穿透层级 ≤ 3", "bonus": 5.0})
            score += 5.0

        return min(max(score, 0.0), 100.0), factors

    @staticmethod
    def score_compliance(penalties: list[dict], exceptions: list[dict]) -> tuple[float, list[dict]]:
        """合规状况评分 — 基于处罚与异常"""
        score = 100.0
        factors: list[dict] = []

        for p in penalties:
            deduction = 10.0
            factors.append({"item": f"行政处罚: {p.get('reason', '未知')}", "deduction": deduction})
            score -= deduction

        for e in exceptions:
            deduction = 10.0
            factors.append({"item": f"经营异常: {e.get('reason', '未知')}", "deduction": deduction})
            score -= deduction

        return max(score, 0.0), factors


# ── Service ──────────────────────────────────────────


class RatingEngine:
    """六维评级引擎"""

    def __init__(self) -> None:
        self._factor = _Factor()

    async def calculate_rating(
        self,
        db: AsyncSession,
        company: Company,
        task: Task | None = None,
        risks: dict[str, list[dict]] | None = None,
        financials: list[dict] | None = None,
        bank_statements: list[dict] | None = None,
        credit_records: list[dict] | None = None,
        shareholders: list[dict] | None = None,
        equity_chain: dict | None = None,
        controller: dict | None = None,
        penalties: list[dict] | None = None,
        exceptions: list[dict] | None = None,
    ) -> dict[str, Any]:
        """执行六维评级，返回评分结果并持久化"""
        risks = risks or {}
        financials = financials or []
        bank_statements = bank_statements or []
        credit_records = credit_records or []
        shareholders = shareholders or []
        equity_chain = equity_chain or {}
        controller = controller or {}
        penalties = penalties or []
        exceptions = exceptions or []

        # 1. 六维评分
        judicial_score, judicial_factors = self._factor.score_judicial(risks)
        financial_score, financial_factors = self._factor.score_financial(financials)
        credit_score, credit_factors = self._factor.score_credit(bank_statements, credit_records)
        operation_score, operation_factors = self._factor.score_operation(company, financials)
        equity_score, equity_factors = self._factor.score_equity(shareholders, equity_chain, controller)
        compliance_score, compliance_scores_factors = self._factor.score_compliance(penalties, exceptions)

        scores = {
            "司法风险": judicial_score,
            "财务健康": financial_score,
            "征信状况": credit_score,
            "经营稳定性": operation_score,
            "股权结构": equity_score,
            "合规状况": compliance_score,
        }

        # 2. 加权总分
        total_score = sum(
            scores[dim] * weight for dim, weight in DIMENSIONS.items()
        )
        total_score = round(total_score, 2)
        grade = _determine_grade(total_score)

        # 3. 维度明细
        dimension_scores = []
        factor_maps = {
            "司法风险": judicial_factors,
            "财务健康": financial_factors,
            "征信状况": credit_factors,
            "经营稳定性": operation_factors,
            "股权结构": equity_factors,
            "合规状况": compliance_scores_factors,
        }
        for dim, weight in DIMENSIONS.items():
            dimension_scores.append({
                "dimension": dim,
                "score": scores[dim],
                "weight": weight * 100,
                "weighted_score": round(scores[dim] * weight, 2),
                "factors": factor_maps[dim],
            })

        # 4. 持久化
        rating_record = RatingRecord(
            id=uuid4(),
            task_id=task.id if task else uuid4(),
            grade=grade,
            total_score=total_score,
            judicial_score=judicial_score,
            financial_score=financial_score,
            credit_score=credit_score,
            operation_score=operation_score,
            equity_score=equity_score,
            compliance_score=compliance_score,
            detail_breakdown={dim: factor_maps[dim] for dim in DIMENSIONS},
        )
        db.add(rating_record)
        await db.commit()
        await db.refresh(rating_record)

        return {
            "rating_id": str(rating_record.id),
            "task_id": str(rating_record.task_id),
            "company_id": str(company.id),
            "company_name": company.company_name,
            "judicial_score": judicial_score,
            "financial_score": financial_score,
            "credit_score": credit_score,
            "operation_score": operation_score,
            "equity_score": equity_score,
            "compliance_score": compliance_score,
            "final_score": total_score,
            "grade": grade.value,
            "dimension_scores": dimension_scores,
            "rating_reason": self._generate_reason(factor_maps),
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }

    def _generate_reason(self, factor_maps: dict[str, list[dict]]) -> str:
        """根据评分因子生成评级原因摘要"""
        reasons: list[str] = []
        for dim, factors in factor_maps.items():
            deductions = [f for f in factors if "deduction" in f and f["deduction"] > 0]
            if deductions:
                items = ", ".join(f["item"] for f in deductions[:3])
                reasons.append(f"[{dim}] {items}")
        return "; ".join(reasons) if reasons else "各项指标正常"

    async def get_rating_history(
        self, db: AsyncSession, company_id: str
    ) -> list[dict[str, Any]]:
        """获取企业评级历史"""
        stmt = (
            select(RatingRecord)
            .where(RatingRecord.task_id.is_not(None))
            .order_by(RatingRecord.rated_at.desc())
        )
        result = await db.execute(stmt)
        records = list(result.scalars().all())
        return [
            {
                "rating_id": str(r.id),
                "company_name": "",  # 需要关联查询，简化处理
                "final_score": r.total_score,
                "grade": r.grade.value,
                "generated_at": r.rated_at.isoformat() if r.rated_at else None,
            }
            for r in records
        ]
