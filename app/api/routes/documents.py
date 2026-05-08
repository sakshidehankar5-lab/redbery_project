"""
API Routes
-----------
POST /documents/upload    — upload & extract
GET  /documents           — list all documents
GET  /documents/{id}      — get extraction result
GET  /templates           — list available templates
GET  /health              — health check
"""
import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas import (
    DocumentListItem,
    ErrorResponse,
    ExtractionDetailResponse,
    ExtractionResponse,
    HealthResponse,
    TemplateResponse,
)
from app.core.config import get_settings
from app.core.exceptions import IDEPBaseException
from app.core.logging import get_logger
from app.db.database import get_async_db
from app.db.repositories.repositories import DocumentRepository, ExtractionResultRepository
from app.extractors.templates.extraction_templates import list_templates
from app.services.document_service import DocumentProcessingService

settings = get_settings()
log = get_logger(__name__)
router = APIRouter()


# ── Health ────────────────────────────────────────────────────────────────────

@router.get("/health", response_model=HealthResponse, tags=["System"])
async def health_check():
    return HealthResponse(
        status="ok",
        version=settings.app_version,
        environment=settings.app_env,
    )


# ── Templates ─────────────────────────────────────────────────────────────────

@router.get("/templates", response_model=List[TemplateResponse], tags=["Templates"])
async def get_templates():
    """Return all supported document types and their extractable fields."""
    templates = list_templates()
    return [
        TemplateResponse(
            document_type=t.document_type,
            display_name=t.display_name,
            fields=[
                {
                    "name": f.name,
                    "description": f.description,
                    "required": f.required,
                    "example": f.example,
                }
                for f in t.fields
            ],
        )
        for t in templates
    ]


# ── Document Upload & Extraction ──────────────────────────────────────────────

@router.post(
    "/documents/upload",
    response_model=ExtractionResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Documents"],
    summary="Upload a document and extract structured data",
)
async def upload_and_extract(
    file: UploadFile = File(..., description="Document file (PDF, PNG, JPG, TIFF)"),
    document_type: str = Form(
        default="auto",
        description="Document type or 'auto' for auto-detection",
    ),
    custom_fields: Optional[str] = Form(
        default=None,
        description="Comma-separated list of fields to extract (optional)",
    ),
    db: AsyncSession = Depends(get_async_db),
):
    fields_list = (
        [f.strip() for f in custom_fields.split(",") if f.strip()]
        if custom_fields
        else None
    )

    service = DocumentProcessingService(session=db)
    try:
        result = await service.process_upload(
            upload=file,
            document_type=document_type,
            custom_fields=fields_list,
        )
        return ExtractionResponse(**result)
    except IDEPBaseException as e:
        log.error(f"Extraction pipeline error: {e.message}")
        raise HTTPException(status_code=e.status_code, detail=e.to_dict())
    except Exception as e:
        log.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail={"error_code": "INTERNAL_ERROR", "message": str(e)})


# ── List Documents ────────────────────────────────────────────────────────────

@router.get(
    "/documents",
    response_model=List[DocumentListItem],
    tags=["Documents"],
    summary="List all processed documents",
)
async def list_documents(
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_async_db),
):
    repo = DocumentRepository(db)
    docs = await repo.list_all(limit=limit, offset=offset)
    return [
        DocumentListItem(
            id=d.id,
            original_filename=d.original_filename,
            document_type=d.document_type.value,
            file_size_bytes=d.file_size_bytes,
            created_at=d.created_at,
        )
        for d in docs
    ]


# ── Get Extraction Result ─────────────────────────────────────────────────────

@router.get(
    "/documents/{extraction_id}",
    response_model=ExtractionDetailResponse,
    tags=["Documents"],
    summary="Get extraction result by ID",
)
async def get_extraction(
    extraction_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_db),
):
    service = DocumentProcessingService(session=db)
    try:
        result = await service.get_extraction_result(extraction_id)
        return ExtractionDetailResponse(**result)
    except IDEPBaseException as e:
        raise HTTPException(status_code=e.status_code, detail=e.to_dict())
