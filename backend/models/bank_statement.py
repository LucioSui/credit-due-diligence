"""Bank statements model (银行流水)."""

import enum
import uuid
from datetime import datetime, date as date_type

from sqlalchemy import (
    Column,
    DateTime,
    Date,
    Enum,
    ForeignKey,
    JSON,
    Integer,
    String,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .user import Base


class StatementSource(str, enum.Enum):
    INTERNAL = "internal"
    UPLOADED = "uploaded"


class BankStatementParseStatus(str, enum.Enum):
    PENDING = "pending"
    PARSED = "parsed"
    FAILED = "failed"


class BankStatement(Base):
    __tablename__ = "bank_statements"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    company_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("companies.id"), nullable=False
    )
    account_no: Mapped[str | None] = mapped_column(String(64), nullable=True)
    bank_name: Mapped[str | None] = mapped_column(String(128), nullable=True)
    statement_source: Mapped[StatementSource] = mapped_column(
        Enum(StatementSource), nullable=False
    )
    file_name: Mapped[str | None] = mapped_column(String(256), nullable=True)
    file_path: Mapped[str | None] = mapped_column(String(512), nullable=True)
    start_date: Mapped[date_type | None] = mapped_column(Date, nullable=True)
    end_date: Mapped[date_type | None] = mapped_column(Date, nullable=True)
    total_inflow: Mapped[float | None] = mapped_column(nullable=True)
    total_outflow: Mapped[float | None] = mapped_column(nullable=True)
    avg_daily_balance: Mapped[float | None] = mapped_column(nullable=True)
    ending_balance: Mapped[float | None] = mapped_column(nullable=True)
    transaction_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    transaction_summary: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    anomaly_flags: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    parse_status: Mapped[BankStatementParseStatus] = mapped_column(
        Enum(BankStatementParseStatus), default=BankStatementParseStatus.PENDING, nullable=False
    )
    uploaded_by: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id"), nullable=True
    )
    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    parsed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    company = relationship("Company")
    uploader = relationship("User", foreign_keys=[uploaded_by])

    def __repr__(self) -> str:
        return f"<BankStatement(id={self.id}, account={self.account_no})>"
