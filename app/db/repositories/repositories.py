"""
Repository Pattern (Data Access Layer)
---------------------------------------
Follows Repository + Unit-of-Work pattern.
All DB access goes through these classes — services never touch SQLAlchemy directly.
"""
import uuid
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import RecordNotFoundException
from app.core.logging import get_logger, log_exceptions, log_execution
from app.db.models.models import Document, DocumentType, ExtractionResult, ExtractionStatus, OCRResult

log = get_logger(__name__)


class DocumentRepository:
    """CRUD operations for Document model."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    @log_execution
    @log_exceptions
    async def create(self, **kwargs) -> Document:
        doc = Document(**kwargs)
        self._session.add(doc)
        await self._session.flush()
        await self._session.refresh(doc)
        log.info(f"Document created: id={doc.id}")
        return doc

    @log_execution
    async def get_by_id(self, doc_id: uuid.UUID) -> Document:
        result = await self._session.execute(
            select(Document).where(Document.id == doc_id)
        )
        doc = result.scalar_one_or_none()
        if not doc:
            raise RecordNotFoundException(
                f"Document {doc_id} not found", details={"document_id": str(doc_id)}
            )
        return doc

    @log_execution
    async def list_all(self, limit: int = 50, offset: int = 0) -> List[Document]:
        result = await self._session.execute(
            select(Document).order_by(Document.created_at.desc()).limit(limit).offset(offset)
        )
        return list(result.scalars().all())

    @log_execution
    async def update_document_type(self, doc_id: uuid.UUID, doc_type: DocumentType) -> Document:
        doc = await self.get_by_id(doc_id)
        doc.document_type = doc_type
        await self._session.flush()
        return doc

    @log_execution
    async def delete(self, doc_id: uuid.UUID) -> None:
        doc = await self.get_by_id(doc_id)
        await self._session.delete(doc)
        await self._session.flush()
        log.info(f"Document deleted: id={doc_id}")


class OCRResultRepository:
    """CRUD operations for OCRResult model."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    @log_execution
    @log_exceptions
    async def create(self, **kwargs) -> OCRResult:
        ocr = OCRResult(**kwargs)
        self._session.add(ocr)
        await self._session.flush()
        await self._session.refresh(ocr)
        return ocr

    @log_execution
    async def get_by_document(self, doc_id: uuid.UUID) -> List[OCRResult]:
        result = await self._session.execute(
            select(OCRResult)
            .where(OCRResult.document_id == doc_id)
            .order_by(OCRResult.page_number)
        )
        return list(result.scalars().all())


class ExtractionResultRepository:
    """CRUD operations for ExtractionResult model."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    @log_execution
    @log_exceptions
    async def create(self, **kwargs) -> ExtractionResult:
        er = ExtractionResult(**kwargs)
        self._session.add(er)
        await self._session.flush()
        await self._session.refresh(er)
        log.info(f"ExtractionResult created: id={er.id}")
        return er

    @log_execution
    async def get_by_id(self, result_id: uuid.UUID) -> ExtractionResult:
        result = await self._session.execute(
            select(ExtractionResult).where(ExtractionResult.id == result_id)
        )
        er = result.scalar_one_or_none()
        if not er:
            raise RecordNotFoundException(
                f"ExtractionResult {result_id} not found",
                details={"result_id": str(result_id)},
            )
        return er

    @log_execution
    async def get_by_document(self, doc_id: uuid.UUID) -> List[ExtractionResult]:
        result = await self._session.execute(
            select(ExtractionResult)
            .where(ExtractionResult.document_id == doc_id)
            .order_by(ExtractionResult.created_at.desc())
        )
        return list(result.scalars().all())

    @log_execution
    async def update_status(
        self,
        result_id: uuid.UUID,
        status: ExtractionStatus,
        **extra_fields,
    ) -> ExtractionResult:
        er = await self.get_by_id(result_id)
        er.status = status
        for k, v in extra_fields.items():
            setattr(er, k, v)
        await self._session.flush()
        return er
