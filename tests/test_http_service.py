"""Tests for BTP Engine HTTP Service."""

import os
import json
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock
import pytest
from fastapi.testclient import TestClient

from service.app import app

client = TestClient(app)


def test_health_endpoint():
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    
    data = response.json()
    assert data["ok"] is True
    assert data["service"] == "btp-engine-core"
    assert data["mode"] == "deterministic"
    assert data["guardrails_ok"] is True


def test_run_without_token_when_required():
    """Test POST /run without token when BTP_ENGINE_TOKEN is set."""
    with patch.dict(os.environ, {"BTP_ENGINE_TOKEN": "test-token"}):
        response = client.post(
            "/run",
            data={"mode": "dry_run"},
            files={"file": ("test.pdf", b"fake pdf content", "application/pdf")}
        )
        assert response.status_code == 401
        assert "Authorization token required" in response.json()["detail"]


def test_run_with_invalid_token():
    """Test POST /run with invalid token."""
    with patch.dict(os.environ, {"BTP_ENGINE_TOKEN": "test-token"}):
        response = client.post(
            "/run",
            data={"mode": "dry_run"},
            files={"file": ("test.pdf", b"fake pdf content", "application/pdf")},
            headers={"Authorization": "Bearer wrong-token"}
        )
        assert response.status_code == 403
        assert "Invalid authorization token" in response.json()["detail"]


def test_run_refuses_non_dry_run_mode():
    """Test POST /run refuses modes other than dry_run."""
    response = client.post(
        "/run",
        data={"mode": "production"},
        files={"file": ("test.pdf", b"fake pdf content", "application/pdf")}
    )
    assert response.status_code == 400
    assert "Only 'dry_run' mode is allowed" in response.json()["detail"]


def test_run_refuses_unsupported_file_type():
    """Test POST /run refuses unsupported file types."""
    response = client.post(
        "/run",
        data={"mode": "dry_run"},
        files={"file": ("test.txt", b"fake content", "text/plain")}
    )
    assert response.status_code == 400
    assert "Only PDF or ZIP files are allowed" in response.json()["detail"]


def test_run_accepts_multipart_file():
    """Test POST /run accepts multipart file field."""
    mock_result = {
        "engine_version": "BTP_ENGINE_CORE_V3_REAL_REGRESSION_STRICT_RELEASE_FROZEN",
        "repo_sha": "abc123",
        "pdf_count": 1,
        "task_candidates_count": 5,
        "dst_mapping_count": 5,
        "missing_expected_flags_total": 0,
        "quality_score": {},
        "guardrails_counters": {
            "openai_calls": 0,
            "gpt_calls": 0,
            "gemini_calls": 0,
            "vision_api_calls": 0,
            "lovable_gateway_calls": 0,
            "db_writes": 0,
            "dst_pushes": 0,
            "prod_touched": False,
            "cost_usd": 0.0
        },
        "files": {
            "inventory.json": "{}",
            "extraction_report.json": "{}",
            "classification_report.json": "{}",
            "problems.json": "{}",
            "candidate_tasks.json": "{}",
            "candidate_tasks.csv": "",
            "dst_mapping_report.json": "{}",
            "quality_score.json": "{}",
            "guardrails_report.json": "{}",
            "final_report.md": "",
            "per_doc.json": "{}"
        }
    }
    
    with patch("service.app.extract_uploaded_file") as mock_extract, \
         patch("service.app.run_engine") as mock_run:
        
        mock_extract.return_value = Path(tempfile.mkdtemp())
        mock_run.return_value = (mock_result, Path(tempfile.mkdtemp()))
        
        response = client.post(
            "/run",
            data={"mode": "dry_run"},
            files={"file": ("test.pdf", b"fake pdf content", "application/pdf")}
        )
        
        assert response.status_code == 200


def test_run_returns_expected_structure():
    """Test POST /run returns expected output structure."""
    mock_result = {
        "engine_version": "BTP_ENGINE_CORE_V3_REAL_REGRESSION_STRICT_RELEASE_FROZEN",
        "repo_sha": "abc123",
        "pdf_count": 1,
        "task_candidates_count": 5,
        "dst_mapping_count": 5,
        "missing_expected_flags_total": 0,
        "quality_score": {},
        "guardrails_counters": {
            "openai_calls": 0,
            "gpt_calls": 0,
            "gemini_calls": 0,
            "vision_api_calls": 0,
            "lovable_gateway_calls": 0,
            "db_writes": 0,
            "dst_pushes": 0,
            "prod_touched": False,
            "cost_usd": 0.0
        },
        "files": {
            "inventory.json": "{}",
            "extraction_report.json": "{}",
            "classification_report.json": "{}",
            "problems.json": "{}",
            "candidate_tasks.json": "{}",
            "candidate_tasks.csv": "",
            "dst_mapping_report.json": "{}",
            "quality_score.json": "{}",
            "guardrails_report.json": "{}",
            "final_report.md": "",
            "per_doc.json": "{}"
        }
    }
    
    with patch("service.app.extract_uploaded_file") as mock_extract, \
         patch("service.app.run_engine") as mock_run:
        
        mock_extract.return_value = Path(tempfile.mkdtemp())
        mock_run.return_value = (mock_result, Path(tempfile.mkdtemp()))
        
        response = client.post(
            "/run",
            data={"mode": "dry_run"},
            files={"file": ("test.pdf", b"fake pdf content", "application/pdf")}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Check required keys
        assert "engine_version" in data
        assert "repo_sha" in data
        assert "pdf_count" in data
        assert "task_candidates_count" in data
        assert "dst_mapping_count" in data
        assert "missing_expected_flags_total" in data
        assert "quality_score" in data
        assert "guardrails_counters" in data
        assert "files" in data


def test_run_returns_zero_guardrails():
    """Test POST /run returns all guardrails counters at zero."""
    mock_result = {
        "engine_version": "BTP_ENGINE_CORE_V3_REAL_REGRESSION_STRICT_RELEASE_FROZEN",
        "repo_sha": "abc123",
        "pdf_count": 1,
        "task_candidates_count": 5,
        "dst_mapping_count": 5,
        "missing_expected_flags_total": 0,
        "quality_score": {},
        "guardrails_counters": {
            "openai_calls": 0,
            "gpt_calls": 0,
            "gemini_calls": 0,
            "vision_api_calls": 0,
            "lovable_gateway_calls": 0,
            "db_writes": 0,
            "dst_pushes": 0,
            "prod_touched": False,
            "cost_usd": 0.0
        },
        "files": {
            "inventory.json": "{}",
            "extraction_report.json": "{}",
            "classification_report.json": "{}",
            "problems.json": "{}",
            "candidate_tasks.json": "{}",
            "candidate_tasks.csv": "",
            "dst_mapping_report.json": "{}",
            "quality_score.json": "{}",
            "guardrails_report.json": "{}",
            "final_report.md": "",
            "per_doc.json": "{}"
        }
    }
    
    with patch("service.app.extract_uploaded_file") as mock_extract, \
         patch("service.app.run_engine") as mock_run:
        
        mock_extract.return_value = Path(tempfile.mkdtemp())
        mock_run.return_value = (mock_result, Path(tempfile.mkdtemp()))
        
        response = client.post(
            "/run",
            data={"mode": "dry_run"},
            files={"file": ("test.pdf", b"fake pdf content", "application/pdf")}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        guardrails = data["guardrails_counters"]
        assert guardrails["openai_calls"] == 0
        assert guardrails["gpt_calls"] == 0
        assert guardrails["gemini_calls"] == 0
        assert guardrails["vision_api_calls"] == 0
        assert guardrails["lovable_gateway_calls"] == 0
        assert guardrails["db_writes"] == 0
        assert guardrails["dst_pushes"] == 0
        assert guardrails["prod_touched"] is False
        assert guardrails["cost_usd"] == 0.0
