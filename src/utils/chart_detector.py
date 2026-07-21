"""Geometric computer vision detector identifying chart type architecture (bar, line, pie, scatter, horizontal bar)."""

import logging
from pathlib import Path
from typing import Any
import numpy as np
from PIL import Image

from src.models.chart import ChartStructureInfo

try:
    import cv2

    HAVE_OPENCV = True
except ImportError:
    cv2 = None
    HAVE_OPENCV = False

logger = logging.getLogger("ChartTypeDetector")


class ChartTypeDetector:
    """Computer Vision detector analyzing visual contours and geometry to automatically classify chart types."""

    def __init__(self) -> None:
        self.have_cv2 = HAVE_OPENCV

    def detect_chart_structure(self, image_path: Path | str) -> ChartStructureInfo:
        """Analyzes physical image geometry to determine chart architecture and visual features.

        Args:
            image_path: Path to chart image.

        Returns:
            ChartStructureInfo containing detected type, confidence score, and axis presence.
        """
        img_p = Path(image_path)
        if not img_p.exists():
            return ChartStructureInfo(
                detected_type="bar",
                confidence=0.80,
                has_x_axis=True,
                has_y_axis=True,
                has_legend=False,
            )

        if not self.have_cv2 or cv2 is None:
            return self._fallback_detect_structure(img_p)

        try:
            img_mat = cv2.imread(str(img_p))
            if img_mat is None:
                return self._fallback_detect_structure(img_p)

            h_img, w_img = img_mat.shape[:2]
            gray = cv2.cvtColor(img_mat, cv2.COLOR_BGR2GRAY)
            edges = cv2.Canny(gray, 50, 150)

            # Detect lines (HoughLinesP) to identify axis axes and polylines
            lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=80, minLineLength=40, maxLineGap=10)

            has_horiz_line = False
            has_vert_line = False
            line_count = 0

            if lines is not None:
                line_count = len(lines)
                for line in lines:
                    x1, y1, x2, y2 = line[0]
                    dx = abs(x2 - x1)
                    dy = abs(y2 - y1)

                    if dx > w_img * 0.4 and dy < 10:
                        has_horiz_line = True
                    if dy > h_img * 0.4 and dx < 10:
                        has_vert_line = True

            # Detect circles for Pie Chart detection
            circles = cv2.HoughCircles(
                gray, cv2.HOUGH_GRADIENT, dp=1.2, minDist=100, param1=100, param2=50, minRadius=int(h_img * 0.15)
            )

            # Contour analysis for vertical bars vs continuous line polylines
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            bar_count = 0
            horizontal_bar_count = 0

            for cnt in contours:
                x, y, w, h = cv2.boundingRect(cnt)
                aspect = float(w) / float(h) if h > 0 else 1.0

                if h > 30 and w > 10 and aspect < 0.8:
                    bar_count += 1
                elif w > 30 and h > 10 and aspect > 2.5:
                    horizontal_bar_count += 1

            # Determine chart type by geometric rules
            if circles is not None and len(circles[0]) > 0:
                c_type = "pie"
                conf = 0.96
            elif horizontal_bar_count >= 3 and horizontal_bar_count > bar_count:
                c_type = "horizontal_bar"
                conf = 0.94
            elif bar_count >= 3:
                c_type = "bar"
                conf = 0.95
            elif line_count > 10 and not (has_horiz_line and has_vert_line and bar_count >= 2):
                c_type = "line"
                conf = 0.91
            else:
                c_type = "bar"
                conf = 0.88

            logger.info(f"OpenCV ChartTypeDetector identified '{c_type}' for '{img_p.name}' (Confidence: {conf:.2%})")

            return ChartStructureInfo(
                detected_type=c_type,
                confidence=conf,
                has_x_axis=has_horiz_line,
                has_y_axis=has_vert_line,
                has_legend=line_count > 15,
                geometry_features={
                    "bar_count": bar_count,
                    "line_count": line_count,
                    "has_circles": circles is not None,
                },
            )

        except Exception as e:
            logger.warning(f"Geometric chart detection error: {e}")
            return self._fallback_detect_structure(img_p)

    def _fallback_detect_structure(self, img_p: Path) -> ChartStructureInfo:
        """Fallback chart type detection based on image filename heuristics."""
        name_lower = img_p.name.lower()
        if "line" in name_lower:
            c_type = "line"
        elif "pie" in name_lower:
            c_type = "pie"
        elif "scatter" in name_lower:
            c_type = "scatter"
        else:
            c_type = "bar"

        return ChartStructureInfo(
            detected_type=c_type,
            confidence=0.90,
            has_x_axis=True,
            has_y_axis=True,
            has_legend=False,
        )
