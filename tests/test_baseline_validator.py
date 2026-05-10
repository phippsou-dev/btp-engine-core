"""Test baseline validator."""

import pytest
from btp_engine.scoring import BaselineValidator
from btp_engine.scoring.baseline_validator import BaselineStatus


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


def test_no_pass_without_source():
    """Test that task baseline cannot PASS without source."""
    validator = BaselineValidator()
    candidate = {
        "evidence": "some evidence",
        "source_class": "RAPPORT",
    }
    baseline_item = {
        "type": "TASK_BASELINE",
        "allowed_classes": ["RAPPORT"],
    }
    result = validator.validate_task_baseline(candidate, baseline_item)
    assert result["status"] == BaselineStatus.FAIL
    assert any("source" in str(r).lower() for r in result["reasons"])


def test_no_pass_without_evidence():
    """Test that task baseline cannot PASS without evidence."""
    validator = BaselineValidator()
    candidate = {
        "source_file": "doc.pdf",
        "source_class": "RAPPORT",
    }
    baseline_item = {
        "type": "TASK_BASELINE",
        "allowed_classes": ["RAPPORT"],
    }
    result = validator.validate_task_baseline(candidate, baseline_item)
    assert result["status"] == BaselineStatus.FAIL
    assert any("evidence" in str(r).lower() for r in result["reasons"])


def test_dpe_cannot_prove_cf():
    """Test that DPE cannot prove CF."""
    validator = BaselineValidator()
    candidate = {
        "source_file": "dpe.pdf",
        "evidence": "conformité électrique",
        "source_class": "DPE",
    }
    baseline_item = {
        "type": "TASK_BASELINE",
        "domain": "CF",
        "allowed_classes": ["DPE", "RAPPORT"],
    }
    result = validator.validate_task_baseline(candidate, baseline_item)
    assert result["status"] == BaselineStatus.INCOMPATIBLE_SOURCE
    assert any("forbidden" in str(r).lower() for r in result["reasons"])


def test_crep_cannot_prove_ep():
    """Test that DIAGNOSTIC_PLOMB_CREP cannot prove EP."""
    validator = BaselineValidator()
    candidate = {
        "source_file": "crep.pdf",
        "evidence": "eaux pluviales",
        "source_class": "DIAGNOSTIC_PLOMB_CREP",
    }
    baseline_item = {
        "type": "TASK_BASELINE",
        "domain": "EP",
        "allowed_classes": ["DIAGNOSTIC_PLOMB_CREP", "RAPPORT"],
    }
    result = validator.validate_task_baseline(candidate, baseline_item)
    assert result["status"] == BaselineStatus.INCOMPATIBLE_SOURCE


def test_termites_cannot_prove_facade():
    """Test that DIAGNOSTIC_TERMITES cannot prove façade."""
    validator = BaselineValidator()
    candidate = {
        "source_file": "termites.pdf",
        "evidence": "façade",
        "source_class": "DIAGNOSTIC_TERMITES",
    }
    baseline_item = {
        "type": "TASK_BASELINE",
        "domain": "facade",
        "allowed_classes": ["DIAGNOSTIC_TERMITES", "RAPPORT"],
    }
    result = validator.validate_task_baseline(candidate, baseline_item)
    assert result["status"] == BaselineStatus.INCOMPATIBLE_SOURCE


def test_document_presence_pass():
    """Test document presence PASS with filename + sha256 + class."""
    validator = BaselineValidator()
    document = {
        "filename": "doc.pdf",
        "sha256": "abc123",
        "class": "RAPPORT",
    }
    baseline_item = {
        "type": "DOCUMENT_PRESENCE_BASELINE",
        "allowed_classes": ["RAPPORT"],
    }
    result = validator.validate_document_presence(document, baseline_item)
    assert result["status"] == BaselineStatus.PASS


def test_task_baseline_pass():
    """Test task baseline PASS with all requirements."""
    validator = BaselineValidator()
    candidate = {
        "source_file": "rapport.pdf",
        "evidence": "électrique conforme",
        "source_class": "RAPPORT",
    }
    baseline_item = {
        "type": "TASK_BASELINE",
        "domain": "electricite",
        "allowed_classes": ["RAPPORT"],
        "required_triggers": ["électrique"],
    }
    result = validator.validate_task_baseline(candidate, baseline_item)
    assert result["status"] == BaselineStatus.PASS


def test_missing_trigger_fail():
    """Test that missing trigger causes FAIL."""
    validator = BaselineValidator()
    candidate = {
        "source_file": "rapport.pdf",
        "evidence": "some text",
        "source_class": "RAPPORT",
    }
    baseline_item = {
        "type": "TASK_BASELINE",
        "allowed_classes": ["RAPPORT"],
        "required_triggers": ["électrique", "conforme"],
    }
    result = validator.validate_task_baseline(candidate, baseline_item)
    assert result["status"] == BaselineStatus.FAIL
    assert any("trigger" in str(r).lower() for r in result["reasons"])


def test_incompatible_source():
    """Test incompatible source class."""
    validator = BaselineValidator()
    candidate = {
        "source_file": "doc.pdf",
        "evidence": "some evidence",
        "source_class": "FACTURE",
    }
    baseline_item = {
        "type": "TASK_BASELINE",
        "allowed_classes": ["RAPPORT"],
    }
    result = validator.validate_task_baseline(candidate, baseline_item)
    assert result["status"] == BaselineStatus.INCOMPATIBLE_SOURCE


def test_aggregate_counters_zero_invalid_pass():
    """Test that aggregate counters have zero invalid PASS."""
    validator = BaselineValidator()
    
    candidates = [
        {
            "source_file": "rapport.pdf",
            "evidence": "électrique conforme",
            "source_class": "RAPPORT",
        }
    ]
    
    documents = []
    
    baseline_items = [
        {
            "type": "TASK_BASELINE",
            "domain": "electricite",
            "allowed_classes": ["RAPPORT"],
            "required_triggers": ["électrique"],
        }
    ]
    
    result = validator.validate_all(candidates, documents, baseline_items)
    
    assert result["empty_evidence_pass_count"] == 0
    assert result["wrong_source_class_pass_count"] == 0
    assert result["baseline_pass_strict_count"] > 0