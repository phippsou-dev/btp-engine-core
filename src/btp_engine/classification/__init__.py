"""Classification module - Document type classification."""

from .document_classifier import DocumentClassifier
from .class_patterns import ClassificationPatterns
from .class_priority import ClassificationPriority

__all__ = ["DocumentClassifier", "ClassificationPatterns", "ClassificationPriority"]