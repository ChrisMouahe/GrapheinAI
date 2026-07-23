"""Exponential backoff retry decorator for Gemini API calls."""

import functools
import logging
import time
from typing import Any, Callable, TypeVar

logger = logging.getLogger("GeminiRetry")

F = TypeVar("F", bound=Callable[..., Any])


def exponential_backoff_retry(
    max_retries: int = 5,
    initial_delay: float = 1.0,
    backoff_factor: float = 2.0,
    quota_manager: Any | None = None,
) -> Callable[[F], F]:
    """Decorator that retries API calls on 429, 503, or Timeout errors with exponential backoff (1s, 2s, 4s, 8s...)."""

    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            delay = initial_delay
            last_exception = None

            for attempt in range(1, max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as exc:
                    last_exception = exc
                    err_msg = str(exc).lower()

                    is_retryable = any(
                        keyword in err_msg
                        for keyword in ["429", "resource_exhausted", "quota", "503", "unavailable", "timeout", "rate limit", "deadline"]
                    )

                    if quota_manager:
                        quota_manager.record_error()

                    if not is_retryable or attempt == max_retries:
                        logger.error(f"Gemini call failed on attempt {attempt}/{max_retries}: {exc}")
                        raise exc

                    if quota_manager:
                        quota_manager.record_retry()

                    logger.warning(
                        f"Gemini transient error ({exc}). Retrying in {delay}s... (Attempt {attempt}/{max_retries})"
                    )
                    time.sleep(delay)
                    delay *= backoff_factor

            if last_exception:
                raise last_exception

        return wrapper  # type: ignore

    return decorator
