"""TaskQueueManager handling background asynchronous job execution, progress tracking, and queue state management."""

import asyncio
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
import logging
from typing import Any, Callable
import uuid

from pydantic import BaseModel, Field

logger = logging.getLogger("TaskQueueManager")


class AsyncTaskItem(BaseModel):
    """Structured representation of an asynchronous task in the queue."""

    task_id: str = Field(..., description="Unique task identifier")
    task_type: str = Field(..., description="Task type ('OCR', 'EXTRACTION', 'GEMINI', 'PDF', 'RECOMMENDATIONS')")
    status: str = Field(default="PENDING", description="'PENDING', 'IN_PROGRESS', 'COMPLETED', 'FAILED'")
    status_label: str = Field(default="En attente", description="Human-readable French status string")
    progress_percent: int = Field(default=0, ge=0, le=100, description="Task completion percentage (0-100%)")
    created_at: str = Field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    completed_at: str | None = Field(default=None)
    result_data: Any | None = Field(default=None)
    error_message: str | None = Field(default=None)


class TaskQueueManager:
    """Manages an in-memory asynchronous task queue with thread pool execution and progress tracking."""

    def __init__(self, max_workers: int = 4) -> None:
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.tasks: dict[str, AsyncTaskItem] = {}

    def submit_task(self, task_type: str, func: Callable[..., Any], *args: Any, **kwargs: Any) -> AsyncTaskItem:
        """Submits a heavy synchronous function to run asynchronously in the background worker pool.

        Args:
            task_type: Category of the task ('OCR', 'GEMINI', 'PDF', etc.).
            func: Target callable function.
            *args: Positional arguments for func.
            **kwargs: Keyword arguments for func.

        Returns:
            AsyncTaskItem initial model payload.
        """
        task_id = f"task_{uuid.uuid4().hex[:8]}"
        task_item = AsyncTaskItem(
            task_id=task_id,
            task_type=task_type,
            status="PENDING",
            status_label="En attente",
            progress_percent=0,
        )
        self.tasks[task_id] = task_item

        def _worker_wrapper():
            try:
                task_item.status = "IN_PROGRESS"
                task_item.status_label = "En cours"
                task_item.progress_percent = 25

                # Execute target workload
                result = func(*args, **kwargs)

                task_item.progress_percent = 100
                task_item.status = "COMPLETED"
                task_item.status_label = "Terminé"
                task_item.completed_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                task_item.result_data = result
                logger.info(f"TaskQueueManager: Task '{task_id}' ({task_type}) completed successfully.")

            except Exception as ex:
                task_item.status = "FAILED"
                task_item.status_label = "Erreur"
                task_item.progress_percent = 100
                task_item.error_message = str(ex)
                task_item.completed_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                logger.error(f"TaskQueueManager: Task '{task_id}' ({task_type}) failed: {ex}")

        self.executor.submit(_worker_wrapper)
        return task_item

    def get_task_status(self, task_id: str) -> AsyncTaskItem | None:
        """Returns current status of task_id."""
        return self.tasks.get(task_id)

    def list_recent_tasks(self, limit: int = 20) -> list[AsyncTaskItem]:
        """Lists recent tasks ordered by creation time descending."""
        sorted_tasks = sorted(self.tasks.values(), key=lambda t: t.created_at, reverse=True)
        return sorted_tasks[:limit]
