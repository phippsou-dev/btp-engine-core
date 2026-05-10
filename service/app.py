"""FastAPI HTTP service for BTP Engine Core - Lovable compatible."""

import os
import sys
import json
import base64
import tempfile
import shutil
import subprocess
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, File, UploadFile, Header, HTTPException, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from .security import verify_token, check_guardrails_startup
from .schemas import HealthResponse, RunResponse

# Add src to path for btp_engine imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from btp_engine.guardrails import STRICT_GUARDRAILS

# Check guardrails at startup
check_guardrails_startup()

app = FastAPI(
    title="BTP Engine Core HTTP Service",
    description="Document analysis engine for MyHome/Lovable integration",
    version="1.0.0",
)

# CORS for Lovable
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", response_model=HealthResponse)
async def health():
    """Health check endpoint."""
    return {
        "ok": True,
        "service": "btp-engine-core",
        "mode": "deterministic",
        "guardrails_ok": all(
            not STRICT_GUARDRAILS[k] 
            for k in STRICT_GUARDRAILS 
            if k != "max_cost_usd"
        ) and STRICT_GUARDRAILS["max_cost_usd"] == 0.0,
    }


@app.post("/run")
async def run_engine(
    file: UploadFile = File(...),
    mode: str = Form(...),
    authorization: Optional[str] = Header(None),
):
    """Run BTP Engine on uploaded PDF or ZIP."""
    
    # Verify token if configured
    token = os.getenv("BTP_ENGINE_TOKEN")
    if token:
        verify_token(authorization, token)
    
    # Only dry_run allowed
    if mode != "dry_run":
        raise HTTPException(status_code=400, detail="Only mode=dry_run is allowed")
    
    # Create temp directories
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)
        input_dir = tmpdir_path / "input"
        output_dir = tmpdir_path / "output"
        input_dir.mkdir()
        output_dir.mkdir()
        
        # Save uploaded file
        upload_path = tmpdir_path / file.filename
        with open(upload_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # Handle ZIP or PDF
        if file.filename.lower().endswith(".zip"):
            import zipfile
            with zipfile.ZipFile(upload_path, 'r') as zip_ref:
                zip_ref.extractall(input_dir)
        elif file.filename.lower().endswith(".pdf"):
            shutil.copy(upload_path, input_dir / file.filename)
        else:
            raise HTTPException(status_code=400, detail="Only PDF or ZIP files accepted")
        
        # Run engine
        script_path = Path(__file__).parent.parent / "scripts" / "run_engine.py"
        
        try:
            result = subprocess.run(
                [
                    sys.executable,
                    str(script_path),
                    "--input", str(input_dir),
                    "--output", str(output_dir),
                    "--dry-run",
                ],
                capture_output=True,
                text=True,
                timeout=300,
            )
            
            if result.returncode != 0:
                raise HTTPException(
                    status_code=500,
                    detail=f"Engine failed: {result.stderr}"
                )
        except subprocess.TimeoutExpired:
            raise HTTPException(status_code=500, detail="Engine timeout")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Engine error: {str(e)}")
        
        # Read output files
        files_data = {}
        expected_files = [
            "inventory.json",
            "extraction_report.json",
            "classification_report.json",
            "problems.json",
            "candidate_tasks.json",
            "candidate_tasks.csv",
            "dst_mapping_report.json",
            "quality_score.json",
            "guardrails_report.json",
            "final_report.md",
            "per_doc.json",
        ]
        
        for fname in expected_files:
            fpath = output_dir / fname
            if fpath.exists():
                content = fpath.read_text(encoding='utf-8')
                files_data[fname] = content
            else:
                files_data[fname] = None
        
        # Parse key metrics
        guardrails = {}
        pdf_count = 0
        task_candidates_count = 0
        dst_mapping_count = 0
        quality_score = {}
        missing_flags_total = 0
        
        if files_data.get("guardrails_report.json"):
            guardrails = json.loads(files_data["guardrails_report.json"])
        
        if files_data.get("per_doc.json"):
            per_doc = json.loads(files_data["per_doc.json"])
            pdf_count = len(per_doc)
            missing_flags_total = sum(
                len(d.get("missing_expected_flags", [])) for d in per_doc
            )
        
        if files_data.get("candidate_tasks.json"):
            tasks = json.loads(files_data["candidate_tasks.json"])
            task_candidates_count = len(tasks)
        
        if files_data.get("dst_mapping_report.json"):
            dst = json.loads(files_data["dst_mapping_report.json"])
            dst_mapping_count = len(dst) if isinstance(dst, list) else 0
        
        if files_data.get("quality_score.json"):
            quality_score = json.loads(files_data["quality_score.json"])
        
        # Get repo info
        try:
            repo_sha = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=Path(__file__).parent.parent,
                capture_output=True,
                text=True,
            ).stdout.strip()
        except:
            repo_sha = "unknown"
        
        # Build response
        response = {
            "engine_version": "1.0.0",
            "repo_sha": repo_sha,
            "pdf_count": pdf_count,
            "task_candidates_count": task_candidates_count,
            "dst_mapping_count": dst_mapping_count,
            "missing_expected_flags_total": missing_flags_total,
            "quality_score": quality_score,
            "guardrails_counters": {
                "openai_calls": guardrails.get("openai_calls", 0),
                "gpt_calls": guardrails.get("gpt_calls", 0),
                "gemini_calls": guardrails.get("gemini_calls", 0),
                "vision_api_calls": guardrails.get("vision_api_calls", 0),
                "lovable_gateway_calls": guardrails.get("lovable_gateway_calls", 0),
                "db_writes": guardrails.get("db_writes", 0),
                "dst_pushes": guardrails.get("dst_pushes", 0),
                "prod_touched": guardrails.get("prod_touched", False),
                "cost_usd": guardrails.get("cost_usd", 0.0),
            },
            "files": files_data,
        }
        
        return JSONResponse(content=response)