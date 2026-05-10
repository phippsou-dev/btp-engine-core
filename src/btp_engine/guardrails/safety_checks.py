"""Safety checks for BTP Engine operations - Fail-closed guardrails."""

import os
from pathlib import Path
from typing import Dict, List, Optional
from .exceptions import SafetyViolationError, GuardrailViolation


STRICT_GUARDRAILS = {
    "openai_enabled": False,
    "gpt_enabled": False,
    "gemini_enabled": False,
    "vision_api_enabled": False,
    "lovable_gateway_enabled": False,
    "db_writes_enabled": False,
    "dst_push_enabled": False,
    "prod_access_enabled": False,
    "max_cost_usd": 0.0,
}

OPENAI_ENABLED = STRICT_GUARDRAILS["openai_enabled"]
GPT_ENABLED = STRICT_GUARDRAILS["gpt_enabled"]
GEMINI_ENABLED = STRICT_GUARDRAILS["gemini_enabled"]
VISION_API_ENABLED = STRICT_GUARDRAILS["vision_api_enabled"]
LOVABLE_GATEWAY_ENABLED = STRICT_GUARDRAILS["lovable_gateway_enabled"]
DB_WRITES_ENABLED = STRICT_GUARDRAILS["db_writes_enabled"]
DST_PUSH_ENABLED = STRICT_GUARDRAILS["dst_push_enabled"]
PROD_ACCESS_ENABLED = STRICT_GUARDRAILS["prod_access_enabled"]
MAX_COST_USD = STRICT_GUARDRAILS["max_cost_usd"]


FORBIDDEN_ACTIONS = {
    "openai_call",
    "gpt_call",
    "gemini_call",
    "vision_api_call",
    "lovable_gateway_call",
    "db_write",
    "dst_push",
    "prod_access",
    "external_cost",
}


def check_guardrails(action: str, cost_usd: float = 0.0) -> bool:
    """Check if action is allowed under strict guardrails.
    
    Args:
        action: Action to check
        cost_usd: Cost associated with action
        
    Returns:
        True if allowed
        
    Raises:
        GuardrailViolation: If action is forbidden or cost exceeds limit
    """
    # Check cost limit
    if cost_usd > 0.0:
        raise GuardrailViolation(f"Cost guardrail violated: {cost_usd} USD > 0.0 USD")
    
    # Fail-closed: any forbidden action raises
    if action in FORBIDDEN_ACTIONS:
        raise GuardrailViolation(f"Action '{action}' is forbidden by guardrails")
    
    # Fail-closed: unknown actions are forbidden
    # Only explicitly allowed actions can pass
    allowed_actions = {
        "file_read",
        "file_parse",
        "text_clean",
        "pattern_match",
        "local_classify",
        "local_analyze",
    }
    
    if action not in allowed_actions:
        raise GuardrailViolation(f"Unknown action '{action}' is forbidden (fail-closed)")
    
    return True


class SafetyChecker:
    """Validates safety constraints before operations."""
    
    FORBIDDEN_EXTENSIONS = {".exe", ".dll", ".so", ".dylib", ".bat", ".sh", ".cmd"}
    MAX_FILE_SIZE_MB = 100
    
    def __init__(self):
        self.violations: List[str] = []
    
    def check_file_safety(self, filepath: str) -> bool:
        """Check if file is safe to process."""
        path = Path(filepath)
        
        if not path.exists():
            self.violations.append(f"File does not exist: {filepath}")
            return False
        
        if not path.is_file():
            self.violations.append(f"Not a file: {filepath}")
            return False
        
        if path.suffix.lower() in self.FORBIDDEN_EXTENSIONS:
            self.violations.append(f"Forbidden extension: {path.suffix}")
            return False
        
        size_mb = path.stat().st_size / (1024 * 1024)
        if size_mb > self.MAX_FILE_SIZE_MB:
            self.violations.append(f"File too large: {size_mb:.1f}MB > {self.MAX_FILE_SIZE_MB}MB")
            return False
        
        return True
    
    def check_directory_safety(self, dirpath: str) -> bool:
        """Check if directory is safe to process."""
        path = Path(dirpath)
        
        if not path.exists():
            self.violations.append(f"Directory does not exist: {dirpath}")
            return False
        
        if not path.is_dir():
            self.violations.append(f"Not a directory: {dirpath}")
            return False
        
        return True
    
    def enforce(self) -> None:
        """Raise exception if violations exist."""
        if self.violations:
            raise SafetyViolationError("; ".join(self.violations))
    
    def reset(self) -> None:
        """Clear violations."""
        self.violations.clear()