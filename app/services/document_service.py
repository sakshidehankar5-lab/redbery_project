"""
Document Processing Service (Orchestrator / Facade)
------------------------------------------------------
Coordinates the full pipeline:
  1. Validate & save uploaded file
  2. Run OCR
  3. Classify document type
  4. Extract structured fields via LLM
  5. Persist all results in DB

This is the single entry-point for file processing — routes call only this.
"""
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.exceptions import FileSizeExceededException, UnsupportedFileTypeException
from app.core.logging import get_logger, log_exceptions, log_execution
from app.db.models.models import DocumentType, ExtractionStatus, OCREngine
from app.db.repositories.repositories import (
    DocumentRepository,
    ExtractionResultRepository,
    OCRResultRepository,
)
from app.services.classifier_service import DocumentClassifier
from app.services.llm_service import LLMExtractionService
from app.services.ocr_service import OCRService

settings = get_settings()
log = get_logger(__name__)

import mimetypes
import aiofiles


class DocumentProcessingService:
    """Facade that orchestrates the entire extraction pipeline."""

    def __init__(
        self,
        session: AsyncSession,
        ocr_service: Optional[OCRService] = None,
        llm_service: Optional[LLMExtractionService] = None,
        classifier: Optional[DocumentClassifier] = None,
    ) -> None:
        self._session = session
        self._doc_repo = DocumentRepository(session)
        self._ocr_repo = OCRResultRepository(session)
        self._extraction_repo = ExtractionResultRepository(session)
        self._ocr = ocr_service or OCRService()
        self._llm = llm_service or LLMExtractionService()
        self._classifier = classifier or DocumentClassifier()

    # ── Public API ────────────────────────────────────────────────

    @log_execution
    @log_exceptions
    async def process_upload(
        self,
        upload: UploadFile,
        document_type: Optional[str] = None,
        custom_fields: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Full pipeline. Returns a summary dict with extraction results.
        """
        # 1. Validate & save
        file_path = await self._save_upload(upload)
        doc = await self._doc_repo.create(
            original_filename=upload.filename or "unknown",
            stored_filename=file_path.name,
            file_path=str(file_path),
            file_size_bytes=file_path.stat().st_size,
            mime_type=upload.content_type or "application/octet-stream",
        )
        log.info(f"File saved: {file_path} | doc_id={doc.id}")

        # 2. OCR
        ocr_pages = await self._ocr.process_document(file_path)
        full_text = "\n\n".join(p["raw_text"] for p in ocr_pages)

        for page in ocr_pages:
            await self._ocr_repo.create(
                document_id=doc.id,
                engine=OCREngine(self._ocr.engine_name),
                raw_text=page["raw_text"],
                confidence_score=page["confidence"],
                page_number=page["page_number"],
                processing_time_ms=page["processing_time_ms"],
            )

        # 3. Classify
        if document_type and document_type != "auto":
            detected_type = DocumentType(document_type)
            confidence = 1.0
        else:
            detected_type, confidence = self._classifier.classify(full_text)

        await self._doc_repo.update_document_type(doc.id, detected_type)

        # 4. Create pending extraction record
        er = await self._extraction_repo.create(
            document_id=doc.id,
            document_type=detected_type,
            status=ExtractionStatus.PROCESSING,
        )

        # 5. LLM Extraction
        try:
            if detected_type == DocumentType.UNKNOWN:
                raise ValueError("Cannot extract from UNKNOWN document type. Please specify manually.")

            llm_result = await self._llm.extract_fields(
                ocr_text=full_text,
                document_type=detected_type.value,
                custom_fields=custom_fields,
            )

            er = await self._extraction_repo.update_status(
                er.id,
                ExtractionStatus.COMPLETED,
                extracted_fields=llm_result["extracted_fields"],
                raw_llm_response=llm_result["raw_llm_response"],
                llm_model=llm_result["llm_model"],
                processing_time_ms=llm_result["processing_time_ms"],
                confidence_score=confidence,
            )
            log.info(f"Extraction complete | doc_id={doc.id} | extraction_id={er.id}")

        except Exception as exc:
            await self._extraction_repo.update_status(
                er.id,
                ExtractionStatus.FAILED,
                error_message=str(exc),
            )
            log.error(f"Extraction failed | doc_id={doc.id} | error={exc}")
            raise

        return {
            "document_id": str(doc.id),
            "extraction_id": str(er.id),
            "original_filename": doc.original_filename,
            "document_type": detected_type.value,
            "classification_confidence": confidence,
            "status": er.status.value,
            "extracted_fields": er.extracted_fields,
            "llm_model": er.llm_model,
            "ocr_pages": len(ocr_pages),
            "processing_time_ms": er.processing_time_ms,
        }

    @log_execution
    async def get_extraction_result(self, extraction_id: uuid.UUID) -> Dict[str, Any]:
        er = await self._extraction_repo.get_by_id(extraction_id)
        doc = await self._doc_repo.get_by_id(er.document_id)
        return {
            "document_id": str(doc.id),
            "extraction_id": str(er.id),
            "original_filename": doc.original_filename,
            "document_type": er.document_type.value,
            "status": er.status.value,
            "extracted_fields": er.extracted_fields,
            "llm_model": er.llm_model,
            "confidence_score": er.confidence_score,
            "processing_time_ms": er.processing_time_ms,
            "error_message": er.error_message,
            "created_at": er.created_at.isoformat(),
        }

    # ── File helpers ──────────────────────────────────────────────

    async def _save_upload(self, upload: UploadFile) -> Path:
        # Validate extension
        filename = upload.filename or "file"
        ext = Path(filename).suffix.lstrip(".").lower()
        if ext not in settings.allowed_extensions_list:
            raise UnsupportedFileTypeException(
                f"File type '.{ext}' not allowed",
                details={"allowed": settings.allowed_extensions_list},
            )

        # Read & size check
        content = await upload.read()
        if len(content) > settings.max_file_size_bytes:
            raise FileSizeExceededException(
                f"File too large: {len(content) / 1024 / 1024:.1f}MB "
                f"(limit {settings.max_file_size_mb}MB)"
            )

        # Save
        upload_dir = Path(settings.upload_dir)
        upload_dir.mkdir(parents=True, exist_ok=True)
        unique_name = f"{uuid.uuid4().hex}_{filename}"
        dest = upload_dir / unique_name

        async with aiofiles.open(dest, "wb") as f:
            await f.write(content)

        return dest
