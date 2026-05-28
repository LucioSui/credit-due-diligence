"""File storage management for uploaded documents."""

import os
import uuid
from pathlib import Path

from fastapi import HTTPException

from config import settings

# Error codes
ERR_FILE_UPLOAD_FAILED = 5001
ERR_UNSUPPORTED_FORMAT = 5003


class FileStorage:
    """Handles saving, validating, and deleting uploaded files."""

    UPLOAD_DIR = "storage/uploads"

    ALLOWED_EXTENSIONS: dict[str, set[str]] = {
        "financial_report": {".pdf", ".xlsx"},
        "bank_statement": {".pdf", ".xlsx", ".jpg", ".png"},
        "credit_report": {".pdf", ".jpg", ".png"},
    }

    @classmethod
    def get_upload_path(cls, company_id: str, module: str, filename: str) -> str:
        """Return the full upload path: storage/uploads/{company_id}/{module}/{safe_filename}."""
        safe_filename = cls._sanitize_filename(filename)
        base = Path(cls.UPLOAD_DIR) / str(company_id) / module
        return str(base / safe_filename)

    @classmethod
    def validate_file(
        cls,
        filename: str,
        module: str,
        file_size: int,
        max_size: int = 50 * 1024 * 1024,
    ) -> None:
        """Validate file extension and size. Raises HTTPException on failure."""
        # Check extension
        ext = Path(filename).suffix.lower()
        allowed = cls.ALLOWED_EXTENSIONS.get(module, set())
        if ext not in allowed:
            raise HTTPException(
                status_code=ERR_UNSUPPORTED_FORMAT,
                detail=f"不支持的文件格式: {ext}，允许的格式: {', '.join(allowed)}",
            )

        # Check size
        if file_size > max_size:
            raise HTTPException(
                status_code=ERR_FILE_UPLOAD_FAILED,
                detail=f"文件大小超限 ({file_size} > {max_size} bytes)",
            )

    @classmethod
    async def save_file(cls, file_content: bytes, save_path: str) -> str:
        """Write *file_content* to disk at *save_path* and return the absolute path."""
        path = Path(save_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(file_content)
        return str(path.resolve())

    @classmethod
    async def delete_file(cls, file_path: str) -> None:
        """Remove a file from disk if it exists."""
        path = Path(file_path)
        if path.exists():
            path.unlink()

    @classmethod
    def _sanitize_filename(cls, filename: str) -> str:
        """Strip dangerous characters and append a uuid prefix to avoid collisions."""
        stem = Path(filename).stem
        ext = Path(filename).suffix.lower()
        # Keep only alphanumeric, dash, underscore, chinese chars
        safe = "".join(ch if ch.isalnum() or ch in "-_你我他" else "_" for ch in stem)
        if not safe:
            safe = "file"
        unique = str(uuid.uuid4())[:8]
        return f"{unique}_{safe}{ext}"

    @classmethod
    def get_file_source_from_filename(cls, filename: str) -> str:
        """Determine FileSource enum value from filename extension."""
        ext = Path(filename).suffix.lower()
        if ext == ".pdf":
            return "pdf"
        elif ext == ".xlsx":
            return "excel"
        return "excel"  # default fallback
