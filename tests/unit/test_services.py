"""
Unit Tests
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.services.classifier_service import DocumentClassifier
from app.db.models.models import DocumentType
from app.extractors.templates.extraction_templates import get_template, list_templates
from app.core.exceptions import TemplateNotFoundException


# ── Classifier Tests ──────────────────────────────────────────────────────────

class TestDocumentClassifier:
    def setup_method(self):
        self.clf = DocumentClassifier()

    def test_classify_aadhaar(self):
        text = "UIDAI Government of India Aadhaar 1234 5678 9012 Date of Birth: 01/01/1990"
        doc_type, confidence = self.clf.classify(text)
        assert doc_type == DocumentType.AADHAAR
        assert confidence > 0.2

    def test_classify_passport(self):
        text = "PASSPORT Republic of India Ministry of External Affairs P<IND Nationality: Indian"
        doc_type, confidence = self.clf.classify(text)
        assert doc_type == DocumentType.PASSPORT

    def test_classify_driving_licence(self):
        text = "DRIVING LICENCE MH0120231234567 Transport Department Motor Vehicles Act LMV MCWG"
        doc_type, confidence = self.clf.classify(text)
        assert doc_type == DocumentType.DRIVING_LICENCE

    def test_classify_invoice(self):
        text = "TAX INVOICE Invoice No: INV-001 GSTIN: 27AABCU9603R1ZX Total Amount: 11800 CGST SGST"
        doc_type, confidence = self.clf.classify(text)
        assert doc_type == DocumentType.INVOICE

    def test_classify_unknown(self):
        text = "Hello world this is random text with no document keywords."
        doc_type, confidence = self.clf.classify(text)
        assert doc_type == DocumentType.UNKNOWN


# ── Template Tests ────────────────────────────────────────────────────────────

class TestExtractionTemplates:
    def test_get_aadhaar_template(self):
        t = get_template("aadhaar")
        assert t.document_type == "aadhaar"
        assert any(f.name == "aadhaar_number" for f in t.fields)
        assert any(f.name == "name" for f in t.fields)

    def test_get_invoice_template(self):
        t = get_template("invoice")
        assert t.document_type == "invoice"
        assert any(f.name == "total_amount" for f in t.fields)
        assert any(f.name == "invoice_number" for f in t.fields)

    def test_get_unknown_template_raises(self):
        with pytest.raises(TemplateNotFoundException):
            get_template("banana_document")

    def test_list_templates_returns_all(self):
        templates = list_templates()
        types = {t.document_type for t in templates}
        assert {"aadhaar", "driving_licence", "passport", "invoice"}.issubset(types)


# ── LLM Service Tests ─────────────────────────────────────────────────────────

class TestLLMExtractionService:
    @pytest.mark.asyncio
    async def test_extract_fields_success(self):
        from app.services.llm_service import LLMExtractionService

        mock_provider = AsyncMock()
        mock_provider.provider_name = "mock"
        mock_provider.complete = AsyncMock(
            return_value=(
                '{"name": "Ramesh Kumar", "aadhaar_number": "1234 5678 9012"}',
                "mock-model",
            )
        )

        service = LLMExtractionService(provider=mock_provider)
        result = await service.extract_fields(
            ocr_text="Name: Ramesh Kumar Aadhaar: 1234 5678 9012",
            document_type="aadhaar",
        )

        assert result["extracted_fields"]["name"] == "Ramesh Kumar"
        assert result["llm_model"] == "mock-model"

    @pytest.mark.asyncio
    async def test_extract_fields_bad_json_raises(self):
        from app.services.llm_service import LLMExtractionService
        from app.core.exceptions import LLMResponseParseException

        mock_provider = AsyncMock()
        mock_provider.provider_name = "mock"
        mock_provider.complete = AsyncMock(return_value=("not json at all !!!", "mock"))

        service = LLMExtractionService(provider=mock_provider)
        with pytest.raises(LLMResponseParseException):
            await service.extract_fields("some text", "aadhaar")


# ── Exception Tests ───────────────────────────────────────────────────────────

class TestExceptions:
    def test_base_exception_to_dict(self):
        from app.core.exceptions import IDEPBaseException
        exc = IDEPBaseException("Test error", details={"key": "val"})
        d = exc.to_dict()
        assert d["message"] == "Test error"
        assert d["details"]["key"] == "val"

    def test_exception_hierarchy(self):
        from app.core.exceptions import (
            FileSizeExceededException,
            IDEPBaseException,
            OCRException,
        )
        assert issubclass(FileSizeExceededException, IDEPBaseException)
        assert issubclass(OCRException, IDEPBaseException)
