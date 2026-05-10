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


def _filename_hint(fname_lc: str) -> str:
    """Return a strong filename-based class hint, or '' if none."""
    if "notice" in fname_lc and ("secur" in fname_lc or "habitation" in fname_lc):
        return "NOTICE_SECURITE_HABITATION"
    if "dpe" in fname_lc:
        return "DPE_PROJETE"
    if "edl" in fname_lc:
        return "EDL_AVANT_PROJET"
    if ("piece" in fname_lc and "pc" in fname_lc) or "facade" in fname_lc or "plan_pc" in fname_lc or "graphic" in fname_lc:
        return "PLAN_GRAPHIC_PC_FACADES"
    return ""


def classify_document(filename: str, text: str) -> Dict:
    """Functional wrapper used by scripts/run_engine.py.

    Filename hint is a STRONG override when filename clearly indicates type.
    Pattern scoring is used as confirmation/fallback.
    """
    classifier = DocumentClassifier()
    result = classifier.classify_with_confidence(text or "")
    fname_lc = (filename or "").lower()
    hint = _filename_hint(fname_lc)
    scores = result.get("scores", {}) or {}
    if hint:
        # If hint type has any pattern match OR pattern classifier is ambiguous, force hint
        hint_score = scores.get(hint, 0)
        if hint_score >= 1 or result["type"] == "unknown" or result["confidence"] < 0.6:
            result["type"] = hint
            total = sum(scores.values()) or 1
            result["confidence"] = max(round(hint_score / total, 2), 0.5)
    return {
        "filename": filename,
        "class": result["type"],
        "classified_as": result["type"],
        "confidence": result["confidence"],
        "priority": int(result["priority"]),
        "scores": result["scores"],
    }
