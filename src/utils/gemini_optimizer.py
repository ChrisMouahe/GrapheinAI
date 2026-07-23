"""GeminiOptimizer managing VLM response caching and prompt token optimization."""

import hashlib
import logging
import time
from typing import Any

from src.models.chart import ChartExtraction

logger = logging.getLogger("GeminiOptimizer")


class GeminiOptimizer:
    """Optimizer handling VLM response caching and prompt compression."""

    def __init__(self) -> None:
        self.response_cache: dict[str, tuple[ChartExtraction, float]] = {}

    def compute_cache_key(self, image_bytes: bytes, question: str) -> str:
        """Computes SHA-256 hash key for image content and question."""
        h = hashlib.sha256()
        h.update(image_bytes)
        h.update(question.encode("utf-8"))
        return h.hexdigest()

    def get_cached_response(self, cache_key: str) -> tuple[ChartExtraction, float] | None:
        """Retrieves cached ChartExtraction if present."""
        if cache_key in self.response_cache:
            extraction, cache_t = self.response_cache[cache_key]
            logger.info("GeminiOptimizer: VLM cache hit!")
            return extraction, cache_t
        return None

    def store_cached_response(self, cache_key: str, extraction: ChartExtraction) -> None:
        """Stores ChartExtraction response in VLM cache."""
        self.response_cache[cache_key] = (extraction, time.time())

    def compress_prompt(self, prompt: str) -> str:
        """Compresses redundant whitespace and removes comments from VLM prompts."""
        lines = [line.strip() for line in prompt.splitlines() if line.strip() and not line.strip().startswith("//")]
        return "\n".join(lines)
