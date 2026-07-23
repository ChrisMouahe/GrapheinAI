"""PDFOptimizer for fast ReportLab PDF report compilation."""

from io import BytesIO
import logging
import time
from typing import Any

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

logger = logging.getLogger("PDFOptimizer")


class PDFOptimizer:
    """Optimizer providing pre-compiled ReportLab styles and fast memory buffer rendering."""

    def __init__(self) -> None:
        self.base_styles = getSampleStyleSheet()
        self._init_cached_styles()

    def _init_cached_styles(self) -> None:
        """Pre-compiles reusable ReportLab paragraph styles."""
        self.header_style = ParagraphStyle(
            "PDFOptHeader",
            parent=self.base_styles["Heading1"],
            fontName="Helvetica-Bold",
            fontSize=20,
            leading=24,
            textColor=colors.HexColor("#1E3A8A"),
        )
        self.body_style = ParagraphStyle(
            "PDFOptBody",
            parent=self.base_styles["Normal"],
            fontName="Helvetica",
            fontSize=10,
            leading=14,
            textColor=colors.HexColor("#1F2937"),
        )

    def generate_fast_pdf(self, title: str, content_lines: list[str]) -> tuple[bytes, float]:
        """Compiles PDF document directly in memory using pre-built styles.

        Args:
            title: Document title string.
            content_lines: Paragraph text lines.

        Returns:
            Tuple of (pdf_bytes, generation_latency_sec).
        """
        start_t = time.time()
        buf = BytesIO()
        doc = SimpleDocTemplate(buf, pagesize=letter, leftMargin=36, rightMargin=36, topMargin=36, bottomMargin=36)
        story = [
            Paragraph(title, self.header_style),
            Spacer(1, 12),
        ]
        for line in content_lines:
            story.append(Paragraph(line, self.body_style))
            story.append(Spacer(1, 6))

        doc.build(story)
        pdf_data = buf.getvalue()
        latency = time.time() - start_t
        logger.info(f"PDFOptimizer: Fast PDF compiled in {latency:.4f}s ({len(pdf_data)} bytes)")
        return pdf_data, latency
