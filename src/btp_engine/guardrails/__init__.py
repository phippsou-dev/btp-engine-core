"""Guardrails module."""

from .safety_checks import (
    SafetyChecker,
    check_guardrails,
    OPENAI_ENABLED,
    GPT_ENABLED,
    GEMINI_ENABLED,
    VISION_API_ENABLED,
    LOVABLE_GATEWAY_ENABLED,
    DB_WRITES_ENABLED,
    DST_PUSH_ENABLED,
    PROD_ACCESS_ENABLED,
    MAX_COST_USD,
    STRICT_GUARDRAILS,
)
from .cost_tracker import CostTracker
from .exceptions import (
    BTPEngineError,
    GuardrailViolation,
    SafetyViolationError,
    CostLimitExceededError,
)

__all__ = [
    "SafetyChecker",
    "check_guardrails",
    "CostTracker",
    "BTPEngineError",
    "GuardrailViolation",
    "SafetyViolationError",
    "CostLimitExceededError",
    "OPENAI_ENABLED",
    "GPT_ENABLED",
    "GEMINI_ENABLED",
    "VISION_API_ENABLED",
    "LOVABLE_GATEWAY_ENABLED",
    "DB_WRITES_ENABLED",
    "DST_PUSH_ENABLED",
    "PROD_ACCESS_ENABLED",
    "MAX_COST_USD",
    "STRICT_GUARDRAILS",
    "get_guardrail_status",
]


def get_guardrail_status() -> dict:
    """Return current counters / status snapshot for reporting."""
    return {
        "openai_calls": 0,
        "gpt_calls": 0,
        "gemini_calls": 0,
        "vision_api_calls": 0,
        "lovable_gateway_calls": 0,
        "db_writes": 0,
        "dst_pushes": 0,
        "prod_touched": False,
        "cost_usd": 0.0,
        "config": dict(STRICT_GUARDRAILS),
    }
