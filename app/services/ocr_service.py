"""
OCR Service — Strategy Pattern
--------------------------------
OCRStrategy (interface)
  ├── TesseractOCRStrategy
  └── PaddleOCRStrategy

OCRService selects the strategy via config and exposes a single
`extract_text(image_path)` method.
"""
import time
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional

from PIL import Image

from app.core.config import get_settings
from app.core.exceptions import OCREngineNotAvailableException, OCRException
from app.core.logging import get_logger, log_exceptions, log_execution

settings = get_settings()
log = get_logger(__name__)


# ── Strategy Interface ────────────────────────────────────────────────────────

class OCRStrategy(ABC):
    """Abstract base — all OCR engines implement this."""

    @abstractmethod
    def extract(self, image: Image.Image) -> tuple[str, Optional[float]]:
        """
        Returns (raw_text, confidence_score).
        confidence_score may be None if engine doesn't support it.
        """

    @property
    @abstractmethod
    def engine_name(self) -> str:
        ...


# ── Tesseract Strategy ────────────────────────────────────────────────────────

class TesseractOCRStrategy(OCRStrategy):
    """Wraps pytesseract."""

    def __init__(self) -> None:
        try:
            import pytesseract
            pytesseract.pytesseract.tesseract_cmd = settings.tesseract_cmd
            self._tesseract = pytesseract
        except ImportError as e:
            raise OCREngineNotAvailableException(
                "pytesseract not installed", cause=e
            )

    @property
    def engine_name(self) -> str:
        return "tesseract"

    @log_exceptions
    def extract(self, image: Image.Image) -> tuple[str, Optional[float]]:
        try:
            text = self._tesseract.image_to_string(
                image, lang=settings.ocr_language, config="--psm 6"
            )
            # Get per-character confidence and compute mean
            data = self._tesseract.image_to_data(
                image, output_type=self._tesseract.Output.DICT
            )
            confs = [c for c in data["conf"] if c != -1]
            confidence = sum(confs) / len(confs) / 100.0 if confs else None
            return text.strip(), confidence
        except Exception as e:
            raise OCRException(f"Tesseract extraction failed: {e}", cause=e)


# ── PaddleOCR Strategy ────────────────────────────────────────────────────────

class PaddleOCRStrategy(OCRStrategy):
    """Wraps PaddleOCR (optional — install paddleocr separately)."""

    def __init__(self) -> None:
        try:
            from paddleocr import PaddleOCR  # type: ignore
            self._paddle = PaddleOCR(use_angle_cls=True, lang="en", show_log=False)
        except ImportError as e:
            raise OCREngineNotAvailableException(
                "paddleocr not installed. Run: pip install paddleocr", cause=e
            )

    @property
    def engine_name(self) -> str:
        return "paddleocr"

    @log_exceptions
    def extract(self, image: Image.Image) -> tuple[str, Optional[float]]:
        import numpy as np
        try:
            img_array = np.array(image)
            result = self._paddle.ocr(img_array, cls=True)
            lines = []
            confidences = []
            for line in result or []:
                for item in line or []:
                    text_info = item[1]
                    lines.append(text_info[0])
                    confidences.append(text_info[1])
            raw_text = "\n".join(lines)
            confidence = sum(confidences) / len(confidences) if confidences else None
            return raw_text.strip(), confidence
        except Exception as e:
            raise OCRException(f"PaddleOCR extraction failed: {e}", cause=e)


# ── OCR Service ────────────────────────────────────────────────────────────────

class OCRService:
    """
    High-level OCR service.
    Selects strategy from config; handles image pre-processing and PDF conversion.
    """

    def __init__(self, strategy: Optional[OCRStrategy] = None) -> None:
        self._strategy = strategy or self._build_strategy()

    def _build_strategy(self) -> OCRStrategy:
        engine = settings.ocr_engine.lower()
        if engine == "tesseract":
            return TesseractOCRStrategy()
        elif engine == "paddleocr":
            return PaddleOCRStrategy()
        raise OCREngineNotAvailableException(f"Unknown OCR engine: {engine}")

    @property
    def engine_name(self) -> str:
        return self._strategy.engine_name

    @log_execution
    @log_exceptions
    async def process_document(self, file_path: Path) -> list[dict]:
        """
        Process a document file (image or PDF).
        Returns list of {page_number, raw_text, confidence, processing_time_ms}.
        """
        suffix = file_path.suffix.lower()
        if suffix == ".pdf":
            images = self._pdf_to_images(file_path)
        else:
            images = [Image.open(file_path).convert("RGB")]

        pages = []
        for idx, image in enumerate(images, start=1):
            preprocessed = self._preprocess(image)
            t0 = time.perf_counter()
            raw_text, confidence = self._strategy.extract(preprocessed)
            elapsed_ms = (time.perf_counter() - t0) * 1000
            pages.append(
                {
                    "page_number": idx,
                    "raw_text": raw_text,
                    "confidence": confidence,
                    "processing_time_ms": round(elapsed_ms, 2),
                }
            )
            log.info(
                f"OCR page {idx}/{len(images)} | "
                f"engine={self.engine_name} | "
                f"chars={len(raw_text)} | "
                f"confidence={confidence:.2f if confidence else 'N/A'} | "
                f"time={elapsed_ms:.1f}ms"
            )
        return pages

    # ── Private helpers ───────────────────────────────────────────

    @staticmethod
    def _pdf_to_images(file_path: Path) -> list[Image.Image]:
        try:
            from pdf2image import convert_from_path
            return convert_from_path(str(file_path), dpi=300)
        except ImportError as e:
            raise OCREngineNotAvailableException("pdf2image not installed", cause=e)
        except Exception as e:
            raise OCRException(f"PDF to image conversion failed: {e}", cause=e)

    @staticmethod
    def _preprocess(image: Image.Image) -> Image.Image:
        """Basic pre-processing: grayscale + resize if too small."""
        import cv2
        import numpy as np

        img = image.convert("RGB")
        arr = np.array(img)
        gray = cv2.cvtColor(arr, cv2.COLOR_RGB2GRAY)

        # Upscale small images for better OCR
        h, w = gray.shape
        if w < 1000:
            scale = 1000 / w
            gray = cv2.resize(gray, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)

        # Denoise
        gray = cv2.fastNlMeansDenoising(gray, h=10)

        return Image.fromarray(gray)
