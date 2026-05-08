"""
Pydantic Schemas — API Request & Response Models
"""
import uuid
from datetime import datetime
from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


# ── Enums (mirror DB enums) ───────────────────────────────────────────────────

DocumentTypeEnum = Literal[
    "aadhaar", "driving_licence", "passport", "invoice", "unknown", "auto"
]

ExtractionStatusEnum = Literal["pending", "processing", "completed", "failed"]


# ── Upload ────────────────────────────────────────────────────────────────────

class ExtractionRequest(BaseModel):
    """Query params / form data for upload endpoint."""
    document_type: DocumentTypeEnum = Field(
        default="auto",
        description="Document type. Use 'auto' for automatic detection.",
    )
    custom_fields: Optional[List[str]] = Field(
        default=None,
        description="Restrict extraction to these field names only (optional).",
    )


# ── Response ──────────────────────────────────────────────────────────────────

class ExtractionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    document_id: uuid.UUID
    extraction_id: uuid.UUID
    original_filename: str
    document_type: str
    classification_confidence: float
    status: str
    extracted_fields: Optional[Dict[str, Any]] = None
    llm_model: Optional[str] = None
    ocr_pages: int
    processing_time_ms: Optional[float] = None


class ExtractionDetailResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    document_id: uuid.UUID
    extraction_id: uuid.UUID
    original_filename: str
    document_type: str
    status: str
    extracted_fields: Optional[Dict[str, Any]] = None
    llm_model: Optional[str] = None
    confidence_score: Optional[float] = None
    processing_time_ms: Optional[float] = None
    error_message: Optional[str] = None
    created_at: str


class DocumentListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    original_filename: str
    document_type: str
    file_size_bytes: int
    created_at: datetime


class TemplateFieldSchema(BaseModel):
    name: str
    description: str
    required: bool
    example: Optional[str] = None


class TemplateResponse(BaseModel):
    document_type: str
    display_name: str
    fields: List[TemplateFieldSchema]


class HealthResponse(BaseModel):
    status: str
    version: str
    environment: str


class ErrorResponse(BaseModel):
    error_code: str
    message: str
    details: Dict[str, Any] = {}
