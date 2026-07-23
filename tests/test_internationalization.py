"""Comprehensive test suite for Internationalization (i18n) engine, LanguageManager, multi-lingual prompts, PDF reports, and pipeline auto-detection."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from src.agents.graph_interpreter import GraphInterpreter
from src.agents.pipeline_agent import PipelineAgent
from src.agents.reasoning_agent import ReasoningAgent
from src.i18n.language_manager import LanguageManager
from src.models.chart import (
    ChartExtraction,
    ChartImage,
    ClassificationResult,
    ExtractedDataPoint,
    PipelineResult,
    ValidationResult,
)
from src.utils.pdf_generator import PDFReportGenerator


def test_language_manager_loading() -> None:
    """Tests that LanguageManager loads French and English translation files correctly."""
    mgr = LanguageManager()
    assert "fr" in mgr._translations
    assert "en" in mgr._translations
    assert mgr.get_translation("nav.dashboard", lang="fr") == "Tableau de Bord"
    assert mgr.get_translation("nav.dashboard", lang="en") == "Dashboard"


def test_language_manager_automatic_detection() -> None:
    """Tests automatic language detection algorithm on French and English queries."""
    mgr = LanguageManager()

    # French queries
    assert mgr.detect_language("Combien fait la somme des ventes de Paris et Lyon ?") == "fr"
    assert mgr.detect_language("Quelle est la valeur moyenne observée ?") == "fr"
    assert mgr.detect_language("Décris les tendances clés et les anomalies du graphique.") == "fr"

    # English queries
    assert mgr.detect_language("What is the average sales revenue in 2023?") == "en"
    assert mgr.detect_language("Which category has the highest growth rate?") == "en"
    assert mgr.detect_language("Summarize the main trend and anomalies.") == "en"


def test_language_manager_number_formatting() -> None:
    """Tests locale-specific number formatting (12 345,67 for FR vs 12,345.67 for EN)."""
    assert LanguageManager.format_number(12345.67, lang="fr") == "12 345,67"
    assert LanguageManager.format_number(12345.67, lang="en") == "12,345.67"
    assert LanguageManager.format_number(100, lang="fr") == "100"
    assert LanguageManager.format_number(100, lang="en") == "100"


def test_graph_interpreter_multilingual_reports() -> None:
    """Tests that GraphInterpreter produces French and English narrative reports."""
    interpreter = GraphInterpreter()
    extraction = ChartExtraction(
        chart_type="bar",
        title="Ventes Annuelles",
        data_points=[
            ExtractedDataPoint(label="Paris", value=100.0, confidence=0.98),
            ExtractedDataPoint(label="Lyon", value=50.0, confidence=0.95),
        ],
        x_label="Villes",
        y_label="Ventes",
    )

    fr_report = interpreter.interpret_chart(extraction, target_language="fr")
    assert "RAPPORT AUTOMATIQUE D'INTERPRÉTATION SCIENTIFIQUE DU GRAPHIQUE" in fr_report
    assert "Architecture & Description du Contexte" in fr_report
    assert "Pic Maximum" in fr_report

    en_report = interpreter.interpret_chart(extraction, target_language="en")
    assert "AUTOMATIC SCIENTIFIC GRAPHIC INTERPRETATION REPORT" in en_report
    assert "Description & Context Architecture" in en_report
    assert "Peak Maximum" in en_report


def test_reasoning_agent_prompt_i18n() -> None:
    """Tests that ReasoningAgent constructs prompts matching the requested target_language."""
    agent = ReasoningAgent()
    extraction = ChartExtraction(
        chart_type="bar",
        data_points=[ExtractedDataPoint(label="A", value=10.0, confidence=0.9)],
    )

    fr_prompt = agent.build_prompt(
        question="Quelle est la valeur de A ?",
        retrieved_examples=[],
        extraction=extraction,
        target_language="fr",
    )
    assert "Target Language: FRENCH" in fr_prompt
    assert "Tu es un expert analyste de données visuelles" in fr_prompt

    en_prompt = agent.build_prompt(
        question="What is the value of A?",
        retrieved_examples=[],
        extraction=extraction,
        target_language="en",
    )
    assert "Target Language: ENGLISH" in en_prompt
    assert "You are a Senior AI Chart Analyst expert" in en_prompt


def test_pdf_generator_multilingual(tmp_path: Path) -> None:
    """Tests that PDFReportGenerator produces valid PDF bytes for both fr and en targets."""
    from PIL import Image
    pdf_gen = PDFReportGenerator()
    dummy_img = tmp_path / "test_chart.png"
    img = Image.new("RGB", (50, 50), color="blue")
    img.save(dummy_img)

    result = PipelineResult(
        complexity=ClassificationResult(question="Test Q", complexity="SIMPLE", is_complex=False, confidence=0.9),
        extracted_data=ChartExtraction(
            chart_type="bar",
            data_points=[ExtractedDataPoint(label="A", value=10.0, confidence=0.9)],
        ),
        reasoning="Test reasoning explanation",
        calculation_expression="10.0 * 2.0",
        final_answer="20.0",
        validation_result=ValidationResult(ocr_accuracy=0.9, extraction_accuracy=0.9, overall_confidence=0.9),
        initial_interpretation="### AUTOMATIC SCIENTIFIC REPORT\nTest interpretation",
        retrieved_examples=[],
        is_out_of_domain=False,
    )

    fr_pdf = pdf_gen.generate_pdf_bytes(result, dummy_img, execution_latency=0.5, target_language="fr")
    assert isinstance(fr_pdf, bytes)
    assert len(fr_pdf) > 500

    en_pdf = pdf_gen.generate_pdf_bytes(result, dummy_img, execution_latency=0.5, target_language="en")
    assert isinstance(en_pdf, bytes)
    assert len(en_pdf) > 500


@patch("src.agents.reasoning_agent.ReasoningAgent._call_vlm_vision")
def test_pipeline_agent_auto_language_detection(mock_vlm: MagicMock, tmp_path: Path) -> None:
    """Tests that PipelineAgent automatically detects query language and routes target_language."""
    mock_vlm.return_value = '{"reasoning": "English reasoning test", "calculation_expression": "100 + 50"}'

    pipeline = PipelineAgent()
    dummy_img = tmp_path / "sample.png"
    dummy_img.write_bytes(b"fake_image")

    # English query auto-detected
    res_en = pipeline.answer(image=dummy_img, question="What is the sum of Paris and Lyon?")
    assert res_en is not None

    # French query auto-detected
    mock_vlm.return_value = '{"reasoning": "Raisonnement en français", "calculation_expression": "100 + 50"}'
    res_fr = pipeline.answer(image=dummy_img, question="Combien fait la somme de Paris et Lyon ?")
    assert res_fr is not None
