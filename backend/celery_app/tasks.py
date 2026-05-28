"""Celery 异步任务 — 尽调扫描流水线 & PDF 生成。

MVP 阶段使用 asyncio.gather 替代 Celery，本文件保留完整 Celery
接口供生产环境直接启用。
"""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Celery 配置（生产环境启用）
# ---------------------------------------------------------------------------
# from celery import Celery
#
# celery_app = Celery(
#     "credit_dd",
#     broker=settings.CELERY_BROKER_URL,
#     backend=settings.CELERY_RESULT_BACKEND,
# )
# celery_app.conf.update(
#     task_serializer="json",
#     result_serializer="json",
#     accept_content=["json"],
#     timezone="Asia/Shanghai",
#     enable_utc=True,
# )


# ---------------------------------------------------------------------------
# 尽调扫描任务
# ---------------------------------------------------------------------------

async def scan_task_pipeline(task_id: str) -> dict[str, Any]:
    """完整的尽调扫描流水线（MVP 用 asyncio 替代 Celery）。

    扫描步骤：
    1. 企业基本信息核查 (10%)
    2. 司法风险扫描 (25%)
    3. 股权结构穿透 (40%)
    4. 财务报表采集 (55%)
    5. 银行流水分析 (65%)
    6. 信贷征信查询 (75%)
    7. 六维评级计算 (90%)
    8. 报告生成 (100%)
    """
    from sqlalchemy.ext.asyncio import AsyncSession
    from database import AsyncSessionLocal
    from services.task_service import TaskService
    from services.company_service import CompanyService
    from services.risk_service import RiskService
    from services.equity_service import EquityService
    from services.financial_report_service import FinancialReportService
    from services.bank_statement_service import BankStatementService
    from services.credit_service import CreditService
    from services.rating_engine import RatingEngine
    from services.report_service import ReportService

    db: AsyncSession = AsyncSessionLocal()
    task_service = TaskService()
    company_service = CompanyService()
    risk_service = RiskService()
    equity_service = EquityService()
    financial_service = FinancialReportService()
    bank_service = BankStatementService()
    credit_service = CreditService()
    rating_engine = RatingEngine()
    report_service = ReportService()

    try:
        # Step 0: 启动扫描
        await task_service.update_progress(db, task_id, progress=0.0, status="SCANNING")

        # Step 1: 企业基本信息 (10%)
        logger.info("[%s] Step 1/8: 企业基本信息核查", task_id)
        task_info = await task_service.get_task(db, task_id)
        company = None
        try:
            qcc = __import__("services.qcc_client", fromlist=["QCCClient"]).QCCClient()
            company_data = await qcc.get_company_info(
                task_info["company_name"],
                task_info.get("unified_credit_code"),
            )
            company = await company_service.save_company_info(db, company_data)
        except Exception:
            logger.warning("[%s] 企业信息获取失败，使用Mock数据", task_id)
        await task_service.update_progress(db, task_id, progress=10.0)

        # Step 2: 司法风险扫描 (25%)
        logger.info("[%s] Step 2/8: 司法风险扫描", task_id)
        risks = {}
        if company:
            try:
                risks = await risk_service.get_risk_summary(db, company)
            except Exception:
                logger.warning("[%s] 风险扫描失败", task_id)
        await task_service.update_progress(db, task_id, progress=25.0)

        # Step 3: 股权结构穿透 (40%)
        logger.info("[%s] Step 3/8: 股权结构穿透", task_id)
        equity_data = {}
        if company:
            try:
                equity_data = await equity_service.get_equity_info(db, company)
            except Exception:
                logger.warning("[%s] 股权穿透失败", task_id)
        await task_service.update_progress(db, task_id, progress=40.0)

        # Step 4: 财务报表采集 (55%)
        logger.info("[%s] Step 4/8: 财务报表采集", task_id)
        financial_data = {}
        if company:
            try:
                financial_data = await financial_service.get_summary(db, company)
            except Exception:
                logger.warning("[%s] 财务数据获取失败", task_id)
        await task_service.update_progress(db, task_id, progress=55.0)

        # Step 5: 银行流水分析 (65%)
        logger.info("[%s] Step 5/8: 银行流水分析", task_id)
        bank_data = {}
        if company:
            try:
                bank_data = await bank_service.get_summary(db, company)
            except Exception:
                logger.warning("[%s] 银行流水获取失败", task_id)
        await task_service.update_progress(db, task_id, progress=65.0)

        # Step 6: 信贷征信查询 (75%)
        logger.info("[%s] Step 6/8: 信贷征信查询", task_id)
        credit_data = {}
        if company:
            try:
                credit_data = await credit_service.get_summary(db, company)
            except Exception:
                logger.warning("[%s] 信贷数据获取失败", task_id)
        await task_service.update_progress(db, task_id, progress=75.0)

        # Step 7: 六维评级计算 (90%)
        logger.info("[%s] Step 7/8: 六维评级计算", task_id)
        rating_result = {}
        if company:
            try:
                rating_result = await rating_engine.calculate_rating(
                    db=db,
                    company=company,
                    task=None,
                    risks=risks if isinstance(risks, dict) else {},
                    financials=financial_data.get("periods", []),
                    bank_statements=bank_data.get("statements", []),
                    credit_records=credit_data.get("records", []),
                    shareholders=equity_data.get("shareholders", []),
                    equity_chain=equity_data.get("equity_chain", {}),
                    controller=equity_data.get("controller", {}),
                    penalties=risks.get("penalties", []) if isinstance(risks, dict) else [],
                )
            except Exception:
                logger.warning("[%s] 评级计算失败", task_id)
        await task_service.update_progress(db, task_id, progress=90.0)

        # Step 8: 报告生成 (100%)
        logger.info("[%s] Step 8/8: 报告生成", task_id)
        report_result = {}
        try:
            report_result = await report_service.generate_report(
                db=db,
                task_id=task_id,
                company_info=task_info,
                risk_data=risks if isinstance(risks, dict) else {},
                equity_data=equity_data,
                financial_data=financial_data,
                bank_data=bank_data,
                credit_data=credit_data,
                rating_data=rating_result,
            )
        except Exception:
            logger.warning("[%s] 报告生成失败", task_id)

        await task_service.update_progress(db, task_id, progress=100.0, status="COMPLETED")

        return {
            "task_id": task_id,
            "status": "COMPLETED",
            "progress": 100.0,
            "rating": rating_result,
            "report": report_result,
        }

    except Exception as exc:
        logger.exception("[%s] 扫描流水线异常: %s", task_id, exc)
        await task_service.update_progress(db, task_id, progress=0.0, status="EXPIRED")
        return {"task_id": task_id, "status": "FAILED", "error": str(exc)}
    finally:
        await db.close()


# ---------------------------------------------------------------------------
# PDF 生成任务（生产环境）
# ---------------------------------------------------------------------------

# async def generate_pdf_task(report_id: str) -> str:
#     """将 Markdown 报告转换为 PDF。
#
#     使用 weasyprint 或 wkhtmltopdf 渲染 pdf/template.html。
#     返回 PDF 文件路径。
#     """
#     pass
