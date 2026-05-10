"""Test guardrails module."""

import pytest
from btp_engine.guardrails import (
    SafetyChecker,
    CostTracker,
    GuardrailViolation,
    SafetyViolationError,
    CostLimitExceededError,
    check_guardrails,
)


def test_safety_checker_violations():
    """Test safety checker detects violations."""
    checker = SafetyChecker()
    assert not checker.check_file_safety("/nonexistent.pdf")
    assert len(checker.violations) > 0


def test_cost_tracker():
    """Test cost tracking with non-zero max."""
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


def test_guardrail_openai_call():
    """Test that openai_call is forbidden."""
    with pytest.raises(GuardrailViolation):
        check_guardrails("openai_call")


def test_guardrail_gpt_call():
    """Test that gpt_call is forbidden."""
    with pytest.raises(GuardrailViolation):
        check_guardrails("gpt_call")


def test_guardrail_gemini_call():
    """Test that gemini_call is forbidden."""
    with pytest.raises(GuardrailViolation):
        check_guardrails("gemini_call")


def test_guardrail_vision_api_call():
    """Test that vision_api_call is forbidden."""
    with pytest.raises(GuardrailViolation):
        check_guardrails("vision_api_call")


def test_guardrail_lovable_gateway_call():
    """Test that lovable_gateway_call is forbidden."""
    with pytest.raises(GuardrailViolation):
        check_guardrails("lovable_gateway_call")


def test_guardrail_db_write():
    """Test that db_write is forbidden."""
    with pytest.raises(GuardrailViolation):
        check_guardrails("db_write")


def test_guardrail_dst_push():
    """Test that dst_push is forbidden."""
    with pytest.raises(GuardrailViolation):
        check_guardrails("dst_push")


def test_guardrail_prod_access():
    """Test that prod_access is forbidden."""
    with pytest.raises(GuardrailViolation):
        check_guardrails("prod_access")


def test_guardrail_external_cost():
    """Test that external_cost with cost > 0 is forbidden."""
    with pytest.raises(GuardrailViolation):
        check_guardrails("external_cost", cost_usd=0.01)


def test_guardrail_unknown_action():
    """Test that unknown actions are forbidden (fail-closed)."""
    with pytest.raises(GuardrailViolation):
        check_guardrails("unknown_action")


def test_cost_tracker_zero_max():
    """Test that CostTracker with max=0 rejects any cost."""
    tracker = CostTracker(max_cost_usd=0.0)
    
    with pytest.raises(GuardrailViolation):
        tracker.add_cost("op1", 0.01)


def test_cost_tracker_initial_cost():
    """Test that CostTracker starts at 0."""
    tracker = CostTracker(max_cost_usd=0.0)
    assert tracker.get_cost() == 0.0


def test_guardrail_allowed_action():
    """Test that explicitly allowed actions pass."""
    assert check_guardrails("file_read") is True
    assert check_guardrails("file_parse") is True
    assert check_guardrails("text_clean") is True