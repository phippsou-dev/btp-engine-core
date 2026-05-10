"""Test analysis module."""

import pytest
from btp_engine.analysis import ProblemDetector, FlagDetector


def test_problem_detector():
    """Test problem detection."""
    detector = ProblemDetector()
    text = "Facture avec montant TTC: 0€"
    problems = detector.detect(text, "facture")
    assert len(problems) > 0
    assert any(p["severity"] == "critical" for p in problems)


def test_flag_detector():
    """Test flag detection."""
    detector = FlagDetector()
    text = "Document non signé et incomplet"
    flags = detector.detect(text)
    assert len(flags) > 0