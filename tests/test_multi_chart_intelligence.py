"""Unit and integration test suite for Multi-Chart Intelligence Engine & Document AI Fusion."""

from pathlib import Path
from fastapi.testclient import TestClient
import pytest

from src.agents.multi_chart_fusion import MultiChartFusionEngine
from src.agents.multi_chart_pipeline import MultiChartPipelineAgent
from src.app.api import app
from src.models.chart import ChartExtraction, ClassificationResult, ExtractedDataPoint, PipelineResult
from src.models.multi_chart import ChartRegion, DetectedChart, MultiChartDetectionResult
from src.models.user import UserProfile
from src.utils.multi_chart_detector import MultiChartDetector
from src.utils.pdf_generator import PDFReportGenerator


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def sample_user_profile():
    return UserProfile(
        id="usr_multichart_1",
        name="Elena Executive",
        email="elena@enterprise.ai",
        fonction="Directeur de la Stratégie",
        secteur_activite="Finance",
        niveau_expertise="Expert",
    )


@pytest.fixture
def mock_detection_result():
    return MultiChartDetectionResult(
        total_charts_detected=3,
        detected_charts=[
            DetectedChart(
                chart_id="chart_1",
                chart_index=1,
                title="Évolution des Ventes Trimestrielles",
                chart_type="bar",
                confidence=0.96,
                bbox=ChartRegion(x=10, y=10, w=400, h=300),
                cropped_image_path="tests/fixtures/chart_1.png",
                data_point_count=4,
            ),
            DetectedChart(
                chart_id="chart_2",
                chart_index=2,
                title="Marge Opérationnelle (%)",
                chart_type="line",
                confidence=0.94,
                bbox=ChartRegion(x=430, y=10, w=400, h=300),
                cropped_image_path="tests/fixtures/chart_2.png",
                data_point_count=4,
            ),
            DetectedChart(
                chart_id="chart_3",
                chart_index=3,
                title="Répartition par Canal",
                chart_type="pie",
                confidence=0.91,
                bbox=ChartRegion(x=10, y=330, w=400, h=300),
                cropped_image_path="tests/fixtures/chart_3.png",
                data_point_count=3,
            ),
        ],
        image_width=900,
        image_height=700,
    )


def test_multi_chart_detector_segmentation():
    """Verifies MultiChartDetector bounding box segmentation and classification."""
    detector = MultiChartDetector()
    sample_img = Path("data/raw/sample_chart.png")

    detection = detector.detect_charts(sample_img)
    assert detection.total_charts_detected >= 1
    assert len(detection.detected_charts) == detection.total_charts_detected
    for c in detection.detected_charts:
        assert c.chart_id.startswith("chart_")
        assert c.confidence > 0.0
        assert c.bbox.w > 0 and c.bbox.h > 0


def test_multi_chart_fusion_engine_comparative_analytics(mock_detection_result, sample_user_profile):
    """Verifies MultiChartFusionEngine cross-chart comparative analysis and executive briefing."""
    fusion = MultiChartFusionEngine()

    dummy_complexity = ClassificationResult(question="Test", complexity="SIMPLE", is_complex=False, confidence=0.95)

    indiv_results = {
        "chart_1": PipelineResult(
            final_answer="550.7",
            calculation_expression="120.5 + 85.0 + 195.2 + 150.0",
            reasoning="Ventes Q1-Q4",
            extracted_data=ChartExtraction(
                chart_type="bar",
                title="Évolution des Ventes Trimestrielles",
                data_points=[
                    ExtractedDataPoint(label="Q1", value=120.5),
                    ExtractedDataPoint(label="Q2", value=85.0),
                    ExtractedDataPoint(label="Q3", value=195.2),
                    ExtractedDataPoint(label="Q4", value=150.0),
                ],
            ),
            initial_interpretation="Rapport Ventes",
            complexity=dummy_complexity,
        ),
        "chart_2": PipelineResult(
            final_answer="22.5",
            calculation_expression="22.5",
            reasoning="Marge Opérationnelle",
            extracted_data=ChartExtraction(
                chart_type="line",
                title="Marge Opérationnelle (%)",
                data_points=[
                    ExtractedDataPoint(label="Q1", value=18.0),
                    ExtractedDataPoint(label="Q2", value=14.0),
                    ExtractedDataPoint(label="Q3", value=28.0),
                    ExtractedDataPoint(label="Q4", value=22.5),
                ],
            ),
            initial_interpretation="Rapport Marge",
            complexity=dummy_complexity,
        ),
    }

    comparisons, global_summary, global_recs = fusion.fuse_multi_chart_results(
        detection_result=mock_detection_result,
        individual_results=indiv_results,
        user_profile=sample_user_profile,
        target_language="fr",
    )

    assert len(comparisons) >= 1
    assert comparisons[0].source_chart_id == "chart_1"
    assert comparisons[0].target_chart_id == "chart_2"
    assert "Évolution des Ventes Trimestrielles" in comparisons[0].source_title
    assert "SYNTHÈSE DOCUMENTAIRE MULTI-GRAPHIQUES" in global_summary
    assert len(global_recs) >= 1


def test_multi_chart_pipeline_agent_execution(sample_user_profile):
    """Verifies MultiChartPipelineAgent end-to-end multi-chart processing."""
    agent = MultiChartPipelineAgent()
    sample_img = Path("data/raw/sample_chart.png")

    result = agent.process_multi_chart_document(
        image_path=sample_img,
        question="Analyser l'ensemble du document multi-graphiques",
        session_id="multi_test_01",
        target_language="fr",
        user_profile=sample_user_profile,
    )

    assert result.session_id == "multi_test_01"
    assert result.detection_result.total_charts_detected >= 1
    assert len(result.individual_results) >= 1
    assert result.global_summary is not None


def test_multi_chart_pdf_report_generation(mock_detection_result, sample_user_profile):
    """Verifies multi-chart PDF report rendering with Table of Contents and comparative matrix."""
    pdf_gen = PDFReportGenerator()
    fusion = MultiChartFusionEngine()
    dummy_complexity = ClassificationResult(question="Test", complexity="SIMPLE", is_complex=False, confidence=0.95)

    indiv_results = {
        "chart_1": PipelineResult(
            final_answer="550.7",
            calculation_expression="550.7",
            reasoning="Ventes Q1-Q4",
            extracted_data=ChartExtraction(
                chart_type="bar",
                title="Ventes",
                data_points=[ExtractedDataPoint(label="Q1", value=120.5)],
            ),
            initial_interpretation="Interpretation chart 1",
            complexity=dummy_complexity,
        )
    }

    comparisons, global_summary, global_recs = fusion.fuse_multi_chart_results(
        mock_detection_result, indiv_results, sample_user_profile, "fr"
    )

    from src.models.multi_chart import MultiChartPipelineResult
    multi_pipeline_res = MultiChartPipelineResult(
        session_id="pdf_multi_test",
        detection_result=mock_detection_result,
        individual_results=indiv_results,
        cross_chart_comparisons=comparisons,
        global_summary=global_summary,
        global_recommendations=global_recs,
    )

    pdf_bytes = pdf_gen.generate_multi_chart_pdf_bytes(
        multi_result=multi_pipeline_res,
        image_path="data/raw/sample_chart.png",
        execution_latency=1.2,
        target_language="fr",
        user_profile=sample_user_profile,
    )
    assert pdf_bytes is not None
    assert len(pdf_bytes) > 1000


def test_api_multi_chart_endpoints(client):
    """Verifies REST API endpoints /api/charts, /api/charts/{id}, /api/charts/compare."""
    login_res = client.post("/api/auth/login", json={"email": "demo@graphein.ai", "password": "password123"})
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 1. GET /api/charts
    charts_res = client.get("/api/charts", headers=headers)
    assert charts_res.status_code == 200
    det_body = charts_res.json()
    assert det_body["total_charts_detected"] >= 1

    chart_id = det_body["detected_charts"][0]["chart_id"]

    # 2. GET /api/charts/{chart_id}
    detail_res = client.get(f"/api/charts/{chart_id}", headers=headers)
    assert detail_res.status_code == 200
    assert detail_res.json()["chart_id"] == chart_id

    # 3. POST /api/charts/compare
    compare_res = client.post(
        "/api/charts/compare",
        data={"question": "Comparer les graphiques du document"},
        headers=headers,
    )
    assert compare_res.status_code == 200
    comp_body = compare_res.json()
    assert "global_summary" in comp_body
    assert "cross_chart_comparisons" in comp_body
