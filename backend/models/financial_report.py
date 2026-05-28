"""Uploaded financial reports model (客户上传财报)."""

import enum
import uuid
from datetime import datetime

from sqlalchemy import (
    DateTime,
    Enum,
    ForeignKey,
    JSON,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .user import Base


class ReportType(str, enum.Enum):
    AUDIT = "audit"
    TAX = "tax"
    QUARTERLY = "quarterly"


class FileSource(str, enum.Enum):
    PDF = "pdf"
    EXCEL = "excel"


class ParseStatus(str, enum.Enum):
    PENDING = "pending"
    PARSED = "parsed"
    FAILED = "failed"


class UploadedFinancialReport(Base):
    __tablename__ = "uploaded_financial_reports"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    company_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("companies.id"), nullable=False
    )
    report_type: Mapped[ReportType] = mapped_column(
        Enum(ReportType), nullable=False
    )
    report_period: Mapped[str | None] = mapped_column(String(64), nullable=True)
    file_name: Mapped[str] = mapped_column(String(256), nullable=False)
    file_path: Mapped[str] = mapped_column(String(512), nullable=False)
    file_source: Mapped[FileSource] = mapped_column(
        Enum(FileSource), nullable=False
    )
    total_assets: Mapped[float | None] = mapped_column(nullable=True)
    total_liabilities: Mapped[float | None] = mapped_column(nullable=True)
    revenue: Mapped[float | None] = mapped_column(nullable=True)
    net_profit: Mapped[float | None] = mapped_column(nullable=True)
    operating_cash_flow: Mapped[float | None] = mapped_column(nullable=True)
    parsed_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    parse_status: Mapped[ParseStatus] = mapped_column(
        Enum(ParseStatus), default=ParseStatus.PENDING, nullable=False
    )
    parse_error: Mapped[str | None] = mapped_column(Text, nullable=True)
    uploaded_by: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id"), nullable=False
    )
    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    parsed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    company = relationship("Company")
    uploader = relationship("User")

    def __repr__(self) -> str:
        return f"<UploadedFinancialReport(id={self.id}, file={self.file_name})>"
