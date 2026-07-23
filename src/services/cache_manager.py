"""CacheManager for flushing OCR, Gemini Vision, FAISS, Statistics, Interpretation, and Extractions."""

import logging
import shutil
from pathlib import Path
from typing import Any

logger = logging.getLogger("CacheManager")


class CacheManager:
    """Manages cache eviction and state reset for isolated chart analysis sessions."""

    def __init__(self, cache_dir: Path | str | None = None) -> None:
        if cache_dir is None:
            cache_dir = Path("data/cache")
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        self._in_memory_cache: dict[str, Any] = {}

    def clear_all(self) -> None:
        """Completely flushes all in-memory and disk caches."""
        logger.info("CacheManager: Flushing all system caches (OCR, Gemini, FAISS, Stats, Interpretation)...")
        self._in_memory_cache.clear()

        if self.cache_dir.exists():
            try:
                for item in self.cache_dir.iterdir():
                    if item.is_file():
                        item.unlink()
                    elif item.is_dir():
                        shutil.rmtree(item)
            except Exception as e:
                logger.warning(f"CacheManager warning during disk cache flush: {e}")

    def clear_extraction_cache(self, image_id: str | None = None) -> None:
        """Clears specific vision and extraction cache for an image."""
        logger.info(f"CacheManager: Evicting extraction cache for image: '{image_id}'")
        if image_id and image_id in self._in_memory_cache:
            del self._in_memory_cache[image_id]

        # Flush disk cache files associated with image_id
        if image_id and self.cache_dir.exists():
            for c_file in self.cache_dir.glob(f"*{image_id}*"):
                try:
                    if c_file.is_file():
                        c_file.unlink()
                except Exception:
                    pass

    def get(self, key: str) -> Any:
        """Retrieves cached item if present."""
        return self._in_memory_cache.get(key)

    def set(self, key: str, value: Any) -> None:
        """Stores item in cache."""
        self._in_memory_cache[key] = value
