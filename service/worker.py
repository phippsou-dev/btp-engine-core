"""Background worker for async jobs."""

import asyncio
import httpx
import tempfile
import shutil
import logging
from pathlib import Path
from typing import Dict, Any

from .jobs import job_manager, JobStatus, job_queue
from .runner import run_engine

logger = logging.getLogger(__name__)


async def download_file(url: str, destination: Path) -> None:
    """Download file from URL to destination."""
    logger.info(f"Downloading from {url[:100]}...")
    async with httpx.AsyncClient(timeout=300.0) as client:
        async with client.stream("GET", url) as response:
            response.raise_for_status()
            with open(destination, "wb") as f:
                async for chunk in response.aiter_bytes(chunk_size=8192):
                    f.write(chunk)
    logger.info(f"Download complete: {destination.name}")


async def send_callback(
    callback_url: str,
    callback_token: str,
    payload: Dict[str, Any]
) -> int:
    """
    Send callback to Supabase Edge Function.
    
    Returns:
        HTTP status code
    """
    logger.info(f"Posting callback to {callback_url}")
    logger.info(f"Payload run_id: {payload.get('run_id')}, status: {payload.get('status')}")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            callback_url,
            json=payload,
            headers={
                "Authorization": f"Bearer {callback_token}",
                "Content-Type": "application/json"
            }
        )
        response.raise_for_status()
        logger.info(f"Callback posted successfully: HTTP {response.status_code}")
        return response.status_code


async def process_job(run_id: str) -> None:
    """Process a job in background."""
    logger.info(f"Worker picked job: {run_id}")
    
    job = job_manager.get_job(run_id)
    if not job:
        logger.error(f"Job not found: {run_id}")
        return
    
    tmp_download = None
    tmp_input = None
    tmp_output = None
    
    try:
        # Update status to running
        job_manager.update_status(run_id, JobStatus.RUNNING)
        logger.info(f"Job status: RUNNING - {run_id}")
        
        # Create temp directories
        tmp_download = Path(tempfile.mkdtemp(prefix="btp_download_"))
        tmp_input = Path(tempfile.mkdtemp(prefix="btp_input_"))
        
        # Download source file
        job_manager.update_status(run_id, JobStatus.DOWNLOADING_SOURCE)
        logger.info(f"Job status: DOWNLOADING_SOURCE - {run_id}")
        
        download_path = tmp_download / job.source_filename
        await download_file(job.source_url, download_path)
        
        # Extract file
        if job.source_filename.lower().endswith('.zip'):
            from zipfile import ZipFile
            logger.info(f"Extracting ZIP: {job.source_filename}")
            with ZipFile(download_path, 'r') as zip_ref:
                zip_ref.extractall(tmp_input)
        else:
            # Copy PDF to input
            logger.info(f"Copying PDF: {job.source_filename}")
            shutil.copy(download_path, tmp_input / job.source_filename)
        
        # Run engine
        job_manager.update_status(run_id, JobStatus.RUNNING_ENGINE)
        logger.info(f"Job status: RUNNING_ENGINE - {run_id}")
        logger.info(f"Engine started for {run_id}")
        
        loop = asyncio.get_event_loop()
        result, tmp_output = await loop.run_in_executor(
            None,
            run_engine,
            tmp_input,
            job.mode
        )
        
        logger.info(f"Engine completed for {run_id}")
        
        # Send success callback
        job_manager.update_status(run_id, JobStatus.POSTING_CALLBACK)
        logger.info(f"Job status: POSTING_CALLBACK - {run_id}")
        
        payload = {
            "run_id": run_id,
            "status": "succeeded",
            "workspace_id": job.workspace_id,
            "project_id": job.project_id,
            **result
        }
        
        callback_status_code = await send_callback(job.callback_url, job.callback_token, payload)
        
        # Update status to succeeded
        job_manager.update_status(
            run_id, 
            JobStatus.SUCCEEDED,
            callback_status="success",
            callback_http_status=callback_status_code
        )
        logger.info(f"Job status: SUCCEEDED - {run_id}")
    
    except Exception as e:
        # Update status to failed
        error_msg = str(e)
        logger.error(f"Job FAILED: {run_id} - {error_msg}", exc_info=True)
        
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
            logger.info(f"Attempting to post failure callback for {run_id}")
            callback_status_code = await send_callback(job.callback_url, job.callback_token, payload)
            job_manager.update_status(
                run_id, 
                JobStatus.FAILED, 
                error_msg,
                callback_status="failed_posted",
                callback_http_status=callback_status_code
            )
        except Exception as callback_error:
            logger.error(f"Callback posting failed for {run_id}: {callback_error}")
            job_manager.update_status(
                run_id, 
                JobStatus.FAILED, 
                error_msg,
                callback_status="callback_failed",
                callback_http_status=None
            )
    
    finally:
        # Cleanup
        logger.info(f"Cleanup for {run_id}")
        if tmp_download and tmp_download.exists():
            shutil.rmtree(tmp_download, ignore_errors=True)
        if tmp_input and tmp_input.exists():
            shutil.rmtree(tmp_input, ignore_errors=True)
        if tmp_output and tmp_output.exists():
            shutil.rmtree(tmp_output, ignore_errors=True)


async def worker_loop():
    """Main worker loop that processes jobs from the queue."""
    logger.info("Worker loop started")
    
    while True:
        try:
            # Wait for a job
            run_id = await job_queue.get()
            logger.info(f"Worker dequeued job: {run_id}")
            
            # Process the job
            await process_job(run_id)
            
            # Mark job as done in queue
            job_queue.task_done()
            
        except asyncio.CancelledError:
            logger.info("Worker loop cancelled")
            break
        except Exception as e:
            logger.error(f"Worker loop error: {e}", exc_info=True)
            # Continue processing next job
