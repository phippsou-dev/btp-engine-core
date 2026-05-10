"""Pydantic schemas for HTTP service."""

from typing import Dict, Any, Optional
from pydantic import BaseModel


class HealthResponse(BaseModel):
    """Health check response."""
    ok: bool
    service: str
    mode: str
    guardrails_ok: bool


class GuardrailsCounters(BaseModel):
    """Guardrails counters."""
    openai_calls: int = 0
    gpt_calls: int = 0
    gemini_calls: int = 0
    vision_api_calls: int = 0
    lovable_gateway_calls: int = 0
    db_writes: int = 0
    dst_pushes: int = 0
    prod_touched: bool = False
    cost_usd: float = 0.0


class RunResponse(BaseModel):
    """Engine run response."""
    engine_version: str
    repo_sha: str
    pdf_count: int
    task_candidates_count: int
    dst_mapping_count: int
    missing_expected_flags_total: int
    quality_score: Dict[str, Any]
    guardrails_counters: GuardrailsCounters
    files: Dict[str, Optional[str]]