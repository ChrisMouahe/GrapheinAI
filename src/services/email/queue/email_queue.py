"""Asynchronous Email Dispatch Queue with retry policies and observability metrics."""

import time
import uuid
import logging
from concurrent.futures import ThreadPoolExecutor
from typing import Any
from pydantic import BaseModel, Field

from src.services.email.providers.base import BaseEmailProvider, EmailDispatchResult, EmailMessage

logger = logging.getLogger(__name__)


class QueuedEmailJob(BaseModel):
    """Data model representing a queued email job item."""

    job_id: str = Field(..., description="Unique Queue Job ID")
    message: EmailMessage = Field(..., description="Email message payload")
    status: str = Field(default="pending", description="Job status ('pending', 'sending', 'sent', 'failed', 'retry')")
    attempts: int = Field(default=0, description="Current attempt count")
    max_retries: int = Field(default=3, description="Maximum retry limit")
    error: str | None = Field(default=None, description="Last error message")
    created_at: float = Field(default_factory=time.time, description="Creation timestamp")
    sent_at: float | None = Field(default=None, description="Successful dispatch timestamp")
    latency_ms: float = Field(default=0.0, description="Dispatch latency in milliseconds")


class EmailQueue:
    """Async background worker queue executing email dispatches without blocking HTTP responses."""

    def __init__(self, provider: BaseEmailProvider | None = None, max_workers: int = 4) -> None:
        self.provider = provider
        self.executor = ThreadPoolExecutor(max_workers=max_workers, thread_name_prefix="EmailQueueWorker")
        self._jobs: dict[str, QueuedEmailJob] = {}

    def set_provider(self, provider: BaseEmailProvider) -> None:
        """Updates the active email provider."""
        self.provider = provider

    def enqueue(self, message: EmailMessage, max_retries: int = 3) -> QueuedEmailJob:
        """Adds an email message to the async dispatch queue and launches worker execution."""
        job_id = f"job_{uuid.uuid4().hex[:12]}"
        job = QueuedEmailJob(
            job_id=job_id,
            message=message,
            status="pending",
            max_retries=max_retries,
        )
        self._jobs[job_id] = job

        # Submit task to background thread pool
        self.executor.submit(self._process_job, job_id)
        return job

    def _process_job(self, job_id: str) -> None:
        """Worker method processing a queued email dispatch job."""
        job = self._jobs.get(job_id)
        if not job or not self.provider:
            if job:
                job.status = "failed"
                job.error = "Aucun fournisseur d'emails configuré."
            return

        job.status = "sending"
        job.attempts += 1

        start_time = time.time()
        result: EmailDispatchResult = self.provider.send_email(job.message)
        latency = (time.time() - start_time) * 1000

        if result.success:
            job.status = "sent"
            job.sent_at = time.time()
            job.latency_ms = round(latency, 2)
            logger.info(f"[EmailQueue] Job {job_id} delivered successfully via {result.provider_name} in {latency:.1f}ms")
        else:
            job.error = result.error
            if job.attempts < job.max_retries:
                job.status = "retry"
                logger.warning(f"[EmailQueue] Job {job_id} failed (Attempt {job.attempts}/{job.max_retries}). Retrying...")
                time.sleep(1.0)
                self.executor.submit(self._process_job, job_id)
            else:
                job.status = "failed"
                logger.error(f"[EmailQueue] Job {job_id} failed permanently after {job.attempts} attempts: {result.error}")

    def retry_job(self, job_id: str) -> bool:
        """Manually triggers a retry for a failed email job."""
        job = self._jobs.get(job_id)
        if job and job.status == "failed":
            job.status = "pending"
            job.attempts = 0
            job.error = None
            self.executor.submit(self._process_job, job_id)
            return True
        return False

    def get_job(self, job_id: str) -> QueuedEmailJob | None:
        """Retrieves job status by job ID."""
        return self._jobs.get(job_id)

    def get_all_jobs(self) -> list[QueuedEmailJob]:
        """Returns all recorded queued jobs."""
        return list(self._jobs.values())

    def get_metrics(self) -> dict[str, Any]:
        """Calculates queue performance metrics for Admin Dashboard monitoring."""
        jobs = list(self._jobs.values())
        total = len(jobs)
        pending = sum(1 for j in jobs if j.status in ("pending", "sending", "retry"))
        sent = sum(1 for j in jobs if j.status == "sent")
        failed = sum(1 for j in jobs if j.status == "failed")
        latencies = [j.latency_ms for j in jobs if j.status == "sent" and j.latency_ms > 0]
        avg_latency = round(sum(latencies) / len(latencies), 2) if latencies else 0.0

        return {
            "total_emails": total,
            "pending_count": pending,
            "sent_count": sent,
            "failed_count": failed,
            "success_rate_percent": round((sent / total * 100), 1) if total > 0 else 100.0,
            "avg_latency_ms": avg_latency,
            "provider_name": self.provider.provider_name if self.provider else "none",
        }
