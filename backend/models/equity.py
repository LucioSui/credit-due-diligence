"""Equity chains model."""

import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, JSON, Integer, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .user import Base


class ChainType(str, enum.Enum):
    UPWARD = "upward"
    DOWNWARD = "downward"
    UBO = "ubo"


class EquityChain(Base):
    __tablename__ = "equity_chains"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    company_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("companies.id"), nullable=False
    )
    chain_type: Mapped[ChainType] = mapped_column(
        Enum(ChainType), nullable=False
    )
    chain_depth: Mapped[int] = mapped_column(Integer, nullable=False)
    chain_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    fetched_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    company = relationship("Company")

    def __repr__(self) -> str:
        return f"<EquityChain(id={self.id}, type={self.chain_type}, depth={self.chain_depth})>"
