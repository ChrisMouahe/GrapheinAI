"""ChartIntelligenceEngine for computer vision chart taxonomy classification, contour geometry analysis, and VLM reconciliation."""

import logging
from pathlib import Path
from typing import Any

import cv2
import numpy as np

from src.models.chart import OCRTextBox
from src.models.chart_intelligence import ChartMetadata, ChartTaxonomyType

logger = logging.getLogger("ChartIntelligenceEngine")


class ChartIntelligenceEngine:
    """Advanced Computer Vision Engine for fine-grained chart taxonomy detection and structural feature analysis."""

    def __init__(self) -> None:
        pass

    def analyze_image(self, image_path: Path | str, ocr_boxes: list[OCRTextBox] | None = None) -> ChartMetadata:
        """Analyzes chart image using contour geometry, Hough line grids, color clustering, and text region layouts."""
        img_p = Path(image_path)
        if not img_p.exists():
            logger.warning(f"Image filepath '{image_path}' not found. Returning default VERTICAL_BAR metadata.")
            return ChartMetadata(
                chart_type=ChartTaxonomyType.VERTICAL_BAR,
                confidence=0.85,
                orientation="vertical",
                decision_rationale="Default fallback due to missing image file.",
            )

        try:
            image = cv2.imread(str(img_p))
            if image is None:
                raise ValueError(f"OpenCV failed to decode image at '{image_path}'.")

            h, w, _ = image.shape
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

            # 1. Color Palette Extraction (Dominant HEX Colors)
            dominant_colors = self._extract_dominant_colors(image, num_colors=4)

            # 2. Hough Lines & Grid / Axis Analysis
            grid_detected, horiz_lines, vert_lines = self._detect_grid_and_axes(gray, h, w)

            # 3. Contour Geometry Classification
            cnts = cv2.findContours(cv2.Canny(gray, 50, 150), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            contours = cnts[0] if len(cnts) == 2 else cnts[1]

            # Analyze geometric shapes
            circular_count = 0
            rect_count = 0
            vertical_rects = 0
            horizontal_rects = 0
            line_segments = 0
            star_polygons = 0

            for c in contours:
                area = cv2.contourArea(c)
                if area < 50 or area > (h * w * 0.9):
                    continue

                perimeter = cv2.arcLength(c, True)
                if perimeter == 0:
                    continue

                circularity = 4 * np.pi * (area / (perimeter * perimeter))
                x, y, cw, ch = cv2.boundingRect(c)
                aspect_ratio = cw / float(ch) if ch > 0 else 1.0

                if circularity > 0.75 and min(cw, ch) > 20:
                    circular_count += 1
                elif aspect_ratio > 2.5:
                    rect_count += 1
                    horizontal_rects += 1
                elif aspect_ratio < 0.4:
                    rect_count += 1
                    vertical_rects += 1
                elif 0.4 <= aspect_ratio <= 2.5:
                    rect_count += 1
                    if aspect_ratio < 1.0:
                        vertical_rects += 1
                    else:
                        horizontal_rects += 1
                
                # Check for line segment characteristics
                approx = cv2.approxPolyDP(c, 0.02 * perimeter, True)
                if len(approx) > 5 and circularity < 0.4:
                    star_polygons += 1

            # 4. Legend & Series Count Estimation
            legend_detected, series_count = self._detect_legend_and_series(image, ocr_boxes)

            # 5. Taxonomy Decision Logic
            chart_type = ChartTaxonomyType.VERTICAL_BAR
            orientation = "vertical"
            confidence = 0.85
            rationale_parts = []

            # Check Scatter / Bubble (Multiple scattered circular markers)
            if circular_count >= 3 and rect_count < 3:
                if len(dominant_colors) >= 3:
                    chart_type = ChartTaxonomyType.BUBBLE_CHART
                    confidence = 0.89
                    rationale_parts.append(f"Multiple variable-sized circular nodes ({circular_count}) detected indicating Bubble chart.")
                else:
                    chart_type = ChartTaxonomyType.SCATTER_PLOT
                    confidence = 0.91
                    rationale_parts.append(f"Multiple coordinate circular markers ({circular_count}) detected indicating Scatter plot.")

            # Check Pie / Donut (Single pie or concentric donut rings)
            elif circular_count >= 1 and rect_count < 3:
                if circular_count >= 2:
                    chart_type = ChartTaxonomyType.DONUT_CHART
                    orientation = "radial"
                    rationale_parts.append("Concentric circular contours detected indicating Donut chart.")
                else:
                    chart_type = ChartTaxonomyType.PIE_CHART
                    orientation = "radial"
                    rationale_parts.append("Dominant circular contour detected indicating Pie chart.")
                confidence = 0.94

            # Check Radar Chart
            elif star_polygons >= 2 and circularity < 0.5:
                chart_type = ChartTaxonomyType.RADAR_CHART
                orientation = "radial"
                confidence = 0.88
                rationale_parts.append("Radial star polygon vertices and polar grid structure detected.")

            # Check Horizontal Bar
            elif horizontal_rects > vertical_rects and horizontal_rects >= 2:
                if series_count > 1:
                    chart_type = ChartTaxonomyType.GROUPED_BAR
                else:
                    chart_type = ChartTaxonomyType.HORIZONTAL_BAR
                orientation = "horizontal"
                confidence = 0.92
                rationale_parts.append(f"Multiple horizontal rectangular bars ({horizontal_rects}) detected.")

            # Check Line / Multi-Line / Area
            elif vert_lines > 4 and horiz_lines > 4 and rect_count < 3:
                if series_count > 1:
                    chart_type = ChartTaxonomyType.MULTI_LINE
                    rationale_parts.append(f"Grid intersection and {series_count} continuous lines detected.")
                else:
                    chart_type = ChartTaxonomyType.LINE
                    rationale_parts.append("Continuous line plot vertices and grid coordinate system detected.")
                orientation = "vertical"
                confidence = 0.89

            # Default Vertical / Stacked Bar
            else:
                if series_count > 1 and legend_detected:
                    chart_type = ChartTaxonomyType.STACKED_BAR
                    rationale_parts.append(f"Segmented vertical bars with {series_count} series legend detected.")
                else:
                    chart_type = ChartTaxonomyType.VERTICAL_BAR
                    rationale_parts.append(f"Vertical rectangular column contours ({vertical_rects}) detected.")
                orientation = "vertical"
                confidence = 0.90

            # 6. OCR Text Title & Axis Analysis
            x_title, y_title, detected_lang = self._analyze_ocr_labels(ocr_boxes)

            metadata = ChartMetadata(
                chart_type=chart_type,
                confidence=confidence,
                orientation=orientation,
                number_of_series=max(1, series_count),
                legend_detected=legend_detected,
                grid_detected=grid_detected,
                x_axis={"label": x_title, "gridlines": horiz_lines},
                y_axis={"label": y_title, "gridlines": vert_lines},
                colors=dominant_colors,
                language_detected=detected_lang,
                decision_rationale=" ".join(rationale_parts) or "Contour geometry and color features analyzed.",
                cv_confidence=confidence,
                final_decision_source="Computer Vision Engine",
            )
            return metadata

        except Exception as e:
            logger.warning(f"Error in ChartIntelligenceEngine.analyze_image: {e}")
            return ChartMetadata(
                chart_type=ChartTaxonomyType.VERTICAL_BAR,
                confidence=0.80,
                orientation="vertical",
                decision_rationale=f"Fallback due to CV processing error: {e}",
            )

    def reconcile_with_vlm(
        self,
        cv_metadata: ChartMetadata,
        vlm_proposed_type: str | None,
        vlm_confidence: float = 0.90,
    ) -> ChartMetadata:
        """Cross-validates Computer Vision metadata with Gemini VLM prediction and logs decision reconciliation."""
        if not vlm_proposed_type:
            return cv_metadata

        vlm_type_str = str(vlm_proposed_type).lower().strip().replace(" ", "_")

        # Map string to taxonomy enum if possible
        vlm_enum = None
        for tax in ChartTaxonomyType:
            if tax.value in vlm_type_str or vlm_type_str in tax.value:
                vlm_enum = tax
                break

        if not vlm_enum:
            vlm_enum = cv_metadata.chart_type

        # Choose highest confidence
        final_type = cv_metadata.chart_type
        final_source = "Computer Vision Engine"
        final_conf = cv_metadata.cv_confidence

        if vlm_confidence > cv_metadata.cv_confidence + 0.05:
            final_type = vlm_enum
            final_source = "Gemini Vision VLM"
            final_conf = vlm_confidence

        logger.info(
            f"Chart Intelligence: {cv_metadata.chart_type.value.upper()} ({cv_metadata.cv_confidence * 100:.1f}%) | "
            f"Gemini: {vlm_enum.value.upper()} ({vlm_confidence * 100:.1f}%) | "
            f"Décision finale: {final_type.value.upper()} [{final_source}]"
        )

        cv_metadata.chart_type = final_type
        cv_metadata.confidence = final_conf
        cv_metadata.vlm_confidence = vlm_confidence
        cv_metadata.final_decision_source = final_source
        return cv_metadata

    def _extract_dominant_colors(self, image: np.ndarray, num_colors: int = 4) -> list[str]:
        """Extracts dominant HEX colors from chart image using color quantization."""
        try:
            resized = cv2.resize(image, (100, 100))
            pixels = resized.reshape(-1, 3).astype(np.float32)
            criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
            _, labels, centers = cv2.kmeans(pixels, num_colors, None, criteria, 3, cv2.KMEANS_RANDOM_CENTERS)
            
            hex_colors = []
            for center in centers:
                b, g, r = int(center[0]), int(center[1]), int(center[2])
                # Skip pure background white or dark black
                if (r > 240 and g > 240 and b > 240) or (r < 25 and g < 25 and b < 25):
                    continue
                hex_colors.append(f"#{r:02x}{g:02x}{b:02x}")
            return hex_colors[:num_colors] or ["#3b82f6", "#8b5cf6"]
        except Exception:
            return ["#3b82f6", "#8b5cf6"]

    def _detect_grid_and_axes(self, gray: np.ndarray, h: int, w: int) -> tuple[bool, int, int]:
        """Detects presence of horizontal and vertical gridlines via Hough Transform."""
        try:
            edges = cv2.Canny(gray, 50, 150, apertureSize=3)
            lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=80, minLineLength=w // 4, maxLineGap=10)
            if lines is None:
                return False, 0, 0

            horiz = 0
            vert = 0
            for line in lines:
                x1, y1, x2, y2 = line[0]
                if abs(y2 - y1) < 5:
                    horiz += 1
                elif abs(x2 - x1) < 5:
                    vert += 1

            return (horiz > 2 or vert > 2), horiz, vert
        except Exception:
            return True, 3, 3

    def _detect_legend_and_series(self, image: np.ndarray, ocr_boxes: list[OCRTextBox] | None) -> tuple[bool, int]:
        """Estimates series count and legend box presence."""
        legend_found = False
        series_count = 1
        if ocr_boxes:
            labels = [b.text.lower() for b in ocr_boxes if b.text]
            if any(kw in labels for kw in ["legend", "légende", "series", "série", "catégorie", "category"]):
                legend_found = True
            if len(labels) >= 4:
                series_count = min(8, len(labels) // 2)

        if not legend_found:
            # Check right or top margin for color legend patches
            h, w, _ = image.shape
            margin_right = image[:, int(w * 0.75):]
            std_dev = np.std(margin_right, axis=(0, 1))
            if np.mean(std_dev) > 30.0:
                legend_found = True
                series_count = max(2, series_count)

        return legend_found, series_count

    def _analyze_ocr_labels(self, ocr_boxes: list[OCRTextBox] | None) -> tuple[str | None, str | None, str]:
        """Extracts X/Y titles and detects dominant language from OCR bounding boxes."""
        if not ocr_boxes:
            return None, None, "fr"

        text_concat = " ".join([b.text for b in ocr_boxes if b.text]).lower()
        fr_words = ["de", "la", "et", "du", "les", "ventes", "taux", "valeur", "année"]
        fr_score = sum(1 for w in fr_words if w in text_concat)
        lang = "fr" if fr_score >= 1 else "en"

        x_title = "X Axis"
        y_title = "Y Axis"
        for b in ocr_boxes:
            if b and b.text:
                txt_lower = b.text.lower()
                if "axis" in txt_lower or "axe" in txt_lower:
                    if "x" in txt_lower:
                        x_title = b.text
                    elif "y" in txt_lower:
                        y_title = b.text

        return x_title, y_title, lang
