"""CacheManager providing multi-tier caching (OCR, Gemini Vision, FAISS, PDF, Statistics) and automatic invalidation."""

import logging
import shutil
from pathlib import Path
from typing import Any

logger = logging.getLogger("CacheManager")


class CacheManager:
    """Multi-tier intelligent cache storing OCR, Gemini Vision, FAISS, PDF, and Statistics with auto-invalidation."""

    def __init__(self, cache_dir: Path | str | None = None) -> None:
        if cache_dir is None:
            cache_dir = Path("data/cache")
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        self._ocr_cache: dict[str, Any] = {}
        self._gemini_cache: dict[str, Any] = {}
        self._faiss_cache: dict[str, Any] = {}
        self._pdf_cache: dict[str, Any] = {}
        self._stat_cache: dict[str, Any] = {}
        self._in_memory_cache: dict[str, Any] = {}

    def invalidate_on_chart_upload(self, chart_identifier: str = "") -> None:
        """Automatically invalidates all caches whenever a new chart image is uploaded or updated."""
        logger.info(f"CacheManager: Automatic cache invalidation triggered for new chart '{chart_identifier}'")
        self._ocr_cache.clear()
        self._gemini_cache.clear()
        self._faiss_cache.clear()
        self._pdf_cache.clear()
        self._stat_cache.clear()
        self._in_memory_cache.clear()

        if self.cache_dir.exists():
            try:
                for item in self.cache_dir.iterdir():
                    if item.is_file():
                        item.unlink()
                    elif item.is_dir():
                        shutil.rmtree(item)
            except Exception as e:
                logger.warning(f"CacheManager disk eviction error: {e}")

    def clear_all(self) -> None:
        """Flushes all multi-tier caches."""
        self.invalidate_on_chart_upload("global_clear")

    def clear_extraction_cache(self, image_id: str | None = None) -> None:
        """Evicts cache entries for a specific image_id."""
        self.invalidate_on_chart_upload(image_id or "image_evict")

    # Tier-specific getter/setter helpers
    def get_ocr_cache(self, key: str) -> Any | None:
        return self._ocr_cache.get(key)

    def set_ocr_cache(self, key: str, value: Any) -> None:
        self._ocr_cache[key] = value

    def get_gemini_cache(self, key: str) -> Any | None:
        return self._gemini_cache.get(key)

    def set_gemini_cache(self, key: str, value: Any) -> None:
        self._gemini_cache[key] = value

    def get_faiss_cache(self, key: str) -> Any | None:
        return self._faiss_cache.get(key)

    def set_faiss_cache(self, key: str, value: Any) -> None:
        self._faiss_cache[key] = value

    def get_pdf_cache(self, key: str) -> Any | None:
        return self._pdf_cache.get(key)

    def set_pdf_cache(self, key: str, value: Any) -> None:
        self._pdf_cache[key] = value

    def get_stat_cache(self, key: str) -> Any | None:
        return self._stat_cache.get(key)

    def set_stat_cache(self, key: str, value: Any) -> None:
        self._stat_cache[key] = value

    def get(self, key: str) -> Any:
        return self._in_memory_cache.get(key)

    def set(self, key: str, value: Any) -> None:
        self._in_memory_cache[key] = value
