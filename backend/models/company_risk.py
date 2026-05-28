"""Company risks model."""

import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, JSON, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .user import Base


class RiskType(str, enum.Enum):
    LAWSUIT = "lawsuit"
    DISHONEST = "dishonest"
    RESTRICTION = "restriction"
    PENALTY = "penalty"
    ABNORMAL = "abnormal"
    TAX_ABNORMAL = "tax_abnormal"
    BANKRUPTCY = "bankruptcy"
    PLEDGE = "pledge"
    FREEZE = "freeze"
    OTHER = "other"


class RiskLevel(str, enum.Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class CompanyRisk(Base):
    __tablename__ = "company_risks"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    company_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("companies.id"), nullable=False
    )
    risk_type: Mapped[RiskType] = mapped_column(
        Enum(RiskType), nullable=False
    )
    risk_level: Mapped[RiskLevel] = mapped_column(
        Enum(RiskLevel), nullable=False
    )
    risk_detail: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    detected_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    company = relationship("Company")

    def __repr__(self) -> str:
        return f"<CompanyRisk(id={self.id}, type={self.risk_type}, level={self.risk_level})>"
