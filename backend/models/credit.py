"""Credit models: legal person credit (法人征信) and enterprise credit (企业征信)."""

import enum
import uuid
from datetime import datetime

from cryptography.fernet import Fernet, InvalidToken
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
from sqlalchemy.ext.hybrid import hybrid_property

from config import settings
from .user import Base


def _get_fernet() -> Fernet:
    """Get Fernet cipher instance using the dedicated FERNET_KEY.

    Uses FERNET_KEY if configured; otherwise falls back to deriving from SECRET_KEY
    for backward compatibility with existing encrypted data.
    """
    if settings.FERNET_KEY:
        return Fernet(settings.FERNET_KEY.encode("utf-8"))
    # Backward-compatible derivation from SECRET_KEY
    import base64
    import hashlib

    raw = settings.SECRET_KEY.encode("utf-8")
    key = base64.urlsafe_b64encode(hashlib.sha256(raw).digest())
    return Fernet(key)


def encrypt_id_no(value: str) -> str:
    """Encrypt a plaintext ID number for storage."""
    return _get_fernet().encrypt(value.encode("utf-8")).decode("utf-8")


def decrypt_id_no(encrypted_value: str) -> str:
    """Decrypt an encrypted ID number.

    SECURITY: Never returns plaintext on decryption failure.
    Returns '[DECRYPTION_FAILED]' sentinel so the caller can detect the error
    without ever leaking raw data.
    """
    try:
        return _get_fernet().decrypt(encrypted_value.encode("utf-8")).decode("utf-8")
    except InvalidToken:
        return "[DECRYPTION_FAILED]"


def mask_id_number(value: str) -> str:
    """Mask a Chinese ID number for display.

    Rules:
    - 18-digit ID card: show first 3 + last 4, mask the middle (e.g. 110***********1234)
    - Unified social credit code (18 chars): same masking
    - Shorter values: show first 2 + last 2, mask the middle
    - Non-string or already-mocked values: return as-is
    """
    if not value or not isinstance(value, str):
        return value or ""
    # Skip already-masked or error sentinel values
    if value.startswith("[") or "*" in value:
        return value
    length = len(value)
    if length <= 6:
        return value[:2] + "*" * (length - 4) + value[-2:] if length > 4 else "**" * (length // 2)
    # Show first 3 and last 4
    return value[:3] + "*" * (length - 7) + value[-4:]


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
    # Stored encrypted; use hybrid_property for transparent encrypt/decrypt.
    _person_id_no_encrypted: Mapped[str] = mapped_column(
        "person_id_no", String(512), nullable=False
    )

    @hybrid_property
    def person_id_no(self) -> str:
        return decrypt_id_no(self._person_id_no_encrypted)

    @person_id_no.setter
    def person_id_no(self, value: str):
        self._person_id_no_encrypted = encrypt_id_no(value)
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
