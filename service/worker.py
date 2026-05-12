"""Background worker for async jobs."""

import asyncio
import httpx
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Any

from .jobs import job_manager, JobStatus
from .runner import run_engine


async def download_file(url: str, destination: Path) -> None:
    """Download file from URL to destination."""
    async with httpx.AsyncClient(timeout=300.0) as client:
        async with client.stream("GET", url) as response:
            response.raise_for_status()
            with open(destination, "wb") as f:
                async for chunk in response.aiter_bytes(chunk_size=8192):
                    f.write(chunk)


async def send_callback(
    callback_url: str,
    callback_token: str,
    payload: Dict[str, Any]
) -> None:
    """Send callback to Supabase Edge Function."""
    async with httpx.AsyncClient(timeout=30.0) as client:
        await client.post(
            callback_url,
            json=payload,
            headers={"Authorization": f"Bearer {callback_token}"}
        )


async def process_job(run_id: str) -> None:
    """Process a job in background."""
    job = job_manager.get_job(run_id)
    if not job:
        return
    
    tmp_download = None
    tmp_input = None
    tmp_output = None
    
    try:
        # Update status to running
        job_manager.update_status(run_id, JobStatus.RUNNING)
        
        # Create temp directories
        tmp_download = Path(tempfile.mkdtemp(prefix="btp_download_"))
        tmp_input = Path(tempfile.mkdtemp(prefix="btp_input_"))
        
        # Download source file
        download_path = tmp_download / job.source_filename
        await download_file(job.source_url, download_path)
        
        # Extract file
        if job.source_filename.lower().endswith('.zip'):
            from zipfile import ZipFile
            with ZipFile(download_path, 'r') as zip_ref:
                zip_ref.extractall(tmp_input)
        else:
            # Copy PDF to input
            shutil.copy(download_path, tmp_input / job.source_filename)
        
        # Run engine (synchronous call in executor)
        loop = asyncio.get_event_loop()
        result, tmp_output = await loop.run_in_executor(
            None,
            run_engine,
            tmp_input,
            job.mode
        )
        
        # Update status
        job_manager.update_status(run_id, JobStatus.SUCCEEDED)
        
        # Send success callback
        payload = {
            "run_id": run_id,
            "status": "succeeded",
            "workspace_id": job.workspace_id,
            "project_id": job.project_id,
            **result
        }
        await send_callback(job.callback_url, job.callback_token, payload)
    
    except Exception as e:
        # Update status to failed
        error_msg = str(e)
        job_manager.update_status(run_id, JobStatus.FAILED, error_msg)
        
        # Send failure callback
        payload = {
            "run_id": run_id,
            "status": "failed",
            "error_message": error_msg,
            "workspace_id": job.workspace_id,
            "project_id": job.project_id,
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
            }
        }
        try:
            await send_callback(job.callback_url, job.callback_token, payload)
        except:
            pass  # Callback failure is not critical
    
    finally:
        # Cleanup
        if tmp_download and tmp_download.exists():
            shutil.rmtree(tmp_download, ignore_errors=True)
        if tmp_input and tmp_input.exists():
            shutil.rmtree(tmp_input, ignore_errors=True)
        if tmp_output and tmp_output.exists():
            shutil.rmtree(tmp_output, ignore_errors=True)
