"""PDF Report Generator for ChartQA Multimodal Assistant supporting internationalization (ReportLab)."""

import io
from datetime import datetime
from pathlib import Path
from typing import Any

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import Image as RLImage
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from src.i18n.language_manager import LanguageManager
from src.models.chart import PipelineResult


from src.agents.recommendation_engine import PersonalizedRecommendations, RecommendationEngine
from src.models.user import UserProfile


class PDFReportGenerator:
    """Generates professional scientific PDF reports in French or English containing chart visual, extracted data table, interpretation narrative, validation metrics, and personalized AI recommendations."""

    def __init__(self) -> None:
        self.styles = getSampleStyleSheet()
        self.i18n = LanguageManager()
        self.recommendation_engine = RecommendationEngine()

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
        target_language: str = "fr",
        user_profile: UserProfile | None = None,
        recommendations: PersonalizedRecommendations | None = None,
    ) -> bytes:
        """Generates PDF report as bytes buffer in the specified target language."""
        lang = target_language.lower() if target_language in ["fr", "en"] else "fr"
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
        val_res = result.validation_result

        # 1. Document Header
        header_title = self.i18n.t("pdf.header_title", lang=lang)
        story.append(Paragraph(header_title, self.title_style))

        date_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        story.append(
            Paragraph(
                f"Generated on {date_str} | Engine: OpenCV CV + Gemini Flash VLM | Latency: {execution_latency:.2f}s | Language: {lang.upper()}",
                self.body_style,
            )
        )
        conf_lbl = "Confiance Globale" if lang == "fr" else "Overall Validation Confidence"
        story.append(
            Paragraph(
                f"<b>{conf_lbl}:</b> {val_res.overall_confidence:.1%} (OCR Acc: {val_res.ocr_accuracy:.1%} | Extraction Acc: {val_res.extraction_accuracy:.1%})",
                self.body_style,
            )
        )
        story.append(Spacer(1, 10))

        # 2. Image Section
        if img_p.exists():
            try:
                rl_img = RLImage(str(img_p), width=240, height=160)
                story.append(rl_img)
                story.append(Spacer(1, 10))
            except Exception:
                pass

        # 3. Final Answer Badge Card
        ans_lbl = self.i18n.t("pdf.sec_key_answer", lang=lang)
        expr_lbl = "Formule:" if lang == "fr" else "Expression:"
        answer_text = f"<b>{ans_lbl} {result.final_answer}</b><br/><font size=9>{expr_lbl} {result.calculation_expression}</font>"
        answer_bg = colors.HexColor("#D32F2F") if result.is_out_of_domain else colors.HexColor("#1565C0")

        answer_table = Table(
            [[Paragraph(answer_text, self.badge_style)]],
            colWidths=[540],
        )
        answer_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, -1), answer_bg),
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
        sec1_title = self.i18n.t("pdf.sec_executive_summary", lang=lang)
        q_lbl = "Question Cible:" if lang == "fr" else "Target Question:"
        reasoning_lbl = "Raisonnement Étape par Étape:" if lang == "fr" else "Step-by-step Logic:"
        story.append(Paragraph(sec1_title, self.h2_style))
        story.append(Paragraph(f"<b>{q_lbl}</b> {result.complexity.question}", self.body_style))
        story.append(Paragraph(f"<b>{reasoning_lbl}</b> {result.reasoning}", self.body_style))
        story.append(Spacer(1, 10))

        # 5. Extracted Tabular Data Table
        sec2_title = self.i18n.t("pdf.sec_quantitative", lang=lang)
        hitl_note = " <i>(HITL Modified)</i>" if result.extracted_data.metadata.get("is_hitl_modified") else ""
        story.append(Paragraph(f"{sec2_title}{hitl_note}", self.h2_style))

        lbl_hdr = self.i18n.t("pdf.table_label", lang=lang)
        val_hdr = self.i18n.t("pdf.table_value", lang=lang)
        conf_hdr = self.i18n.t("pdf.table_confidence", lang=lang)
        table_data = [[lbl_hdr, val_hdr, conf_hdr]]

        dps = result.extracted_data.data_points
        for dp in dps:
            lbl_text = dp.label if dp.label is not None else "[Unreadable Label]"
            val_fmt = LanguageManager.format_number(dp.value, lang=lang) if isinstance(dp.value, (int, float)) else str(dp.value)
            table_data.append([str(lbl_text), val_fmt, f"{dp.confidence:.2%}"])

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

        # 6. Automatic Scientific Graphic Interpretation
        sec3_title = self.i18n.t("pdf.sec_interpretation", lang=lang)
        story.append(Paragraph(sec3_title, self.h2_style))
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

        # 7. AI Strategic Recommendations & Action Plan Section
        recs = recommendations or self.recommendation_engine.generate_recommendations(
            extraction=result.extracted_data,
            user_profile=user_profile,
            target_language=lang,
        )

        rec_sec_title = "Recommandations Stratégiques & Plan d'Action AI" if lang == "fr" else "AI Strategic Recommendations & Action Plan"
        story.append(Paragraph(rec_sec_title, self.h2_style))
        story.append(Paragraph(f"<b>Executive Summary:</b> {recs.executive_summary}", self.body_style))
        story.append(Spacer(1, 4))

        rec_head = "Recommandations Prioritaires:" if lang == "fr" else "Priority Recommendations:"
        story.append(Paragraph(f"<b>{rec_head}</b>", self.body_style))
        for r in recs.priority_recommendations:
            story.append(Paragraph(f"• <b>[{r.priority.upper()}] {r.title}:</b> {r.description} <i>({r.rationale})</i>", self.body_style))
            story.append(Spacer(1, 2))

        story.append(Spacer(1, 4))
        action_head = "Plan d'Action & Étape Suivantes:" if lang == "fr" else "Action Plan & Next Steps:"
        story.append(Paragraph(f"<b>{action_head}</b>", self.body_style))
        for act in recs.action_plan:
            story.append(Paragraph(f"{act.step_number}. {act.action} (Impact: <i>{act.expected_impact}</i>, Responsable: <i>{act.owner}</i>)", self.body_style))
            story.append(Spacer(1, 2))

        story.append(Spacer(1, 6))
        story.append(Paragraph(f"<i>Garde-fou et Déclaration d'Authenticité: {recs.disclaimer}</i>", self.body_style))
        story.append(Spacer(1, 15))

        # 8. Validation Audit & RAG Context Section
        sec4_title = self.i18n.t("pdf.sec_methodology", lang=lang)
        story.append(Paragraph(sec4_title, self.h2_style))
        for note in val_res.validation_notes:
            story.append(Paragraph(f"• {note}", self.body_style))

        doc.build(story)
        pdf_bytes = buffer.getvalue()
        buffer.close()
        return pdf_bytes

    def generate_multi_chart_pdf_bytes(
        self,
        multi_result: Any,
        image_path: Path | str,
        execution_latency: float = 0.0,
        target_language: str = "fr",
        user_profile: UserProfile | None = None,
    ) -> bytes:
        """Generates a comprehensive multi-chart PDF report containing Table of Contents, sub-chart figures, comparative analytics, and global executive briefing."""
        lang = target_language.lower() if target_language in ["fr", "en"] else "fr"
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
        date_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 1. Title & Header
        title_txt = "RAPPORT DOCUMENTAIRE MULTI-GRAPHIQUES AI" if lang == "fr" else "AI MULTI-CHART DOCUMENTARY REPORT"
        story.append(Paragraph(title_txt, self.title_style))
        story.append(
            Paragraph(
                f"Generated on {date_str} | Sub-charts Detected: {multi_result.detection_result.total_charts_detected} | Latency: {execution_latency:.2f}s",
                self.body_style,
            )
        )
        story.append(Spacer(1, 10))

        # 2. Executive Global Briefing Section
        sec_title = "1. Synthèse Globale & Briefing Exécutif" if lang == "fr" else "1. Global Executive Briefing"
        story.append(Paragraph(sec_title, self.h2_style))
        story.append(Paragraph(f"<b>{multi_result.global_summary}</b>", self.body_style))
        story.append(Spacer(1, 10))

        # 3. Cross-Chart Comparative Analysis
        comp_title = "2. Analyse Comparative & Corrélations Inter-Graphiques" if lang == "fr" else "2. Cross-Chart Comparative Analysis"
        story.append(Paragraph(comp_title, self.h2_style))
        for comp in multi_result.cross_chart_comparisons:
            story.append(Paragraph(f"• <b>{comp.source_title} ↔ {comp.target_title}:</b> {comp.comparison_summary} <i>(Correlation: {comp.correlation_type.upper()})</i>", self.body_style))
            story.append(Spacer(1, 2))

        story.append(Spacer(1, 10))

        # 4. Individual Sub-Chart Breakdowns
        indiv_title = "3. Décomposition Individuelle des Graphiques" if lang == "fr" else "3. Individual Sub-Chart Breakdown"
        story.append(Paragraph(indiv_title, self.h2_style))

        for cid, res in multi_result.individual_results.items():
            c_title = res.extracted_data.title or f"Graphique {cid}"
            story.append(Paragraph(f"<b>[{cid.upper()}] {c_title}</b> (Type: {res.extracted_data.chart_type})", self.body_style))
            for dp in (res.extracted_data.data_points or []):
                lbl = dp.label or "[Illisible]"
                story.append(Paragraph(f"   - {lbl}: <code>{dp.value}</code>", self.body_style))
            story.append(Spacer(1, 4))

        story.append(Spacer(1, 10))

        # 5. Consolidated Global Recommendations
        rec_title = "4. Recommandations Stratégiques Consolidées" if lang == "fr" else "4. Consolidated Strategic Recommendations"
        story.append(Paragraph(rec_title, self.h2_style))
        for idx, rec in enumerate(multi_result.global_recommendations, 1):
            story.append(Paragraph(f"{idx}. {rec}", self.body_style))
            story.append(Spacer(1, 2))

        story.append(Spacer(1, 8))
        story.append(Paragraph("<i>Garde-fou et Déclaration d'Authenticité: La recommandation est basée sur les données observées.</i>", self.body_style))

        doc.build(story)
        pdf_bytes = buffer.getvalue()
        buffer.close()
        return pdf_bytes
