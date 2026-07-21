"""PDF Report Generator for ChartQA Multimodal Assistant using ReportLab."""

import io
from datetime import datetime
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import Image as RLImage
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from src.models.chart import PipelineResult


class PDFReportGenerator:
    """Generates professional scientific PDF reports containing chart visual, extracted data table, interpretation narrative, and reasoning answer."""

    def __init__(self) -> None:
        self.styles = getSampleStyleSheet()

        # Custom paragraph styles
        self.title_style = ParagraphStyle(
            "DocTitle",
            parent=self.styles["Title"],
            fontSize=22,
            leading=26,
            textColor=colors.HexColor("#1E88E5"),
            alignment=0,
            spaceAfter=12,
        )

        self.h2_style = ParagraphStyle(
            "SectionH2",
            parent=self.styles["Heading2"],
            fontSize=14,
            leading=18,
            textColor=colors.HexColor("#1565C0"),
            spaceBefore=12,
            spaceAfter=6,
        )

        self.body_style = ParagraphStyle(
            "BodyTextCustom",
            parent=self.styles["Normal"],
            fontSize=10,
            leading=14,
            textColor=colors.HexColor("#333333"),
            spaceAfter=6,
        )

        self.badge_style = ParagraphStyle(
            "AnswerBadge",
            parent=self.styles["Normal"],
            fontSize=14,
            leading=18,
            textColor=colors.white,
            alignment=1,
        )

    def generate_pdf_bytes(
        self,
        result: PipelineResult,
        image_path: Path | str,
        execution_latency: float = 0.0,
    ) -> bytes:
        """Generates PDF report as bytes buffer.

        Args:
            result: PipelineResult model.
            image_path: Path to chart image file.
            execution_latency: Pipeline latency in seconds.

        Returns:
            bytes containing the PDF document.
        """
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36,
        )

        story = []
        img_p = Path(image_path)

        # 1. Document Header
        story.append(Paragraph("ChartQA Multimodal Scientific Reasoning Report", self.title_style))
        story.append(
            Paragraph(
                f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | GrapheinAI Multimodal Engine",
                self.body_style,
            )
        )
        story.append(Spacer(1, 10))

        # 2. Image & Quick Summary Section
        if img_p.exists():
            try:
                rl_img = RLImage(str(img_p), width=240, height=160)
                story.append(rl_img)
                story.append(Spacer(1, 10))
            except Exception:
                pass

        # 3. Final Answer Badge Card
        answer_text = f"<b>Final Calculated Answer: {result.final_answer}</b><br/><font size=9>Expression: {result.calculation_expression}</font>"
        answer_table = Table(
            [[Paragraph(answer_text, self.badge_style)]],
            colWidths=[540],
        )
        answer_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#1565C0")),
                    ("TOPPADDING", (0, 0), (-1, -1), 10),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ]
            )
        )
        story.append(answer_table)
        story.append(Spacer(1, 15))

        # 4. User Question & Reasoning Section
        story.append(Paragraph("1. User Target Question & Analytical Reasoning", self.h2_style))
        story.append(Paragraph(f"<b>Target Question:</b> {result.complexity.question}", self.body_style))
        story.append(Paragraph(f"<b>Complexity Classification:</b> {result.complexity.complexity} (Confidence: {result.complexity.confidence:.1%})", self.body_style))
        story.append(Paragraph(f"<b>Step-by-step Logic:</b> {result.reasoning}", self.body_style))
        story.append(Paragraph(f"<b>AST SafeCalculator Expression:</b> <code>{result.calculation_expression}</code>", self.body_style))
        story.append(Spacer(1, 10))

        # 5. Extracted Tabular Data Table
        story.append(Paragraph("2. Dynamically Extracted Chart Data Table", self.h2_style))
        dps = result.extracted_data.data_points
        table_data = [["Label / Category", "Value", "Confidence Score"]]

        for dp in dps:
            table_data.append([str(dp.label), str(dp.value), f"{dp.confidence:.2%}"])

        data_table = Table(table_data, colWidths=[240, 150, 150])
        data_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#F0F4F8")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#1565C0")),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("BOTTOMPADDING", (0, 0), (-1, 0), 6),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#DDDDDD")),
                    ("ALIGN", (1, 0), (-1, -1), "CENTER"),
                ]
            )
        )
        story.append(data_table)
        story.append(Spacer(1, 15))

        # 6. Automatic Scientific Graphic Interpretation (~1 page narrative)
        story.append(Paragraph("3. Automatic Scientific Graphic Interpretation", self.h2_style))
        interp_lines = result.initial_interpretation.split("\n")
        for line in interp_lines:
            line_str = line.strip()
            if not line_str:
                continue
            if line_str.startswith("#"):
                clean_h = line_str.lstrip("#").strip()
                story.append(Paragraph(f"<b>{clean_h}</b>", self.body_style))
            else:
                story.append(Paragraph(line_str, self.body_style))
            story.append(Spacer(1, 2))

        story.append(Spacer(1, 15))

        # 7. RAG Few-Shot Context Section
        if result.retrieved_examples:
            story.append(Paragraph("4. Retrieved RAG Few-Shot Context", self.h2_style))
            for idx, ex in enumerate(result.retrieved_examples, 1):
                story.append(
                    Paragraph(
                        f"• <b>Example {idx}:</b> <i>{ex.get('question')}</i> ➔ Formula: <code>{ex.get('resolution_formula')}</code> (Answer: {ex.get('answer')})",
                        self.body_style,
                    )
                )

        doc.build(story)
        pdf_bytes = buffer.getvalue()
        buffer.close()
        return pdf_bytes
