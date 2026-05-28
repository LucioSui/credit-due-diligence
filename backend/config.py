"""Application configuration using pydantic-settings."""

import os

from pydantic import model_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./dev.db"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # Security
    SECRET_KEY: str = "change-me-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours

    # Fernet encryption key for sensitive fields (e.g. ID numbers).
    # Must be a valid 32-byte URL-safe base64-encoded key.
    # Generate with: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
    FERNET_KEY: str = ""

    @model_validator(mode="after")
    def _validate_fernet_key(self):
        if self.FERNET_KEY and len(self.FERNET_KEY) < 44:
            raise ValueError(
                "FERNET_KEY must be a valid Fernet key (44 base64url characters). "
                "Generate one with: python -c \"from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())\""
            )
        return self

    # QCC API
    QCC_API_KEY: str = ""
    QCC_API_BASE_URL: str = "https://api.qcc.com"

    # Debug — must be False in production
    DEBUG: bool = False

    # Demo mode — must be False in production
    ENABLE_DEMO_MODE: bool = False

    # CORS — read from ALLOWED_ORIGINS env var (comma-separated)
    _allowed_origins: str | None = None

    @property
    def ALLOWED_ORIGINS(self) -> list[str]:
        raw = os.getenv("ALLOWED_ORIGINS")
        if raw:
            return [o.strip() for o in raw.split(",") if o.strip()]
        return [
            "http://localhost:3000",
            "http://localhost:3001",
            "http://localhost:5173",
            "http://localhost:80",
        ]

    # File upload
    MAX_FILE_SIZE: int = 50 * 1024 * 1024  # 50MB
    UPLOAD_DIR: str = "uploads"

    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"

    model_config = {"env_file": ".env", "case_sensitive": False}

    @model_validator(mode="after")
    def _validate_secret_key(self):
        if self.SECRET_KEY == "change-me-in-production":
            raise ValueError(
                "SECRET_KEY must be set to a secure random value (>= 32 characters). "
                "Generate one with: python -c 'import secrets; print(secrets.token_urlsafe(48))'"
            )
        if len(self.SECRET_KEY) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters long")
        return self


settings = Settings()
