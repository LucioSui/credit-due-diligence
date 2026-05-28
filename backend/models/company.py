"""Company and related models (shareholders, executives, investments)."""

import uuid
from datetime import datetime

from sqlalchemy import (
    DateTime,
    ForeignKey,
    JSON,
    String,
    Float,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .user import Base


class Company(Base):
    __tablename__ = "companies"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    company_name: Mapped[str] = mapped_column(
        String(256), unique=True, index=True, nullable=False
    )
    unified_credit_code: Mapped[str | None] = mapped_column(
        String(20), unique=True, index=True, nullable=True
    )
    registration_no: Mapped[str | None] = mapped_column(String(64), nullable=True)
    legal_rep: Mapped[str | None] = mapped_column(String(64), nullable=True)
    registered_capital: Mapped[str | None] = mapped_column(String(128), nullable=True)
    est_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    company_status: Mapped[str | None] = mapped_column(String(64), nullable=True)
    business_scope: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    address: Mapped[str | None] = mapped_column(String(512), nullable=True)
    industry_info: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    cached_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Relationships
    shareholders = relationship(
        "CompanyShareholder", back_populates="company", cascade="all, delete-orphan"
    )
    executives = relationship(
        "CompanyExecutive", back_populates="company", cascade="all, delete-orphan"
    )
    investments = relationship(
        "CompanyInvestment", back_populates="company", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Company(id={self.id}, name={self.company_name})>"


class CompanyShareholder(Base):
    __tablename__ = "company_shareholders"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    company_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("companies.id"), nullable=False
    )
    shareholder_name: Mapped[str] = mapped_column(String(256), nullable=False)
    shareholder_type: Mapped[str | None] = mapped_column(String(64), nullable=True)
    share_ratio: Mapped[float | None] = mapped_column(Float, nullable=True)
    subscribe_capital: Mapped[str | None] = mapped_column(String(128), nullable=True)
    paid_in_capital: Mapped[str | None] = mapped_column(String(128), nullable=True)
    pledge_ratio: Mapped[float | None] = mapped_column(Float, nullable=True)
    fetched_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    company = relationship("Company", back_populates="shareholders")

    def __repr__(self) -> str:
        return f"<CompanyShareholder(id={self.id}, name={self.shareholder_name})>"


class CompanyExecutive(Base):
    __tablename__ = "company_executives"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    company_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("companies.id"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    position: Mapped[str | None] = mapped_column(String(128), nullable=True)
    fetched_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    company = relationship("Company", back_populates="executives")

    def __repr__(self) -> str:
        return f"<CompanyExecutive(id={self.id}, name={self.name})>"


class CompanyInvestment(Base):
    __tablename__ = "company_investments"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    company_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("companies.id"), nullable=False
    )
    invested_company: Mapped[str] = mapped_column(String(256), nullable=False)
    invest_ratio: Mapped[float | None] = mapped_column(Float, nullable=True)
    invest_amount: Mapped[str | None] = mapped_column(String(128), nullable=True)
    invest_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    status: Mapped[str | None] = mapped_column(String(64), nullable=True)
    fetched_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    company = relationship("Company", back_populates="investments")

    def __repr__(self) -> str:
        return f"<CompanyInvestment(id={self.id}, invested={self.invested_company})>"
