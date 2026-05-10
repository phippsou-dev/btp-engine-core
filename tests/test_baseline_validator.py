"""Test baseline validator."""

import pytest
from btp_engine.scoring import BaselineValidator


def test_validator_pass():
    """Test validation passes with good scores."""
    validator = BaselineValidator()
    scores = {
        "extraction_quality": 0.8,
        "classification_confidence": 0.7,
        "completeness": 0.9,
        "overall_quality": 0.8,
    }
    result = validator.validate(scores)
    assert result["passed"] is True
    assert len(result["failures"]) == 0


def test_validator_fail():
    """Test validation fails with low scores."""
    validator = BaselineValidator()
    scores = {
        "extraction_quality": 0.3,
        "classification_confidence": 0.2,
        "completeness": 0.4,
        "overall_quality": 0.3,
    }
    result = validator.validate(scores)
    assert result["passed"] is False
    assert len(result["failures"]) > 0