"""Test guardrails module."""

import pytest
from btp_engine.guardrails import SafetyChecker, CostTracker, SafetyViolationError, CostLimitExceededError


def test_safety_checker_violations():
    """Test safety checker detects violations."""
    checker = SafetyChecker()
    assert not checker.check_file_safety("/nonexistent.pdf")
    assert len(checker.violations) > 0


def test_cost_tracker():
    """Test cost tracking."""
    tracker = CostTracker(max_cost_usd=10.0)
    tracker.add_cost("operation1", 5.0)
    assert tracker.get_cost() == 5.0
    assert tracker.get_remaining() == 5.0


def test_cost_limit_exceeded():
    """Test cost limit enforcement."""
    tracker = CostTracker(max_cost_usd=5.0)
    tracker.add_cost("op1", 3.0)
    
    with pytest.raises(CostLimitExceededError):
        tracker.add_cost("op2", 3.0)