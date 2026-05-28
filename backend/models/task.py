"""Tasks model."""

import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, Float, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .user import Base


class TaskStatus(str, enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    task_no: Mapped[str] = mapped_column(
        String(32), unique=True, index=True, nullable=False
    )  # format: DD-YYYYMMDD-XXXX
    company_name: Mapped[str] = mapped_column(String(256), nullable=False)
    unified_credit_code: Mapped[str | None] = mapped_column(
        String(20), index=True, nullable=True
    )
    status: Mapped[TaskStatus] = mapped_column(
        Enum(TaskStatus), default=TaskStatus.PENDING, nullable=False
    )
    progress: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    creator_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id"), nullable=False
    )
    remark: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Relationships
    creator = relationship("User", back_populates="created_tasks")

    def __repr__(self) -> str:
        return f"<Task(id={self.id}, task_no={self.task_no}, status={self.status})>"


# Add back_populates to User model via relationship
from .user import User  # noqa: E402

User.created_tasks = relationship("Task", back_populates="creator")
