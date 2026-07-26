"""EnterpriseQueueManager providing async task queuing, worker thread pool execution, and task status tracking."""

from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from enum import Enum
import logging
from typing import Any, Callable
import uuid

from pydantic import BaseModel, Field

logger = logging.getLogger("EnterpriseQueueManager")


class TaskState(str, Enum):
    """Execution state of a queued background task."""

    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class QueueTaskItem(BaseModel):
    """Representation of an asynchronous queued task."""

    task_id: str = Field(..., description="Unique task identifier")
    task_type: str = Field(..., description="Task category: OCR, GEMINI, FAISS, PDF, RECS")
    state: TaskState = Field(default=TaskState.PENDING, description="Current execution state")
    progress_pct: int = Field(default=0, ge=0, le=100, description="Execution progress percentage")
    created_at: str = Field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    completed_at: str | None = Field(default=None)
    result_data: Any | None = Field(default=None)
    error_message: str | None = Field(default=None)


class EnterpriseQueueManager:
    """Manager handling thread pool worker dispatch, async task queues, and progress reporting."""

    def __init__(self, max_workers: int = 4) -> None:
        self.executor = ThreadPoolExecutor(max_workers=max_workers, thread_name_prefix="GrapheinWorker")
        self.tasks: dict[str, QueueTaskItem] = {}

    def submit_task(self, task_type: str, func: Callable, *args: Any, **kwargs: Any) -> str:
        """Submits a synchronous function for background execution in the thread pool.

        Args:
            task_type: Task category ("OCR", "GEMINI", "FAISS", "PDF", "RECS").
            func: Target callable.
            *args: Arguments for callable.
            **kwargs: Keyword arguments for callable.

        Returns:
            Assigned task_id string.
        """
        task_id = f"task_{task_type.lower()}_{uuid.uuid4().hex[:8]}"
        task_item = QueueTaskItem(task_id=task_id, task_type=task_type, state=TaskState.PENDING)
        self.tasks[task_id] = task_item

        def _runner():
            task_item.state = TaskState.IN_PROGRESS
            task_item.progress_pct = 50
            try:
                res = func(*args, **kwargs)
                task_item.state = TaskState.COMPLETED
                task_item.progress_pct = 100
                task_item.result_data = res
                task_item.completed_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                logger.info(f"QueueManager: Task '{task_id}' ({task_type}) completed successfully.")
            except Exception as e:
                task_item.state = TaskState.FAILED
                task_item.error_message = str(e)
                task_item.completed_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                logger.error(f"QueueManager: Task '{task_id}' failed: {e}")

        self.executor.submit(_runner)
        return task_id

    def get_task_status(self, task_id: str) -> QueueTaskItem | None:
        """Retrieves status of a queued task."""
        return self.tasks.get(task_id)

    def list_active_tasks(self) -> list[QueueTaskItem]:
        """Lists all recorded tasks."""
        return list(self.tasks.values())
