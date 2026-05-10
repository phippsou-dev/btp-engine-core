"""Runner for BTP Engine core."""

import os
import json
import tempfile
import shutil
import subprocess
from pathlib import Path
from typing import Dict, Any, Tuple
from zipfile import ZipFile


def extract_uploaded_file(file_content: bytes, filename: str) -> Path:
    """
    Extract uploaded file to a temporary directory.
    
    Args:
        file_content: File content bytes
        filename: Original filename
        
    Returns:
        Path to temporary input directory
    """
    tmp_input = Path(tempfile.mkdtemp(prefix="btp_engine_input_"))
    
    if filename.lower().endswith('.zip'):
        # Extract ZIP
        zip_path = tmp_input / "upload.zip"
        zip_path.write_bytes(file_content)
        
        with ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(tmp_input)
        
        # Remove the ZIP file itself
        zip_path.unlink()
    elif filename.lower().endswith('.pdf'):
        # Copy PDF
        pdf_path = tmp_input / filename
        pdf_path.write_bytes(file_content)
    else:
        shutil.rmtree(tmp_input)
        raise ValueError(f"Unsupported file type: {filename}")
    
    return tmp_input


def run_engine(input_dir: Path, mode: str) -> Tuple[Dict[str, Any], Path]:
    """
    Run the BTP Engine core.
    
    Args:
        input_dir: Input directory with PDFs
        mode: Run mode (must be 'dry_run')
        
    Returns:
        Tuple of (result dict, output directory path)
    """
    if mode != "dry_run":
        raise ValueError(f"Only 'dry_run' mode is allowed, got: {mode}")
    
    # Create temporary output directory
    tmp_output = Path(tempfile.mkdtemp(prefix="btp_engine_output_"))
    
    # Get repository root
    repo_root = Path(__file__).parent.parent
    
    # Run the engine
    cmd = [
        "python",
        str(repo_root / "scripts" / "run_engine.py"),
        "--input", str(input_dir),
        "--output", str(tmp_output),
        "--dry-run"
    ]
    
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=str(repo_root)
    )
    
    if result.returncode != 0:
        raise RuntimeError(f"Engine failed: {result.stderr}")
    
    return parse_engine_output(tmp_output), tmp_output


def parse_engine_output(output_dir: Path) -> Dict[str, Any]:
    """
    Parse engine output and build response.
    
    Args:
        output_dir: Engine output directory
        
    Returns:
        Response dictionary
    """
    # Read all output files
    files = {}
    
    file_mapping = {
        "inventory.json": "inventory.json",
        "extraction_report.json": "extraction_report.json",
        "classification_report.json": "classification_report.json",
        "problems.json": "problems.json",
        "candidate_tasks.json": "candidate_tasks.json",
        "candidate_tasks.csv": "candidate_tasks.csv",
        "dst_mapping_report.json": "dst_mapping_report.json",
        "quality_score.json": "quality_score.json",
        "guardrails_report.json": "guardrails_report.json",
        "final_report.md": "final_report.md",
        "per_doc.json": "per_doc.json"
    }
    
    for key, filename in file_mapping.items():
        file_path = output_dir / filename
        if file_path.exists():
            files[key] = file_path.read_text(encoding='utf-8')
        else:
            files[key] = ""
    
    # Parse key metrics
    inventory = {}
    quality_score = {}
    guardrails = {}
    candidate_tasks = {}
    dst_mapping = {}
    
    if files.get("inventory.json"):
        try:
            inventory = json.loads(files["inventory.json"])
        except:
            pass
    
    if files.get("quality_score.json"):
        try:
            quality_score = json.loads(files["quality_score.json"])
        except:
            pass
    
    if files.get("guardrails_report.json"):
        try:
            guardrails = json.loads(files["guardrails_report.json"])
        except:
            pass
    
    if files.get("candidate_tasks.json"):
        try:
            candidate_tasks = json.loads(files["candidate_tasks.json"])
        except:
            pass
    
    if files.get("dst_mapping_report.json"):
        try:
            dst_mapping = json.loads(files["dst_mapping_report.json"])
        except:
            pass
    
    # Get repo SHA
    repo_root = Path(__file__).parent.parent
    try:
        sha_result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            cwd=str(repo_root)
        )
        repo_sha = sha_result.stdout.strip() if sha_result.returncode == 0 else "unknown"
    except:
        repo_sha = "unknown"
    
    # Build response
    response = {
        "engine_version": "BTP_ENGINE_CORE_V3_REAL_REGRESSION_STRICT_RELEASE_FROZEN",
        "repo_sha": repo_sha,
        "pdf_count": inventory.get("pdf_count", 0),
        "task_candidates_count": len(candidate_tasks.get("candidates", [])),
        "dst_mapping_count": dst_mapping.get("dst_mapping_count", 0),
        "missing_expected_flags_total": quality_score.get("missing_expected_flags_total", 0),
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
            "cost_usd": guardrails.get("cost_usd", 0.0)
        },
        "files": files
    }
    
    return response
