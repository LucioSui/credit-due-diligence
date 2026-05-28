"""Bank statement analysis service (3.6)."""

import logging
import random
import uuid
from datetime import date, datetime, timedelta
from typing import Any, Optional

from fastapi import HTTPException, UploadFile
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from models.bank_statement import BankStatement, BankStatementParseStatus, StatementSource
from storage.file_storage import FileStorage
from services.file_parser import FileParser

logger = logging.getLogger(__name__)

ERR_FILE_UPLOAD_FAILED = 5001
ERR_FILE_PARSE_FAILED = 5002


class BankStatementService:
    """Business logic for bank statements."""

    async def fetch_internal(
        self,
        db: AsyncSession,
        company_id: str,
        account_no: str,
        start_date: date,
        end_date: date,
        uploaded_by: str,
    ) -> BankStatement:
        """Pull bank statement from internal system — MVP uses simulated data."""
        simulated = self._generate_simulated_statement(
            account_no=account_no,
            start_date=start_date,
            end_date=end_date,
        )

        stmt_record = BankStatement(
            company_id=company_id,
            account_no=account_no,
            bank_name=simulated["bank_name"],
            statement_source=StatementSource.INTERNAL,
            start_date=start_date,
            end_date=end_date,
            total_inflow=simulated["total_inflow"],
            total_outflow=simulated["total_outflow"],
            avg_daily_balance=simulated["avg_daily_balance"],
            ending_balance=simulated["ending_balance"],
            transaction_count=simulated["transaction_count"],
            transaction_summary=simulated["transaction_summary"],
            anomaly_flags=simulated["anomaly_flags"],
            parse_status=BankStatementParseStatus.PARSED,
            uploaded_by=uploaded_by,
            parsed_at=datetime.now(),
        )
        db.add(stmt_record)
        await db.commit()
        await db.refresh(stmt_record)
        return stmt_record

    async def upload_statement(
        self,
        db: AsyncSession,
        company_id: str,
        file: UploadFile,
        uploaded_by: str,
    ) -> BankStatement:
        """Upload a bank statement file and create a DB record."""
        content = await file.read()
        file_size = len(content)

        FileStorage.validate_file(file.filename or "unknown", "bank_statement", file_size)

        save_path = FileStorage.get_upload_path(
            company_id, "bank_statement", file.filename or "statement"
        )
        await FileStorage.save_file(content, save_path)

        ext = FileStorage.get_file_source_from_filename(file.filename or "")

        stmt_record = BankStatement(
            company_id=company_id,
            account_no=None,
            bank_name=None,
            statement_source=StatementSource.UPLOADED,
            file_name=file.filename,
            file_path=save_path,
            parse_status=BankStatementParseStatus.PENDING,
            uploaded_by=uploaded_by,
        )
        db.add(stmt_record)
        await db.commit()
        await db.refresh(stmt_record)
        return stmt_record

    async def list_statements(
        self,
        db: AsyncSession,
        company_id: str,
    ) -> list[BankStatement]:
        """Return all bank statements for a company."""
        stmt = (
            select(BankStatement)
            .where(BankStatement.company_id == company_id)
            .order_by(BankStatement.uploaded_at.desc())
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def get_statement(
        self,
        db: AsyncSession,
        statement_id: str,
    ) -> BankStatement:
        """Fetch a single bank statement by id."""
        stmt = select(BankStatement).where(BankStatement.id == statement_id)
        result = await db.execute(stmt)
        record = result.scalar_one_or_none()
        if not record:
            raise HTTPException(status_code=404, detail="银行流水记录不存在")

        # Auto-parse if pending and file exists
        if record.parse_status == BankStatementParseStatus.PENDING and record.file_path:
            await self._auto_parse(db, record)

        return record

    async def get_summary(
        self,
        db: AsyncSession,
        company_id: str,
    ) -> dict[str, Any]:
        """Aggregate summary across all accounts for a company."""
        stmt = select(BankStatement).where(BankStatement.company_id == company_id)
        result = await db.execute(stmt)
        records = list(result.scalars().all())

        total_inflow = sum(r.total_inflow or 0 for r in records)
        total_outflow = sum(r.total_outflow or 0 for r in records)
        total_ending = sum(r.ending_balance or 0 for r in records)

        accounts = []
        for r in records:
            accounts.append({
                "id": str(r.id),
                "account_no": r.account_no,
                "bank_name": r.bank_name,
                "statement_source": r.statement_source.value,
                "total_inflow": r.total_inflow,
                "total_outflow": r.total_outflow,
                "ending_balance": r.ending_balance,
            })

        return {
            "total_accounts": len(records),
            "total_inflow": round(total_inflow, 2),
            "total_outflow": round(total_outflow, 2),
            "total_ending_balance": round(total_ending, 2),
            "accounts": accounts,
        }

    async def delete_statement(
        self,
        db: AsyncSession,
        statement_id: str,
    ) -> None:
        """Delete a bank statement and its file."""
        record = await self.get_statement(db, statement_id)
        if record.file_path:
            await FileStorage.delete_file(record.file_path)
        await db.delete(record)
        await db.commit()

    # ── Internal helpers ─────────────────────────────────────────────────

    async def _auto_parse(self, db: AsyncSession, record: BankStatement) -> None:
        """Parse an uploaded statement file and update the record."""
        if not record.file_path:
            return
        parser = FileParser()
        try:
            file_type = (
                "excel"
                if record.file_name and record.file_name.endswith(".xlsx")
                else "pdf"
            )
            parsed = await parser.parse_bank_statement(record.file_path, file_type)
            record.total_inflow = parsed.get("total_inflow")
            record.total_outflow = parsed.get("total_outflow")
            record.avg_daily_balance = parsed.get("avg_daily_balance")
            record.ending_balance = parsed.get("ending_balance")
            record.transaction_count = parsed.get("transaction_count")
            record.transaction_summary = parsed.get("transaction_summary")
            record.anomaly_flags = parsed.get("anomaly_flags")
            record.parse_status = BankStatementParseStatus.PARSED
            record.parsed_at = datetime.now()
        except Exception as exc:
            logger.exception("Failed to parse bank statement %s", record.id)
            record.parse_status = BankStatementParseStatus.FAILED
            record.anomaly_flags = {"parse_error": str(exc)}
        await db.commit()
        await db.refresh(record)

    # ── Simulated data generation ────────────────────────────────────────

    @staticmethod
    def _generate_simulated_statement(
        account_no: str,
        start_date: date,
        end_date: date,
    ) -> dict[str, Any]:
        """Generate 3-month simulated bank statement with 50+ transactions."""
        random.seed(42)  # Reproducible

        bank_names = ["工商银行", "建设银行", "农业银行", "中国银行"]
        bank_name = random.choice(bank_names)

        categories = [
            ("货款收入", "inflow", (50000, 500000)),
            ("服务收入", "inflow", (10000, 200000)),
            ("利息收入", "inflow", (100, 5000)),
            ("工资支出", "outflow", (20000, 100000)),
            ("租金支出", "outflow", (10000, 50000)),
            ("采购付款", "outflow", (30000, 300000)),
            ("税费缴纳", "outflow", (5000, 30000)),
            ("水电费", "outflow", (500, 5000)),
            ("差旅报销", "outflow", (1000, 10000)),
        ]

        transactions: list[dict] = []
        current_balance = 500000.0
        total_inflow = 0.0
        total_outflow = 0.0
        balances: list[float] = []

        delta = (end_date - start_date).days
        current_date = start_date

        for _ in range(60):
            cat, flow_type, (low, high) = random.choice(categories)
            amount = round(random.uniform(low, high), 2)

            if flow_type == "inflow":
                current_balance += amount
                total_inflow += amount
            else:
                current_balance -= amount
                total_outflow += amount

            transactions.append({
                "date": current_date.isoformat(),
                "summary": cat,
                "amount": amount,
                "flow_type": flow_type,
                "balance": round(current_balance, 2),
            })
            balances.append(current_balance)

            days_gap = random.randint(1, max(1, delta // 60))
            current_date += timedelta(days=days_gap)
            if current_date > end_date:
                current_date = end_date

        # Inject a few anomalies
        # 1. Large transfer (anomaly)
        large_amount = round(random.uniform(800000, 1500000), 2)
        current_balance += large_amount
        total_inflow += large_amount
        transactions.append({
            "date": end_date.isoformat(),
            "summary": "大额转账收入（异常）",
            "amount": large_amount,
            "flow_type": "inflow",
            "balance": round(current_balance, 2),
        })
        balances.append(current_balance)

        # 2. Frequent small outflows
        for i in range(5):
            small = round(random.uniform(100, 500), 2)
            current_balance -= small
            total_outflow += small
            transactions.append({
                "date": end_date.isoformat(),
                "summary": f"频繁小额支出-{i+1}",
                "amount": small,
                "flow_type": "outflow",
                "balance": round(current_balance, 2),
            })
            balances.append(current_balance)

        # Sort by date
        transactions.sort(key=lambda t: t["date"])

        # Monthly aggregation
        monthly_inflow: dict[str, float] = {}
        monthly_outflow: dict[str, float] = {}
        for tx in transactions:
            month = tx["date"][:7]
            if tx["flow_type"] == "inflow":
                monthly_inflow[month] = monthly_inflow.get(month, 0) + tx["amount"]
            else:
                monthly_outflow[month] = monthly_outflow.get(month, 0) + tx["amount"]

        anomaly_flags: dict[str, Any] = {
            "large_transfer": {
                "description": "发现单笔超大额转入",
                "amount": large_amount,
                "date": end_date.isoformat(),
            },
            "frequent_small_outflow": {
                "description": "短期内频繁小额支出",
                "count": 5,
            },
        }

        return {
            "bank_name": bank_name,
            "total_inflow": round(total_inflow, 2),
            "total_outflow": round(total_outflow, 2),
            "avg_daily_balance": round(sum(balances) / len(balances), 2) if balances else 0,
            "ending_balance": round(current_balance, 2),
            "transaction_count": len(transactions),
            "transaction_summary": {
                "monthly_inflow": monthly_inflow,
                "monthly_outflow": monthly_outflow,
                "transactions": transactions,
            },
            "anomaly_flags": anomaly_flags,
        }
