"""Comprehensive test suite for Gemini API Optimization Sprint.

Validates BaseAIService, GeminiService, ChartCacheManager (SHA256), QuestionRouter (AST vs Gemini),
GeminiQuotaManager, Exponential Backoff Retry, Single Extraction Strategy, and /api/gemini/metrics.
"""

import time
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

from src.app.api import app
from src.services.gemini import (
    BaseAIService,
    ChartCacheManager,
    FullChartExtraction,
    GeminiMetricsReport,
    GeminiQuotaManager,
    GeminiService,
    QuestionRouter,
    RouteTarget,
    SeriesData,
    exponential_backoff_retry,
)


@pytest.fixture
def sample_image_bytes() -> bytes:
    """Returns sample dummy image bytes for testing."""
    sample_p = Path("data/raw/sample_chart.png")
    if sample_p.exists():
        return sample_p.read_bytes()
    return b"dummy_image_data_for_sha256_testing_12345"


def test_base_ai_service_interface_and_gemini_service(sample_image_bytes):
    """Verifies that GeminiService inherits from BaseAIService and implements required methods."""
    service = GeminiService()
    assert isinstance(service, BaseAIService)

    extraction = service.extract_chart(sample_image_bytes)
    assert isinstance(extraction, FullChartExtraction)
    assert extraction.type_graphique is not None
    assert extraction.confiance_extraction > 0

    detected_type = service.detect_chart_type(sample_image_bytes)
    assert isinstance(detected_type, str)


def test_chart_cache_manager_sha256_hits_and_misses(sample_image_bytes, tmp_path):
    """Verifies ChartCacheManager SHA256 hashing, cache hits, cache misses, and persistence."""
    cache = ChartCacheManager(cache_dir=tmp_path, cache_filename="test_cache.json")

    # Initial lookup -> Miss
    assert cache.get(sample_image_bytes) is None

    # Store extraction
    ext = FullChartExtraction(
        type_graphique="BAR",
        titre="Test Chart",
        series=[SeriesData(series_name="Series 1", categories=["A", "B"], values=[10.0, 20.0])],
    )
    cache.put(sample_image_bytes, ext)

    # Second lookup -> Hit (0 Gemini calls, 0 latency)
    cached_ext = cache.get(sample_image_bytes)
    assert cached_ext is not None
    assert cached_ext.titre == "Test Chart"
    assert cached_ext.series[0].values == [10.0, 20.0]

    # Re-instantiate from disk -> Hit
    cache2 = ChartCacheManager(cache_dir=tmp_path, cache_filename="test_cache.json")
    cached_ext2 = cache2.get(sample_image_bytes)
    assert cached_ext2 is not None
    assert cached_ext2.titre == "Test Chart"


def test_question_router_ast_routing_vs_gemini():
    """Verifies QuestionRouter correctly routes math questions to AST without Gemini calls."""
    router = QuestionRouter()

    # Math / Statistical queries -> AST_CALCULATOR
    assert router.route_question("Quelle est la moyenne des ventes ?") == RouteTarget.AST_CALCULATOR
    assert router.route_question("Quel est le maximum ?") == RouteTarget.AST_CALCULATOR
    assert router.route_question("Calcule la somme totale") == RouteTarget.AST_CALCULATOR
    assert router.route_question("Quelle est la variation en pourcentage ?") == RouteTarget.AST_CALCULATOR

    # Qualitative / Reasoning queries -> GEMINI_VLM
    assert router.route_question("Quelles sont les causes de la baisse au T1 ?") == RouteTarget.GEMINI_VLM
    assert router.route_question("Compare avec les tendances du secteur financier") == RouteTarget.GEMINI_VLM

    # Test AST Execution
    ext = FullChartExtraction(
        titre="Test AST",
        unites="€",
        series=[SeriesData(series_name="Series 1", categories=["T1", "T2"], values=[100.0, 200.0])],
    )
    res_avg = router.execute_ast_query("Quelle est la moyenne ?", ext)
    assert res_avg is not None
    assert "150.00 €" in res_avg
    assert "déterministe" in res_avg

    res_max = router.execute_ast_query("Quel est le maximum ?", ext)
    assert res_max is not None
    assert "200.00 €" in res_max


def test_gemini_quota_manager_metrics_and_savings():
    """Verifies GeminiQuotaManager accurately records calls, tokens, cache hits, and cost savings ($)."""
    quota = GeminiQuotaManager()

    quota.record_call(input_tokens=600, output_tokens=400, latency_sec=0.35)
    quota.record_cache_hit()
    quota.record_local_routing()
    quota.record_error()

    report = quota.get_report()
    assert isinstance(report, GeminiMetricsReport)
    assert report.total_calls == 1
    assert report.cache_hits == 1
    assert report.avoided_calls == 2
    assert report.total_tokens == 1000
    assert report.total_errors == 1
    assert report.avg_latency_sec == 0.35
    assert report.estimated_cost_saved_usd > 0.0


def test_exponential_backoff_retry():
    """Verifies exponential_backoff_retry decorator retries on 429 transient errors."""
    attempts = 0

    @exponential_backoff_retry(max_retries=3, initial_delay=0.01, backoff_factor=1.5)
    def flaky_api_call():
        nonlocal attempts
        attempts += 1
        if attempts < 3:
            raise Exception("HTTP 429 Rate Limit Exceeded")
        return "SUCCESS"

    res = flaky_api_call()
    assert res == "SUCCESS"
    assert attempts == 3


def test_single_extraction_strategy_and_pdf_reuse():
    """Verifies Single Extraction Strategy produces FullChartExtraction once and reuses interpretation."""
    service = GeminiService()
    ext = service.extract_chart(b"unique_chart_image_bytes_xyz_987")
    assert isinstance(ext, FullChartExtraction)

    # Initial interpretation reuse
    interp = service.generate_interpretation(ext, target_language="fr")
    assert isinstance(interp, str)
    assert len(interp) > 0


def test_gemini_metrics_api_endpoint():
    """Verifies GET /api/gemini/metrics REST endpoint."""
    client = TestClient(app)

    # Login to get admin/user token
    login_res = client.post("/api/auth/login", json={"email": "demo@graphein.ai", "password": "password123"})
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    res = client.get("/api/gemini/metrics", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert "total_calls" in data
    assert "cache_hits" in data
    assert "avoided_calls" in data
    assert "estimated_cost_saved_usd" in data
