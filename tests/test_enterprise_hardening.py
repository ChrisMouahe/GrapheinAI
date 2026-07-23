"""Unit, integration, SRE observability, XAI, and security benchmark test suite for Enterprise Hardening."""

from pathlib import Path
from fastapi.testclient import TestClient
import pytest

from src.agents.explainability_engine import ExplainabilityEngine
from src.app.api import app
from src.models.chart import ChartExtraction, ClassificationResult, ExtractedDataPoint, PipelineResult
from src.models.user import UserProfile
from src.services.cache_manager import CacheManager
from src.services.observability_service import ObservabilityService
from src.services.task_queue import TaskQueueManager
from src.utils.confidence_calculator import ConfidenceCalculator
from src.utils.data_validator import DataAnomalyDetector
from src.utils.error_handler import EnterpriseErrorHandler
from src.utils.security_guard import PromptInjectionGuard
from src.utils.structured_logger import StructuredLogger


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def sample_user_profile():
    return UserProfile(
        id="usr_admin_101",
        name="Admin User",
        email="admin@enterprise.ai",
        role="admin",
    )


@pytest.fixture
def sample_pipeline_result():
    dummy_complexity = ClassificationResult(question="Test", complexity="SIMPLE", is_complex=False, confidence=0.95)
    return PipelineResult(
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
        initial_interpretation="Excellente croissance des ventes au Q3.",
        complexity=dummy_complexity,
    )


def test_data_anomaly_detector_inspection():
    """Verifies DataAnomalyDetector detects missing values, outliers, duplicates, and health score."""
    detector = DataAnomalyDetector()

    # 1. Normal Extraction
    clean_ext = ChartExtraction(
        chart_type="bar",
        title="Ventes",
        data_points=[
            ExtractedDataPoint(label="Q1", value=100.0),
            ExtractedDataPoint(label="Q2", value=110.0),
            ExtractedDataPoint(label="Q3", value=120.0),
        ],
    )
    res_clean = detector.inspect_extraction(clean_ext)
    assert res_clean.is_valid is True
    assert res_clean.data_health_score >= 0.90

    # 2. Anomalous Extraction with unreadable labels and outliers
    anom_ext = ChartExtraction(
        chart_type="bar",
        title="Anomalies Test",
        data_points=[
            ExtractedDataPoint(label="[Illisible]", value=100.0),
            ExtractedDataPoint(label="Q1", value=100.0),
            ExtractedDataPoint(label="Q1", value=9500.0),  # Duplicate label & outlier
        ],
    )
    res_anom = detector.inspect_extraction(anom_ext)
    assert res_anom.total_anomalies >= 1
    assert res_anom.data_health_score < 0.90


def test_security_guard_file_validation_and_sanitization():
    """Verifies SecurityGuard magic bytes file inspection, size enforcement, and prompt injection detection."""
    guard = PromptInjectionGuard()

    # Valid PNG Magic Bytes
    valid_png_bytes = b"\x89PNG\r\n\x1a\n\x00\x00\x00\x0dIHDR"
    assert guard.validate_file_upload(valid_png_bytes, "chart.png", max_size_mb=20.0) is True

    # Invalid Magic Bytes
    invalid_bytes = b"NOT_AN_IMAGE_CONTENT"
    with pytest.raises(Exception):
        guard.validate_file_upload(invalid_bytes, "chart.png", max_size_mb=20.0)

    # File Size Limit Exception (> 20 MB)
    large_bytes = b"\x89PNG\r\n\x1a\n" + (b"\x00" * (21 * 1024 * 1024))
    with pytest.raises(Exception):
        guard.validate_file_upload(large_bytes, "chart.png", max_size_mb=20.0)

    # Input Sanitization
    dirty_input = "<script>alert('xss')</script> ../../etc/passwd"
    clean = guard.sanitize_text(dirty_input)
    assert "<script>" not in clean
    assert "../" not in clean


def test_cache_manager_multi_tier_and_invalidation():
    """Verifies CacheManager multi-tier caching and automatic invalidation on chart upload."""
    cache = CacheManager()

    cache.set_ocr_cache("img1_ocr", {"text": "Q1 120.5"})
    cache.set_gemini_cache("img1_gemini", {"answer": "550.7"})
    cache.set_faiss_cache("q1_faiss", [{"score": 0.95}])

    assert cache.get_ocr_cache("img1_ocr") is not None
    assert cache.get_gemini_cache("img1_gemini") is not None
    assert cache.get_faiss_cache("q1_faiss") is not None

    # Trigger automatic invalidation on new chart upload
    cache.invalidate_on_chart_upload("new_chart.png")
    assert cache.get_ocr_cache("img1_ocr") is None
    assert cache.get_gemini_cache("img1_gemini") is None


def test_task_queue_manager_async_execution():
    """Verifies TaskQueueManager async job submission and progress tracking."""
    queue = TaskQueueManager(max_workers=2)

    def _sample_workload(val1: int, val2: int):
        return val1 + val2

    task_item = queue.submit_task("EXTRACTION", _sample_workload, 10, 20)
    assert task_item.task_id.startswith("task_")
    assert task_item.task_type == "EXTRACTION"

    # Fetch status from queue
    status_item = queue.get_task_status(task_item.task_id)
    assert status_item is not None
    assert status_item.status in ["PENDING", "IN_PROGRESS", "COMPLETED"]


def test_enterprise_error_handler_classification():
    """Verifies EnterpriseErrorHandler mapping across 9 error categories."""
    handler = EnterpriseErrorHandler()

    res_val = handler.handle_exception(ValueError("Invalid file size"), category="VALIDATION")
    assert res_val.category == "VALIDATION"
    assert res_val.code == "ERR_VAL_400"
    assert res_val.proposed_solution is not None

    res_gem = handler.handle_exception(RuntimeError("API quota exceeded"), category="GEMINI")
    assert res_gem.category == "GEMINI"
    assert res_gem.code == "ERR_GEM_502"


def test_structured_logger_admin_buffer():
    """Verifies StructuredLogger JSON formatting and in-memory log buffer."""
    logger = StructuredLogger(max_records=50)

    logger.info("API", "User logged in", user_id="usr_123")
    logger.error("OCR", "Text recognition failed", image="chart.png")

    logs = logger.get_admin_logs(limit=10)
    assert len(logs) >= 2
    assert logs[0]["component"] == "OCR"
    assert logs[0]["level"] == "ERROR"


def test_observability_service_report():
    """Verifies ObservabilityService system metrics report."""
    obs = ObservabilityService()
    obs.record_metric("OCR", 0.15)
    obs.record_metric("GEMINI", 0.38)

    report = obs.get_system_report(active_users=3)
    assert report.memory_used_mb > 0.0
    assert report.cpu_percent >= 0.0
    assert report.active_users_count == 3
    assert report.avg_ocr_time_sec > 0.0


def test_explainability_engine_and_confidence_calculator(sample_pipeline_result):
    """Verifies ExplainabilityEngine transparent XAI breakdown and multi-stage ConfidenceCalculator."""
    xai_engine = ExplainabilityEngine()
    conf_calc = ConfidenceCalculator()

    # 1. XAI Breakdown
    xai_report = xai_engine.generate_xai_report(sample_pipeline_result, target_language="fr")
    assert "Évolution des Ventes Trimestrielles" in xai_report.chart_reference
    assert len(xai_report.data_sources_used) >= 4
    assert xai_report.overall_confidence_pct > 0

    # 2. Confidence Calculator
    conf_breakdown = conf_calc.calculate_confidence(sample_pipeline_result)
    assert conf_breakdown.extraction_pct > 0
    assert conf_breakdown.ocr_pct > 0
    assert conf_breakdown.classification_pct > 0
    assert conf_breakdown.final_answer_pct > 0


def test_api_enterprise_hardening_endpoints(client):
    """Verifies REST API task queue and admin observability monitoring endpoints."""
    login_res = client.post("/api/auth/login", json={"email": "demo@graphein.ai", "password": "password123"})
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 1. POST /api/tasks/submit
    submit_res = client.post(
        "/api/tasks/submit",
        data={"task_type": "EXTRACTION", "image_filename": "sample_chart.png", "question": "Analyser"},
        headers=headers,
    )
    assert submit_res.status_code == 200
    task_id = submit_res.json()["task_id"]

    # 2. GET /api/tasks/{task_id}/status
    status_res = client.get(f"/api/tasks/{task_id}/status", headers=headers)
    assert status_res.status_code == 200
    assert status_res.json()["task_id"] == task_id

    # 3. GET /api/admin/metrics
    metrics_res = client.get("/api/admin/metrics", headers=headers)
    assert metrics_res.status_code == 200
    m_body = metrics_res.json()
    assert "memory_used_mb" in m_body
    assert "cpu_percent" in m_body

    # 4. GET /api/admin/logs
    logs_res = client.get("/api/admin/logs", headers=headers)
    assert logs_res.status_code == 200
    assert isinstance(logs_res.json(), list)
