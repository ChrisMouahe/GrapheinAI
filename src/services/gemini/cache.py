"""ChartCacheManager providing persistent SHA256 image-hashed caching for Gemini VLM extractions."""

import hashlib
import json
import logging
import time
from pathlib import Path
from typing import Any

from src.services.gemini.base import FullChartExtraction

logger = logging.getLogger("ChartCacheManager")


class ChartCacheManager:
    """Manages persistent SHA256 image-hashed cache for Gemini VLM extractions."""

    def __init__(
        self,
        cache_dir: Path | str = "data/cache",
        cache_filename: str = "gemini_chart_cache.json",
        ttl_seconds: int = 604800,  # 7 days default
    ) -> None:
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache_file = self.cache_dir / cache_filename
        self.ttl_seconds = ttl_seconds

        self._memory_cache: dict[str, tuple[dict[str, Any], float]] = {}
        self._load_disk_cache()

    @staticmethod
    def compute_image_hash(image_input: bytes | Path | str) -> str:
        """Computes SHA256 hex digest of image bytes or file content."""
        if isinstance(image_input, bytes):
            data = image_input
        else:
            p = Path(image_input)
            if p.exists() and p.is_file():
                data = p.read_bytes()
            else:
                data = str(image_input).encode("utf-8")
        return hashlib.sha256(data).hexdigest()

    def get(self, image_input: bytes | Path | str) -> FullChartExtraction | None:
        """Retrieves cached FullChartExtraction if available and not expired.

        Returns:
            FullChartExtraction model instance or None on cache miss.
        """
        img_hash = self.compute_image_hash(image_input)
        now = time.time()

        if img_hash in self._memory_cache:
            data_dict, timestamp = self._memory_cache[img_hash]
            if now - timestamp <= self.ttl_seconds:
                logger.info(f"ChartCacheManager: CACHE HIT for SHA256 {img_hash[:12]}")
                try:
                    return FullChartExtraction(**data_dict)
                except Exception as e:
                    logger.warning(f"Failed to parse cached ChartExtraction: {e}")
            else:
                logger.info(f"ChartCacheManager: CACHE EXPIRED for SHA256 {img_hash[:12]}")
                del self._memory_cache[img_hash]

        logger.info(f"ChartCacheManager: CACHE MISS for SHA256 {img_hash[:12]}")
        return None

    def put(self, image_input: bytes | Path | str, extraction: FullChartExtraction) -> None:
        """Stores a FullChartExtraction in memory and persistent disk cache."""
        img_hash = self.compute_image_hash(image_input)
        extraction.image_hash = img_hash

        data_dict = extraction.model_dump()
        now = time.time()
        self._memory_cache[img_hash] = (data_dict, now)
        self._save_disk_cache()
        logger.info(f"ChartCacheManager: Saved extraction for SHA256 {img_hash[:12]} to cache.")

    def clear(self) -> None:
        """Clears all cached extractions."""
        self._memory_cache.clear()
        if self.cache_file.exists():
            try:
                self.cache_file.unlink()
            except Exception as e:
                logger.warning(f"Could not delete cache file: {e}")

    def _load_disk_cache(self) -> None:
        """Loads cached extractions from disk file."""
        if not self.cache_file.exists():
            return
        try:
            raw = json.loads(self.cache_file.read_text(encoding="utf-8"))
            now = time.time()
            for key, val in raw.items():
                if isinstance(val, dict) and "data" in val and "timestamp" in val:
                    ts = val["timestamp"]
                    if now - ts <= self.ttl_seconds:
                        self._memory_cache[key] = (val["data"], ts)
            logger.info(f"ChartCacheManager: Loaded {len(self._memory_cache)} valid items from disk cache.")
        except Exception as e:
            logger.warning(f"Failed to read disk cache file {self.cache_file}: {e}")

    def _save_disk_cache(self) -> None:
        """Persists memory cache to disk file."""
        try:
            dump_data = {
                k: {"data": v[0], "timestamp": v[1]}
                for k, v in self._memory_cache.items()
            }
            self.cache_file.write_text(json.dumps(dump_data, indent=2, ensure_ascii=False), encoding="utf-8")
        except Exception as e:
            logger.warning(f"Failed to write disk cache file {self.cache_file}: {e}")
