"""Company financials model (工商财报)."""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, JSON, Integer, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .user import Base


class CompanyFinancial(Base):
    __tablename__ = "company_financials"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    company_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("companies.id"), nullable=False
    )
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    balance_sheet: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    income_statement: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    cash_flow: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    key_indicators: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    fetched_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    company = relationship("Company")

    def __repr__(self) -> str:
        return f"<CompanyFinancial(id={self.id}, year={self.year})>"
