"""OCROptimizer implementing image preprocessing to reduce OCR processing latency."""

import logging
from pathlib import Path
import time
from typing import Any
import cv2
import numpy as np

logger = logging.getLogger("OCROptimizer")


class OCROptimizer:
    """Preprocesses input image files for fast, high-accuracy OCR extraction."""

    def __init__(self) -> None:
        pass

    def optimize_image_for_ocr(self, image_path: Path | str, target_max_dim: int = 1200) -> tuple[np.ndarray, float]:
        """Preprocesses chart image with scaling and contrast adjustment.

        Args:
            image_path: Path to chart image file.
            target_max_dim: Maximum dimension pixel threshold for fast processing.

        Returns:
            Tuple of (preprocessed numpy BGR array, processing_latency_sec).
        """
        start_t = time.time()
        img = cv2.imread(str(image_path))
        if img is None:
            # Fallback black canvas if image unreadable
            img = np.zeros((600, 800, 3), dtype=np.uint8)

        h, w = img.shape[:2]
        if max(h, w) > target_max_dim:
            scale = target_max_dim / float(max(h, w))
            new_w, new_h = int(w * scale), int(h * scale)
            img = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_AREA)

        # Contrast enhancement
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(gray)
        res_bgr = cv2.cvtColor(enhanced, cv2.COLOR_GRAY2BGR)

        latency = time.time() - start_t
        logger.info(f"OCROptimizer: Image preprocessed in {latency:.4f}s")
        return res_bgr, latency
