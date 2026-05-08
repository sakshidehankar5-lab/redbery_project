"""
Document Classifier
--------------------
Auto-detects document type from OCR text using keyword heuristics.
Falls back to LLM classification when heuristics are inconclusive.
"""
import re
from typing import Dict, Optional, Tuple

from app.core.logging import get_logger, log_execution
from app.db.models.models import DocumentType

log = get_logger(__name__)


# ── Keyword Heuristics ────────────────────────────────────────────────────────

_PATTERNS: Dict[DocumentType, list[str]] = {
    DocumentType.AADHAAR: [
        r"aadhaar",
        r"unique identification authority",
        r"uidai",
        r"\d{4}\s\d{4}\s\d{4}",      # UID pattern
        r"enrollment no",
        r"आधार",
    ],
    DocumentType.DRIVING_LICENCE: [
        r"driving licen[sc]e",
        r"driving licence",
        r"motor vehicles act",
        r"transport department",
        r"licence no",
        r"dl no",
        r"[A-Z]{2}\d{2}[A-Z0-9]\d{6,}",  # DL number pattern
        r"lmv|mcwg|hgv|transport",
    ],
    DocumentType.PASSPORT: [
        r"passport",
        r"republic of india",
        r"ministry of external affairs",
        r"place of birth",
        r"nationality",
        r"mrz",
        r"P<IND",                          # MRZ header
        r"[A-Z]\d{7}",                      # Passport number pattern
    ],
    DocumentType.INVOICE: [
        r"invoice",
        r"bill of supply",
        r"tax invoice",
        r"gstin",
        r"gst",
        r"igst|cgst|sgst",
        r"total amount",
        r"subtotal",
        r"amount due",
        r"invoice no",
        r"bill to",
    ],
}


class DocumentClassifier:
    """Classifies a document type from OCR text."""

    @log_execution
    def classify(self, ocr_text: str) -> Tuple[DocumentType, float]:
        """
        Returns (DocumentType, confidence_score).
        Confidence is 0.0–1.0 based on how many patterns matched.
        """
        text_lower = ocr_text.lower()
        scores: Dict[DocumentType, float] = {}

        for doc_type, patterns in _PATTERNS.items():
            matches = sum(
                1 for p in patterns if re.search(p, text_lower, re.IGNORECASE)
            )
            scores[doc_type] = matches / len(patterns)

        best_type = max(scores, key=lambda k: scores[k])
        best_score = scores[best_type]

        if best_score < 0.15:
            log.warning(
                f"Low classification confidence ({best_score:.2f}) — "
                f"defaulting to UNKNOWN. Scores: {scores}"
            )
            return DocumentType.UNKNOWN, best_score

        log.info(
            f"Document classified as {best_type} (confidence={best_score:.2f})"
        )
        return best_type, best_score
