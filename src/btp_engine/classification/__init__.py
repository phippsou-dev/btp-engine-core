"""Classification module - Document type classification."""

from typing import Dict

from .document_classifier import DocumentClassifier
from .class_patterns import ClassificationPatterns
from .class_priority import ClassificationPriority

__all__ = [
    "DocumentClassifier",
    "ClassificationPatterns",
    "ClassificationPriority",
    "classify_document",
]


def classify_document(filename: str, text: str) -> Dict:
    """Functional wrapper used by scripts/run_engine.py."""
    classifier = DocumentClassifier()
    result = classifier.classify_with_confidence(text or "")
    fname_lc = (filename or "").lower()
    # Filename-based hint as fallback / boost
    if result["type"] == "unknown" or result["confidence"] < 0.15:
        if "notice" in fname_lc and "secur" in fname_lc:
            result["type"] = "NOTICE_SECURITE_HABITATION"
        elif "dpe" in fname_lc:
            result["type"] = "DPE_PROJETE"
        elif "edl" in fname_lc:
            result["type"] = "EDL_AVANT_PROJET"
        elif ("pc" in fname_lc and ("piece" in fname_lc or "facade" in fname_lc)) or "plan" in fname_lc:
            result["type"] = "PLAN_GRAPHIC_PC_FACADES"
    return {
        "filename": filename,
        "class": result["type"],
        "classified_as": result["type"],
        "confidence": result["confidence"],
        "priority": int(result["priority"]),
        "scores": result["scores"],
    }
