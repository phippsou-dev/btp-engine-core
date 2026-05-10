"""Test classification module."""

import pytest
from btp_engine.classification import DocumentClassifier, ClassificationPriority


def test_classifier_facture():
    """Test invoice classification."""
    classifier = DocumentClassifier()
    text = "FACTURE N° 12345\nMontant HT: 1000€\nTVA: 200€\nMontant TTC: 1200€"
    doc_type = classifier.classify(text)
    assert doc_type == "facture"


def test_classifier_unknown():
    """Test unknown document classification."""
    classifier = DocumentClassifier()
    text = "Random text with no patterns"
    doc_type = classifier.classify(text)
    assert doc_type == "unknown"


def test_classification_priority():
    """Test priority mapping."""
    priority = ClassificationPriority.from_doc_type("permis")
    assert priority == ClassificationPriority.CRITICAL