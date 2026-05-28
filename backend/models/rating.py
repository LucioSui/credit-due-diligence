"""Rating records model (六维评分)."""

import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, Float, ForeignKey, JSON, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .user import Base


class Grade(str, enum.Enum):
    A = "A"
    B = "B"
    C = "C"
    D = "D"


class RatingRecord(Base):
    __tablename__ = "rating_records"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    task_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("tasks.id"), nullable=False
    )
    grade: Mapped[Grade] = mapped_column(Enum(Grade), nullable=False)
    total_score: Mapped[float] = mapped_column(Float, nullable=False)
    judicial_score: Mapped[float] = mapped_column(Float, nullable=False)
    financial_score: Mapped[float] = mapped_column(Float, nullable=False)
    credit_score: Mapped[float] = mapped_column(Float, nullable=False)
    operation_score: Mapped[float] = mapped_column(Float, nullable=False)
    equity_score: Mapped[float] = mapped_column(Float, nullable=False)
    compliance_score: Mapped[float] = mapped_column(Float, nullable=False)
    detail_breakdown: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    rated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    task = relationship("Task")

    def __repr__(self) -> str:
        return f"<RatingRecord(id={self.id}, grade={self.grade}, score={self.total_score})>"
