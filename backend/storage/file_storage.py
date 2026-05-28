"""File storage management for uploaded documents."""

import mimetypes
import os
import uuid
from pathlib import Path

from fastapi import HTTPException

from config import settings

# Error codes
ERR_FILE_UPLOAD_FAILED = 5001
ERR_UNSUPPORTED_FORMAT = 5003


# Mapping from extension to allowed MIME types
_MIME_MAP: dict[str, dict[str, set[str]]] = {
    "financial_report": {
        ".pdf": {"application/pdf"},
        ".xlsx": {"application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"},
    },
    "bank_statement": {
        ".pdf": {"application/pdf"},
        ".xlsx": {"application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"},
        ".jpg": {"image/jpeg"},
        ".png": {"image/png"},
    },
    "credit_report": {
        ".pdf": {"application/pdf"},
        ".jpg": {"image/jpeg"},
        ".png": {"image/png"},
    },
}


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
        file_content: bytes | None = None,
        max_size: int = 50 * 1024 * 1024,
    ) -> None:
        """Validate file extension, MIME type, and size. Raises HTTPException on failure."""
        # Check extension
        ext = Path(filename).suffix.lower()
        allowed = cls.ALLOWED_EXTENSIONS.get(module, set())
        if ext not in allowed:
            raise HTTPException(
                status_code=ERR_UNSUPPORTED_FORMAT,
                detail=f"不支持的文件格式: {ext}，允许的格式: {', '.join(allowed)}",
            )

        # Check MIME type if content is available
        if file_content is not None:
            mime_types = _MIME_MAP.get(module, {}).get(ext, set())
            if mime_types:
                # Guess MIME type from content magic bytes
                guessed = mimetypes.guess_type(filename, strict=False)[0]
                if guessed is None:
                    # Fallback: check magic bytes for common types
                    if file_content[:4] == b"%PDF":
                        guessed = "application/pdf"
                    elif file_content[:3] == b"\x1f\x8b\x08":
                        guessed = "application/gzip"
                    elif file_content[:8] == b"\x50\x4b\x03\x04\x14\x00\x06\x00":
                        guessed = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    elif file_content[:2] == b"\xff\xd8":
                        guessed = "image/jpeg"
                    elif file_content[:8].startswith(b"\x89PNG"):
                        guessed = "image/png"
                if guessed and guessed not in mime_types:
                    raise HTTPException(
                        status_code=ERR_UNSUPPORTED_FORMAT,
                        detail=f"文件内容类型不匹配: 扩展名为{ext}但检测到{guessed}",
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
