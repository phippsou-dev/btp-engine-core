"""Async job management for BTP Engine."""

import asyncio
import uuid
from datetime import datetime
from typing import Dict, Optional
from enum import Enum


class JobStatus(str, Enum):
    """Job status values."""
    QUEUED = "queued"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


class Job:
    """Represents a BTP Engine job."""
    
    def __init__(
        self,
        run_id: str,
        source_url: str,
        source_filename: str,
        mode: str,
        callback_url: str,
        callback_token: str,
        workspace_id: Optional[str] = None,
        project_id: Optional[str] = None
    ):
        self.run_id = run_id
        self.source_url = source_url
        self.source_filename = source_filename
        self.mode = mode
        self.callback_url = callback_url
        self.callback_token = callback_token
        self.workspace_id = workspace_id
        self.project_id = project_id
        self.status = JobStatus.QUEUED
        self.error_message: Optional[str] = None
        self.created_at = datetime.utcnow()
        self.started_at: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None


class JobManager:
    """In-memory job manager."""
    
    def __init__(self):
        self.jobs: Dict[str, Job] = {}
    
    def create_job(
        self,
        run_id: str,
        source_url: str,
        source_filename: str,
        mode: str,
        callback_url: str,
        callback_token: str,
        workspace_id: Optional[str] = None,
        project_id: Optional[str] = None
    ) -> Job:
        """Create a new job."""
        job = Job(
            run_id=run_id,
            source_url=source_url,
            source_filename=source_filename,
            mode=mode,
            callback_url=callback_url,
            callback_token=callback_token,
            workspace_id=workspace_id,
            project_id=project_id
        )
        self.jobs[run_id] = job
        return job
    
    def get_job(self, run_id: str) -> Optional[Job]:
        """Get job by run_id."""
        return self.jobs.get(run_id)
    
    def update_status(self, run_id: str, status: JobStatus, error_message: Optional[str] = None):
        """Update job status."""
        job = self.jobs.get(run_id)
        if job:
            job.status = status
            if error_message:
                job.error_message = error_message
            if status == JobStatus.RUNNING and not job.started_at:
                job.started_at = datetime.utcnow()
            elif status in [JobStatus.SUCCEEDED, JobStatus.FAILED]:
                job.completed_at = datetime.utcnow()


# Global job manager instance
job_manager = JobManager()
