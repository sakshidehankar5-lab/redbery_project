"""
Database Models (SQLAlchemy 2.x mapped classes)
"""
import uuid
from datetime import datetime
from typing import Any, Dict, Optional

from sqlalchemy import (
    JSON,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.types import TypeDecorator
import enum
import uuid as uuid_pkg


# UUID type that works with both PostgreSQL and SQLite
class GUID(TypeDecorator):
    """Platform-independent GUID type. Uses PostgreSQL's UUID type, otherwise uses CHAR(36)."""
    impl = String
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            from sqlalchemy.dialects.postgresql import UUID
            return dialect.type_descriptor(UUID(as_uuid=True))
        else:
            return dialect.type_descriptor(String(36))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == 'postgresql':
            return value
        else:
            if isinstance(value, uuid_pkg.UUID):
                return str(value)
            return value

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        if isinstance(value, uuid_pkg.UUID):
            return value
        return uuid_pkg.UUID(value)


class Base(DeclarativeBase):
    pass


# ── Enums ─────────────────────────────────────────────────────────────────────

class DocumentType(str, enum.Enum):
    AADHAAR = "aadhaar"
    DRIVING_LICENCE = "driving_licence"
    PASSPORT = "passport"
    INVOICE = "invoice"
    UNKNOWN = "unknown"


class ExtractionStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class OCREngine(str, enum.Enum):
    TESSERACT = "tesseract"
    PADDLEOCR = "paddleocr"


# ── Models ────────────────────────────────────────────────────────────────────

class Document(Base):
    """Uploaded document record."""
    __tablename__ = "documents"

    id: Mapped[uuid_pkg.UUID] = mapped_column(
        GUID(), primary_key=True, default=uuid_pkg.uuid4
    )
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    stored_filename: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    file_path: Mapped[str] = mapped_column(Text, nullable=False)
    file_size_bytes: Mapped[int] = mapped_column(Integer, nullable=False)
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False)
    document_type: Mapped[DocumentType] = mapped_column(
        Enum(DocumentType), default=DocumentType.UNKNOWN, nullable=False
    )
    page_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    extractions: Mapped[list["ExtractionResult"]] = relationship(
        "ExtractionResult", back_populates="document", cascade="all, delete-orphan"
    )
    ocr_results: Mapped[list["OCRResult"]] = relationship(
        "OCRResult", back_populates="document", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Document id={self.id} type={self.document_type} file={self.original_filename}>"


class OCRResult(Base):
    """Raw OCR text extracted from a document."""
    __tablename__ = "ocr_results"

    id: Mapped[uuid_pkg.UUID] = mapped_column(
        GUID(), primary_key=True, default=uuid_pkg.uuid4
    )
    document_id: Mapped[uuid_pkg.UUID] = mapped_column(
        GUID(), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False
    )
    engine: Mapped[OCREngine] = mapped_column(Enum(OCREngine), nullable=False)
    raw_text: Mapped[str] = mapped_column(Text, nullable=False)
    confidence_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    page_number: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    processing_time_ms: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    document: Mapped["Document"] = relationship("Document", back_populates="ocr_results")


class ExtractionResult(Base):
    """Structured data extracted by LLM from OCR text."""
    __tablename__ = "extraction_results"

    id: Mapped[uuid_pkg.UUID] = mapped_column(
        GUID(), primary_key=True, default=uuid_pkg.uuid4
    )
    document_id: Mapped[uuid_pkg.UUID] = mapped_column(
        GUID(), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False
    )
    document_type: Mapped[DocumentType] = mapped_column(Enum(DocumentType), nullable=False)
    status: Mapped[ExtractionStatus] = mapped_column(
        Enum(ExtractionStatus), default=ExtractionStatus.PENDING, nullable=False
    )
    extracted_fields: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    raw_llm_response: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    confidence_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    llm_model: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    processing_time_ms: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    document: Mapped["Document"] = relationship("Document", back_populates="extractions")

    def __repr__(self) -> str:
        return f"<ExtractionResult id={self.id} status={self.status} doc_type={self.document_type}>"
