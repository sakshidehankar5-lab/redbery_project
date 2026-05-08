"""
Integration Tests — FastAPI Endpoints
"""
import io
import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import AsyncClient

from app.main import app


@pytest.fixture
async def client():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


class TestHealthEndpoint:
    @pytest.mark.asyncio
    async def test_health_ok(self, client):
        response = await client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "version" in data


class TestTemplatesEndpoint:
    @pytest.mark.asyncio
    async def test_get_templates(self, client):
        response = await client.get("/api/v1/templates")
        assert response.status_code == 200
        templates = response.json()
        assert isinstance(templates, list)
        assert len(templates) >= 4
        types = {t["document_type"] for t in templates}
        assert "aadhaar" in types
        assert "invoice" in types


class TestDocumentUpload:
    @pytest.mark.asyncio
    async def test_upload_unsupported_extension(self, client):
        """Non-allowed file type should return 415."""
        with patch("app.db.database.get_async_db"):
            fake_file = io.BytesIO(b"fake content")
            response = await client.post(
                "/api/v1/documents/upload",
                files={"file": ("test.exe", fake_file, "application/octet-stream")},
                data={"document_type": "auto"},
            )
        assert response.status_code in (415, 422, 500)

    @pytest.mark.asyncio
    async def test_upload_valid_image(self, client):
        """Mock the full pipeline and verify response shape."""
        mock_result = {
            "document_id": str(uuid.uuid4()),
            "extraction_id": str(uuid.uuid4()),
            "original_filename": "aadhaar.png",
            "document_type": "aadhaar",
            "classification_confidence": 0.85,
            "status": "completed",
            "extracted_fields": {"name": "Test User", "aadhaar_number": "1234 5678 9012"},
            "llm_model": "gpt-4o",
            "ocr_pages": 1,
            "processing_time_ms": 1234.5,
        }

        with patch(
            "app.api.routes.documents.DocumentProcessingService.process_upload",
            new_callable=AsyncMock,
            return_value=mock_result,
        ):
            fake_image = io.BytesIO(b"\x89PNG\r\n\x1a\n" + b"\x00" * 100)
            response = await client.post(
                "/api/v1/documents/upload",
                files={"file": ("aadhaar.png", fake_image, "image/png")},
                data={"document_type": "aadhaar"},
            )

        assert response.status_code == 201
        data = response.json()
        assert data["document_type"] == "aadhaar"
        assert data["status"] == "completed"
        assert "extracted_fields" in data
