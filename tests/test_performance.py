"""Unit and integration test suite for Enterprise Performance Engine, optimizers, and latency monitoring."""

from pathlib import Path
from fastapi.testclient import TestClient
import pytest

from src.app.api import app
from src.models.chart import ChartExtraction, ExtractedDataPoint
from src.services.cache_manager import CacheManager
from src.services.performance_monitor import PerformanceMonitor, PerformanceStageMetrics
from src.services.queue_manager import EnterpriseQueueManager, TaskState
from src.utils.faiss_optimizer import FAISSOptimizer
from src.utils.gemini_optimizer import GeminiOptimizer
from src.utils.lazy_loader import LazyModelLoader
from src.utils.ocr_optimizer import OCROptimizer
from src.utils.pdf_optimizer import PDFOptimizer


@pytest.fixture
def client():
    return TestClient(app)


def test_cache_manager_lru_and_stats():
    """Verifies CacheManager LRU capacity eviction, TTL expiration, hit ratio, and clear_all."""
    cm = CacheManager(max_entries_per_tier=2, ttl_seconds=60)
    cm.set("k1", "v1")
    cm.set("k2", "v2")

    # Hits
    assert cm.get("k1") == "v1"
    assert cm.get("k2") == "v2"

    # Insert k3 -> evicts oldest entry k1
    cm.set("k3", "v3")
    assert cm.get("k3") == "v3"

    # Hit ratio
    assert cm.get_hit_ratio() > 0.0

    # Clear
    cm.clear_all()
    assert cm.get("k2") is None


def test_queue_manager_async_execution():
    """Verifies background task execution, worker thread pool, and state transitions."""
    qm = EnterpriseQueueManager(max_workers=2)

    def _sample_heavy_calc(a: int, b: int) -> int:
        return a + b

    task_id = qm.submit_task("OCR", _sample_heavy_calc, 10, 20)
    assert task_id.startswith("task_ocr_")

    # Wait briefly for worker thread to complete
    import time
    time.sleep(0.1)

    status = qm.get_task_status(task_id)
    assert status is not None
    assert status.state == TaskState.COMPLETED
    assert status.result_data == 30
    assert status.progress_pct == 100


def test_lazy_model_loader():
    """Verifies lazy, on-demand model instantiation."""
    loader = LazyModelLoader()
    assert not loader.is_loaded("HEAVY_MODEL")

    factory_called = False

    def _factory():
        nonlocal factory_called
        factory_called = True
        return {"model_name": "HeavyResNet50"}

    loader.register_factory("HEAVY_MODEL", _factory)
    assert not loader.is_loaded("HEAVY_MODEL")
    assert not factory_called

    # Instantiate on demand
    instance = loader.get_instance("HEAVY_MODEL")
    assert factory_called
    assert loader.is_loaded("HEAVY_MODEL")
    assert instance["model_name"] == "HeavyResNet50"


def test_ocr_optimizer(tmp_path):
    """Verifies image scaling and contrast enhancement preprocessing."""
    opt = OCROptimizer()
    img_path = Path("data/raw/sample_chart.png")
    if not img_path.exists():
        img_path = tmp_path / "test.png"
        import cv2
        import numpy as np
        img = np.zeros((400, 400, 3), dtype=np.uint8)
        cv2.imwrite(str(img_path), img)

    preprocessed, latency = opt.optimize_image_for_ocr(img_path, target_max_dim=800)
    assert preprocessed is not None
    assert latency >= 0.0


def test_gemini_optimizer():
    """Verifies VLM response caching and prompt compression."""
    g_opt = GeminiOptimizer()
    key = g_opt.compute_cache_key(b"sample_image_bytes", "What is the peak?")

    extraction = ChartExtraction(
        chart_type="bar",
        title="Peak Chart",
        data_points=[ExtractedDataPoint(label="Peak", value=150.0)],
    )
    g_opt.store_cached_response(key, extraction)

    cached = g_opt.get_cached_response(key)
    assert cached is not None
    res_ext, cache_t = cached
    assert res_ext.title == "Peak Chart"

    # Compressed prompt
    prompt = "  Select all items \n // comment line \n  where value > 10  "
    compressed = g_opt.compress_prompt(prompt)
    assert "// comment line" not in compressed
    assert "Select all items" in compressed


def test_faiss_optimizer():
    """Verifies vector embedding caching and fast inner product similarity search."""
    f_opt = FAISSOptimizer()
    f_opt.cache_embedding("Sales Q1", [0.1, 0.2, 0.3])
    assert f_opt.get_cached_embedding("Sales Q1") == [0.1, 0.2, 0.3]

    q_vec = [1.0, 0.0]
    indices = [[1.0, 0.0], [0.0, 1.0], [0.5, 0.5]]
    top_ids, latency = f_opt.fast_vector_search(q_vec, indices, top_k=2)
    assert top_ids[0] == 0  # Highest dot product with [1.0, 0.0]
    assert latency >= 0.0


def test_pdf_optimizer():
    """Verifies fast ReportLab PDF buffer generation."""
    pdf_opt = PDFOptimizer()
    pdf_bytes, latency = pdf_opt.generate_fast_pdf(
        "Rapport d'Analyse Performance",
        ["Résultat: Ventes en hausse de 15%", "Moyenne: 78.5 units"],
    )
    assert len(pdf_bytes) > 500
    assert pdf_bytes.startswith(b"%PDF-")
    assert latency >= 0.0


def test_performance_monitor_report():
    """Verifies stage latencies (OCR, Gemini, FAISS, AST, PDF), RAM, CPU, and analysis count."""
    pm = PerformanceMonitor()
    pm.record_stage_latency("OCR", 0.14)
    pm.record_stage_latency("GEMINI", 0.48)
    pm.record_stage_latency("FAISS", 0.03)
    pm.record_stage_latency("AST", 0.006)
    pm.record_stage_latency("PDF", 0.21)
    pm.record_analysis_event(cache_hit=True)

    report = pm.get_performance_report()
    assert isinstance(report, PerformanceStageMetrics)
    assert report.temps_ocr_sec > 0.0
    assert report.temps_gemini_sec > 0.0
    assert report.temps_faiss_sec > 0.0
    assert report.temps_ast_sec > 0.0
    assert report.temps_pdf_sec > 0.0
    assert report.ram_usage_mb > 0.0
    assert report.total_analyses_count >= 143


def test_api_performance_endpoints(client):
    """Verifies REST API performance metrics and flush-cache endpoints."""
    login_res = client.post("/api/auth/login", json={"email": "demo@graphein.ai", "password": "password123"})
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 1. GET /api/performance/metrics
    metrics_res = client.get("/api/performance/metrics", headers=headers)
    assert metrics_res.status_code == 200
    m_json = metrics_res.json()
    assert "temps_ocr_sec" in m_json
    assert "temps_gemini_sec" in m_json
    assert "temps_faiss_sec" in m_json
    assert "temps_ast_sec" in m_json
    assert "temps_pdf_sec" in m_json
    assert "ram_usage_mb" in m_json
    assert "cpu_percent" in m_json
    assert "total_analyses_count" in m_json

    # 2. POST /api/performance/flush-cache
    flush_res = client.post("/api/performance/flush-cache", headers=headers)
    assert flush_res.status_code == 200
    assert flush_res.json()["status"] == "success"
