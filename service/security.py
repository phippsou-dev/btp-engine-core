"""Security checks for HTTP service."""

import os
from fastapi import HTTPException


def verify_token(authorization: str, expected_token: str):
    """Verify Bearer token."""
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header required")
    
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization format")
    
    token = authorization[7:]  # Remove "Bearer "
    
    if token != expected_token:
        raise HTTPException(status_code=401, detail="Invalid token")


def check_guardrails_startup():
    """Check guardrails at startup - fail-closed."""
    forbidden_enabled = [
        "OPENAI_ENABLED",
        "GPT_ENABLED",
        "GEMINI_ENABLED",
        "VISION_API_ENABLED",
        "LOVABLE_GATEWAY_ENABLED",
        "DB_WRITES_ENABLED",
        "DST_PUSH_ENABLED",
        "PROD_ACCESS_ENABLED",
    ]
    
    for var in forbidden_enabled:
        value = os.getenv(var, "false").lower()
        if value in ("true", "1", "yes"):
            raise RuntimeError(f"FAIL-CLOSED: {var} is enabled - service cannot start")
    
    max_cost = float(os.getenv("MAX_COST_USD", "0.0"))
    if max_cost > 0:
        raise RuntimeError(f"FAIL-CLOSED: MAX_COST_USD={max_cost} > 0 - service cannot start")