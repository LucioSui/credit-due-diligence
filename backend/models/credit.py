"""Credit models: legal person credit (法人征信) and enterprise credit (企业征信)."""

import enum
import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    JSON,
    Integer,
    String,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .user import Base


# ── Legal Person Credit (法人征信 3.7) ──────────────────────────────────────


class PersonIdType(str, enum.Enum):
    ID_CARD = "id_card"
    UNIFIED_SOCIAL_CODE = "unified_social_code"


class CreditSource(str, enum.Enum):
    UPLOADED = "uploaded"
    MANUAL = "manual"


class CreditRating(str, enum.Enum):
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"


class LegalPersonCredit(Base):
    __tablename__ = "legal_person_credit"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    company_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("companies.id"), nullable=False
    )
    person_name: Mapped[str] = mapped_column(String(128), nullable=False)
    person_id_type: Mapped[PersonIdType] = mapped_column(
        Enum(PersonIdType), nullable=False
    )
    person_id_no: Mapped[str] = mapped_column(String(64), nullable=False)
    credit_source: Mapped[CreditSource] = mapped_column(
        Enum(CreditSource), nullable=False
    )
    credit_rating: Mapped[CreditRating | None] = mapped_column(
        Enum(CreditRating), nullable=True
    )
    loan_accounts: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    credit_card_accounts: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    guarantee_info: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    overdue_records: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    default_records: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    report_snapshot: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    report_file_path: Mapped[str | None] = mapped_column(String(512), nullable=True)
    entered_by: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id"), nullable=False
    )
    entered_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    company = relationship("Company")
    entered_user = relationship("User")

    def __repr__(self) -> str:
        return f"<LegalPersonCredit(id={self.id}, person={self.person_name})>"


# ── Enterprise Credit (企业征信 3.8) ────────────────────────────────────────


class EnterpriseCredit(Base):
    __tablename__ = "enterprise_credit"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    company_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("companies.id"), nullable=False
    )
    credit_source: Mapped[CreditSource] = mapped_column(
        Enum(CreditSource), nullable=False
    )
    total_credit_line: Mapped[float | None] = mapped_column(nullable=True)
    used_credit_line: Mapped[float | None] = mapped_column(nullable=True)
    remaining_credit_line: Mapped[float | None] = mapped_column(nullable=True)
    loan_details: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    guarantee_out: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    guarantee_in: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    overdue_info: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    attention_list: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    multi_lending_flag: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    lender_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    report_snapshot: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    report_file_path: Mapped[str | None] = mapped_column(String(512), nullable=True)
    entered_by: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id"), nullable=False
    )
    entered_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    company = relationship("Company")
    entered_user = relationship("User")

    def __repr__(self) -> str:
        return f"<EnterpriseCredit(id={self.id}, company_id={self.company_id})>"
