import json
import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

# Configure production rotating log file handler
LOG_DIR = Path(__file__).resolve().parent.parent.parent / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / "graphein_app.log"

root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)
if not any(isinstance(h, RotatingFileHandler) for h in root_logger.handlers):
    rf_handler = RotatingFileHandler(LOG_FILE, maxBytes=5 * 1024 * 1024, backupCount=5, encoding="utf-8")
    rf_handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s'))
    root_logger.addHandler(rf_handler)


class LogRecordEntry(BaseModel):
    """Structured log record item."""

    timestamp: str = Field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    level: str = Field(..., description="'INFO', 'WARNING', 'ERROR', 'DEBUG'")
    component: str = Field(..., description="Target component or module name")
    message: str = Field(..., description="Log message string")
    context: dict[str, Any] = Field(default_factory=dict, description="Additional context parameters")


class StructuredLogger:
    """Structured logger storing JSON log records in a thread-safe in-memory circular buffer and rotating file."""

    def __init__(self, max_records: int = 500) -> None:
        self.max_records = max_records
        self.buffer: list[LogRecordEntry] = []

    def log(self, level: str, component: str, message: str, **context: Any) -> LogRecordEntry:
        """Emits a structured log record.

        Args:
            level: Severity level ('INFO', 'WARNING', 'ERROR', 'DEBUG').
            component: Module or service name.
            message: Human-readable log string.
            **context: Key-value context pairs.

        Returns:
            LogRecordEntry model.
        """
        entry = LogRecordEntry(
            level=level.upper(),
            component=component,
            message=message,
            context=context,
        )
        self.buffer.append(entry)
        if len(self.buffer) > self.max_records:
            self.buffer.pop(0)

        # Standard logging emission
        log_str = json.dumps(entry.model_dump())
        if level.upper() == "ERROR":
            logging.error(log_str)
        elif level.upper() == "WARNING":
            logging.warning(log_str)
        else:
            logging.info(log_str)

        return entry

    def info(self, component: str, message: str, **context: Any) -> LogRecordEntry:
        return self.log("INFO", component, message, **context)

    def warning(self, component: str, message: str, **context: Any) -> LogRecordEntry:
        return self.log("WARNING", component, message, **context)

    def error(self, component: str, message: str, **context: Any) -> LogRecordEntry:
        return self.log("ERROR", component, message, **context)

    def get_admin_logs(self, limit: int = 100, level_filter: str | None = None) -> list[dict[str, Any]]:
        """Returns recent structured logs for admin observability dashboard."""
        logs = list(reversed(self.buffer))
        if level_filter:
            logs = [l for l in logs if l.level == level_filter.upper()]
        return [l.model_dump() for l in logs[:limit]]
