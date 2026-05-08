"""
Custom Exception Hierarchy
--------------------------
All domain exceptions inherit from IDEPBaseException so that
a single FastAPI exception handler can catch & format them uniformly.
"""
from typing import Any, Dict, Optional


class IDEPBaseException(Exception):
    """Root exception for the IDEP platform."""
    status_code: int = 500
    error_code: str = "INTERNAL_ERROR"

    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.details = details or {}
        self.cause = cause

    def to_dict(self) -> Dict[str, Any]:
        return {
            "error_code": self.error_code,
            "message": self.message,
            "details": self.details,
        }


# ── File / Upload ─────────────────────────────────────────────────────────────

class FileUploadException(IDEPBaseException):
    status_code = 400
    error_code = "FILE_UPLOAD_ERROR"


class UnsupportedFileTypeException(IDEPBaseException):
    status_code = 415
    error_code = "UNSUPPORTED_FILE_TYPE"


class FileSizeExceededException(IDEPBaseException):
    status_code = 413
    error_code = "FILE_TOO_LARGE"


# ── OCR ───────────────────────────────────────────────────────────────────────

class OCRException(IDEPBaseException):
    status_code = 500
    error_code = "OCR_PROCESSING_ERROR"


class OCREngineNotAvailableException(IDEPBaseException):
    status_code = 503
    error_code = "OCR_ENGINE_UNAVAILABLE"


# ── LLM ───────────────────────────────────────────────────────────────────────

class LLMException(IDEPBaseException):
    status_code = 502
    error_code = "LLM_ERROR"


class LLMRateLimitException(LLMException):
    status_code = 429
    error_code = "LLM_RATE_LIMIT"


class LLMResponseParseException(LLMException):
    status_code = 500
    error_code = "LLM_PARSE_ERROR"


# ── Extraction ────────────────────────────────────────────────────────────────

class ExtractionException(IDEPBaseException):
    status_code = 422
    error_code = "EXTRACTION_ERROR"


class DocumentClassificationException(IDEPBaseException):
    status_code = 422
    error_code = "CLASSIFICATION_ERROR"


class TemplateNotFoundException(IDEPBaseException):
    status_code = 404
    error_code = "TEMPLATE_NOT_FOUND"


# ── Database ──────────────────────────────────────────────────────────────────

class DatabaseException(IDEPBaseException):
    status_code = 500
    error_code = "DATABASE_ERROR"


class RecordNotFoundException(IDEPBaseException):
    status_code = 404
    error_code = "RECORD_NOT_FOUND"
