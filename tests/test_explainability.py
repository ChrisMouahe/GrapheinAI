"""Unit and integration test suite for Explainability Engine (XAI) and transparency endpoints."""

from fastapi.testclient import TestClient
import pytest

from src.agents.explainability_engine import ExplainabilityEngine, XAIBreakdownReport
from src.app.api import app
from src.models.chart import ChartExtraction, ClassificationResult, ExtractedDataPoint, PipelineResult, ValidationResult


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def explainability_engine():
    return ExplainabilityEngine()


@pytest.fixture
def sample_pipeline_result():
    return PipelineResult(
        extracted_data=ChartExtraction(
            chart_type="bar",
            title="Performances Commerciales Q1-Q3",
            data_points=[
                ExtractedDataPoint(label="Q1 Sales", value=68.0, confidence=0.95),
                ExtractedDataPoint(label="Q2 Sales", value=88.0, confidence=0.98),
                ExtractedDataPoint(label="Q3 Sales", value=78.0, confidence=0.91),
            ],
            extraction_source="OpenCV + Gemini Flash",
        ),
        final_answer="234.00",
        calculation_expression="sum([68.0, 88.0, 78.0]) = 234.00",
        reasoning="Calcul du total des ventes Q1 à Q3",
        complexity=ClassificationResult(
            question="Quel est le total ?",
            complexity="SIMPLE",
            is_complex=False,
            confidence=0.99,
        ),
        retrieved_examples=[{"question": "Ventes totales", "answer": "234.00"}],
        validation_result=ValidationResult(ocr_accuracy=0.95, extraction_accuracy=0.98, overall_confidence=0.96, validation_notes=["AST calcul valide"]),
    )


def test_explainability_report_all_fields_populated(explainability_engine, sample_pipeline_result):
    """Verifies that ExplainabilityEngine generates a report with all 10 required transparency fields."""
    report = explainability_engine.generate_xai_report(
        sample_pipeline_result,
        target_language="fr",
        execution_time_sec=0.825,
    )

    assert isinstance(report, XAIBreakdownReport)
    # 1. Score de confiance global
    assert report.overall_confidence_pct == 96
    # 2. Niveau de confiance
    assert report.confidence_level == "Élevé"
    # 3. Données utilisées
    assert len(report.data_used) == 3
    assert report.data_used[0]["label"] == "Q1 Sales"
    assert report.data_used[0]["value"] == 68.0
    # 4. Graphique utilisé
    assert "Performances Commerciales Q1-Q3" in report.chart_used
    assert "BAR" in report.chart_used
    # 5. Colonnes / Axes utilisées
    assert "Q1 Sales" in report.columns_used["x_axis_categories"]
    assert "68.0" in report.columns_used["y_axis_metrics"]
    # 6. Calculs AST
    assert "234.00" in report.ast_calculations
    # 7. Contexte RAG utilisé
    assert len(report.rag_context_snippets) >= 1
    # 8. Temps d'exécution
    assert report.execution_time_sec == 0.825
    # 9. Modèle Gemini utilisé
    assert "Gemini Flash" in report.gemini_model
    # 10. Sources utilisées
    assert "Gemini Flash 1.5 Vision VLM" in report.sources_used
    assert "OpenCV OCR Extractor" in report.sources_used
    assert "SafeCalculator AST Engine" in report.sources_used


def test_confidence_level_mapping(explainability_engine, sample_pipeline_result):
    """Verifies mapping of confidence scores to Élevé, Moyen, and Faible."""
    # High confidence (>=90%)
    sample_pipeline_result.validation_result.overall_confidence = 0.95
    report_high = explainability_engine.generate_xai_report(sample_pipeline_result, target_language="fr")
    assert report_high.confidence_level == "Élevé"

    # Medium confidence (70-89%)
    sample_pipeline_result.validation_result.overall_confidence = 0.78
    report_med = explainability_engine.generate_xai_report(sample_pipeline_result, target_language="fr")
    assert report_med.confidence_level == "Moyen"

    # Low confidence (<70%)
    sample_pipeline_result.validation_result.overall_confidence = 0.55
    report_low = explainability_engine.generate_xai_report(sample_pipeline_result, target_language="fr")
    assert report_low.confidence_level == "Faible"


def test_no_raw_prompt_chain_leakage(explainability_engine, sample_pipeline_result):
    """Verifies that raw internal system prompt templates and chain-of-thought scratchpads are stripped."""
    report = explainability_engine.generate_xai_report(sample_pipeline_result, target_language="fr")
    report_dump_str = str(report.model_dump()).lower()

    # Ensure no internal prompt keys exist
    assert "system_prompt" not in report_dump_str
    assert "scratchpad" not in report_dump_str
    assert "thought_process" not in report_dump_str


def test_api_explainability_endpoints(client):
    """Verifies REST API integration for /api/analyze and GET /api/explain/{session_id}."""
    login_res = client.post("/api/auth/login", json={"email": "demo@graphein.ai", "password": "password123"})
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Analyze chart
    analyze_res = client.post(
        "/api/analyze",
        data={"question": "Quel est le total de la distribution ?"},
        headers=headers,
    )
    assert analyze_res.status_code == 200
    res_data = analyze_res.json()
    assert "xai_breakdown" in res_data
    xai = res_data["xai_breakdown"]
    assert "overall_confidence_pct" in xai
    assert "confidence_level" in xai
    assert "gemini_model" in xai
    assert "sources_used" in xai

    # 2. Dedicated GET /api/explain/{session_id}
    explain_res = client.get("/api/explain/sample_chart", headers=headers)
    assert explain_res.status_code == 200
    explain_data = explain_res.json()
    assert "overall_confidence_pct" in explain_data
    assert "confidence_level" in explain_data
