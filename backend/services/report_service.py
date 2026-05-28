"""报告生成服务 — 聚合 12 个模块数据，生成 Markdown 尽调报告."""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.company import Company
from models.report import ReportSnapshot
from models.rating import RatingRecord
from models.task import Task

logger = logging.getLogger(__name__)


class ReportService:
    """报告生成服务"""

    def __init__(self) -> None:
        pass

    async def generate_report(
        self,
        db: AsyncSession,
        task_id: str,
        report_version: str = "v1",
        # 各模块数据（由调用方注入）
        company_info: dict[str, Any] | None = None,
        risk_data: dict[str, Any] | None = None,
        equity_data: dict[str, Any] | None = None,
        financial_data: dict[str, Any] | None = None,
        bank_data: dict[str, Any] | None = None,
        credit_data: dict[str, Any] | None = None,
        rating_data: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """根据任务ID聚合数据，生成 Markdown 格式尽调报告"""
        company_info = company_info or {}
        risk_data = risk_data or {}
        equity_data = equity_data or {}
        financial_data = financial_data or {}
        bank_data = bank_data or {}
        credit_data = credit_data or {}
        rating_data = rating_data or {}

        company_name = company_info.get("company_name", "未知企业")
        now = datetime.now(timezone.utc)

        # ── 构建报告内容 ──────────────────────────────
        sections: list[str] = []

        # 封面
        sections.append(self._section_cover(company_name, task_id, now))

        # 目录
        sections.append(self._section_toc())

        # 1. 尽调概述
        sections.append(self._section_overview(company_info, rating_data))

        # 2. 企业基本信息
        sections.append(self._section_company_info(company_info))

        # 3. 司法风险
        sections.append(self._section_risks(risk_data))

        # 4. 股权结构
        sections.append(self._section_equity(equity_data))

        # 5. 财务分析
        sections.append(self._section_financial(financial_data))

        # 6. 银行流水
        sections.append(self._section_bank(bank_data))

        # 7. 信贷征信
        sections.append(self._section_credit(credit_data))

        # 8. 六维评级
        sections.append(self._section_rating(rating_data))

        # 9. 尽调结论
        sections.append(self._section_conclusion(rating_data, company_name))

        report_content = "\n".join(sections)

        # ── 持久化 ───────────────────────────────────
        snapshot = ReportSnapshot(
            id=uuid4(),
            task_id=uuid4() if task_id is None else task_id,
            report_content=report_content,
            report_version=report_version,
            pdf_url=None,
        )
        db.add(snapshot)
        await db.commit()
        await db.refresh(snapshot)

        return {
            "report_id": str(snapshot.id),
            "task_id": str(snapshot.task_id),
            "company_name": company_name,
            "report_version": report_version,
            "report_content": report_content,
            "pdf_url": None,
            "generated_at": snapshot.generated_at.isoformat() if snapshot.generated_at else None,
        }

    # ── 报告章节生成 ─────────────────────────────────

    def _section_cover(self, company_name: str, task_id: str, now: datetime) -> str:
        return f"""# {company_name} 授信尽调报告

> **报告编号**: {task_id}
> **生成时间**: {now.strftime('%Y-%m-%d %H:%M')}
> **报告版本**: v1
> **机密等级**: 内部保密

---
"""

    def _section_toc(self) -> str:
        return """## 目录

1. [尽调概述](#尽调概述)
2. [企业基本信息](#企业基本信息)
3. [司法风险](#司法风险)
4. [股权结构](#股权结构)
5. [财务分析](#财务分析)
6. [银行流水](#银行流水)
7. [信贷征信](#信贷征信)
8. [六维评级](#六维评级)
9. [尽调结论](#尽调结论)

---
"""

    def _section_overview(self, company_info: dict, rating_data: dict) -> str:
        grade = rating_data.get("grade", "N/A")
        score = rating_data.get("final_score", "N/A")
        return f"""## 1. 尽调概述

- **企业名称**: {company_info.get('company_name', 'N/A')}
- **统一信用代码**: {company_info.get('unified_credit_code', 'N/A')}
- **综合评级**: **{grade}** (得分: {score})

本次尽调基于企查查工商数据、本行内部结算系统及客户上传文件，从司法风险、财务健康、征信状况、经营稳定性、股权结构、合规状况六个维度进行综合评估。

---
"""

    def _section_company_info(self, company_info: dict) -> str:
        return f"""## 2. 企业基本信息

| 项目 | 内容 |
|------|------|
| 企业名称 | {company_info.get('company_name', 'N/A')} |
| 统一信用代码 | {company_info.get('unified_credit_code', 'N/A')} |
| 法定代表人 | {company_info.get('legal_rep', 'N/A')} |
| 经营状态 | {company_info.get('company_status', 'N/A')} |
| 成立日期 | {company_info.get('establish_date', 'N/A')} |
| 注册资本 | {company_info.get('registered_capital', 'N/A')} |
| 所属行业 | {company_info.get('industry', 'N/A')} |
| 注册地址 | {company_info.get('address', 'N/A')} |

---
"""

    def _section_risks(self, risk_data: dict) -> str:
        lawsuits = risk_data.get("lawsuits", [])
        dishonest = risk_data.get("dishonest", [])
        penalties = risk_data.get("penalties", [])

        lawsuit_table = ""
        if lawsuits:
            lawsuit_table = "\n".join(
                f"| {ls.get('case_no', 'N/A')} | {ls.get('cause', 'N/A')} | {ls.get('court', 'N/A')} | {ls.get('amount', 'N/A')} |"
                for ls in lawsuits
            )
            lawsuit_table = "\n| 案号 | 案由 | 法院 | 金额 |\n|------|------|------|------|\n" + lawsuit_table
        else:
            lawsuit_table = "\n*未发现诉讼记录*"

        dishonest_text = f"\n共 {len(dishonest)} 条失信记录" if dishonest else "\n*未发现失信记录*"

        penalty_table = ""
        if penalties:
            penalty_table = "\n".join(
                f"| {p.get('penalty_no', 'N/A')} | {p.get('reason', 'N/A')} | {p.get('amount', 'N/A')} |"
                for p in penalties
            )
            penalty_table = "\n| 处罚文号 | 原因 | 金额 |\n|------|------|------|\n" + penalty_table
        else:
            penalty_table = "\n*未发现行政处罚*"

        return f"""## 3. 司法风险

### 3.1 诉讼记录
{lawsuit_table}

### 3.2 失信记录
{dishonest_text}

### 3.3 行政处罚
{penalty_table}

---
"""

    def _section_equity(self, equity_data: dict) -> str:
        shareholders = equity_data.get("shareholders", [])
        controller = equity_data.get("controller", {})

        sh_table = ""
        if shareholders:
            sh_table = "\n".join(
                f"| {s.get('name', 'N/A')} | {s.get('ratio', 'N/A')} | {s.get('amount', 'N/A')} |"
                for s in shareholders
            )
            sh_table = "\n| 股东名称 | 持股比例 | 出资金额 |\n|------|------|------|\n" + sh_table
        else:
            sh_table = "\n*无股东数据*"

        return f"""## 4. 股权结构

### 4.1 主要股东
{sh_table}

### 4.2 实际控制人
- **姓名**: {controller.get('name', 'N/A')}
- **控制比例**: {controller.get('control_ratio', 'N/A')}
- **控制路径**: {controller.get('control_path', 'N/A')}

---
"""

    def _section_financial(self, financial_data: dict) -> str:
        periods = financial_data.get("periods", [])

        if periods:
            rows = "\n".join(
                f"| {p.get('year', 'N/A')} | {p.get('revenue', 'N/A')} | {p.get('net_profit', 'N/A')} | {p.get('total_assets', 'N/A')} | {p.get('total_liabilities', 'N/A')} |"
                for p in periods
            )
            table = "\n| 年份 | 营业收入 | 净利润 | 总资产 | 总负债 |\n|------|------|------|------|------|\n" + rows
        else:
            table = "\n*无财务数据*"

        return f"""## 5. 财务分析

{table}

---
"""

    def _section_bank(self, bank_data: dict) -> str:
        statements = bank_data.get("statements", [])
        if statements:
            rows = "\n".join(
                f"| {s.get('period', 'N/A')} | {s.get('inflow', 'N/A')} | {s.get('outflow', 'N/A')} |"
                for s in statements
            )
            table = "\n| 期间 | 流入 | 流出 |\n|------|------|------|\n" + rows
        else:
            table = "\n*无银行流水数据*"

        return f"""## 6. 银行流水

{table}

---
"""

    def _section_credit(self, credit_data: dict) -> str:
        records = credit_data.get("records", [])
        if records:
            rows = "\n".join(
                f"| {r.get('loan_no', 'N/A')} | {r.get('amount', 'N/A')} | {r.get('status', 'N/A')} |"
                for r in records
            )
            table = "\n| 贷款编号 | 金额 | 状态 |\n|------|------|------|\n" + rows
        else:
            table = "\n*无信贷记录*"

        return f"""## 7. 信贷征信

{table}

---
"""

    def _section_rating(self, rating_data: dict) -> str:
        dims = rating_data.get("dimension_scores", [])
        if dims:
            rows = "\n".join(
                f"| {d['dimension']} | {d['score']} | {d['weight']}% | {d['weighted_score']} |"
                for d in dims
            )
            table = "\n| 维度 | 原始分 | 权重 | 加权分 |\n|------|------|------|------|\n" + rows
        else:
            table = "\n*无评级数据*"

        grade = rating_data.get("grade", "N/A")
        score = rating_data.get("final_score", "N/A")

        return f"""## 8. 六维评级

**综合评级: {grade} | 综合得分: {score}**

{table}

### 评分因子明细
{rating_data.get('rating_reason', 'N/A')}

---
"""

    def _section_conclusion(self, rating_data: dict, company_name: str) -> str:
        grade = rating_data.get("grade", "N/A")
        score = rating_data.get("final_score", "N/A")

        if grade == "A":
            recommendation = "建议授信 — 企业综合资质优秀，风险可控"
        elif grade == "B":
            recommendation = "有条件授信 — 建议审慎评估，适当控制授信额度"
        elif grade == "C":
            recommendation = "谨慎授信 — 存在一定风险，需加强担保措施"
        else:
            recommendation = "不建议授信 — 风险较高，建议拒绝"

        return f"""## 9. 尽调结论

- **企业名称**: {company_name}
- **综合评级**: {grade} (得分: {score})
- **授信建议**: {recommendation}

> **审批意见**:
>
> _（审批员填写）_

---
*本报告由银行授信尽调系统自动生成，仅供参考。*
"""

    async def list_reports(
        self, db: AsyncSession, task_id: str | None = None
    ) -> list[dict[str, Any]]:
        """获取报告列表"""
        stmt = select(ReportSnapshot)
        if task_id:
            stmt = stmt.where(ReportSnapshot.task_id == task_id)
        stmt = stmt.order_by(ReportSnapshot.generated_at.desc())
        result = await db.execute(stmt)
        reports = list(result.scalars().all())
        return [
            {
                "report_id": str(r.id),
                "task_id": str(r.task_id),
                "company_name": "",
                "report_version": r.report_version or "",
                "generated_at": r.generated_at.isoformat() if r.generated_at else None,
            }
            for r in reports
        ]

    async def get_report(
        self, db: AsyncSession, report_id: str
    ) -> dict[str, Any]:
        """获取报告详情"""
        stmt = select(ReportSnapshot).where(ReportSnapshot.id == report_id)
        result = await db.execute(stmt)
        report = result.scalar_one_or_none()
        if not report:
            raise ValueError(f"报告不存在: {report_id}")
        return {
            "report_id": str(report.id),
            "task_id": str(report.task_id),
            "company_name": "",
            "report_version": report.report_version or "",
            "report_content": report.report_content,
            "pdf_url": report.pdf_url,
            "generated_at": report.generated_at.isoformat() if report.generated_at else None,
        }
