"""Pydantic schemas for BTP Engine HTTP Service."""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """Health check response."""
    ok: bool = True
    service: str = "btp-engine-core"
    mode: str = "deterministic"
    guardrails_ok: bool = True


class GuardrailsCounters(BaseModel):
    """Guardrails counters to ensure no forbidden operations."""
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
    """Response from /run endpoint."""
    engine_version: str
    repo_sha: str
    pdf_count: int
    task_candidates_count: int
    dst_mapping_count: int
    missing_expected_flags_total: int
    quality_score: Dict[str, Any]
    guardrails_counters: GuardrailsCounters
    files: Dict[str, str]


class JobStartRequest(BaseModel):
    """Request to start an async job."""
    run_id: str
    source_url: str
    source_filename: str
    mode: str = "dry_run"
    callback_url: str
    callback_token: str
    workspace_id: Optional[str] = None
    project_id: Optional[str] = None


class JobStartResponse(BaseModel):
    """Response from job start."""
    ok: bool = True
    run_id: str
    status: str = "queued"


class JobStatusResponse(BaseModel):
    """Response from job status check."""
    ok: bool = True
    run_id: str
    status: str
    error: Optional[str] = None
