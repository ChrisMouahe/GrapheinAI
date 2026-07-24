"""Unit and integration test suite for AnalysisSessionManager, CacheManager, and session lifecycle."""

from pathlib import Path

from fastapi.testclient import TestClient
import pytest

from src.app.api import app
from src.models.session import AnalysisSession, SessionStatus
from src.services.cache_manager import CacheManager
from src.services.session_manager import AnalysisSessionManager


@pytest.fixture
def client():
    return TestClient(app)


def test_analysis_session_model():
    """Verifies AnalysisSession Pydantic v2 schema initialization and defaults."""
    session = AnalysisSession(
        session_id="test_123",
        created_at="2026-07-22 12:00:00",
        file_name="sample_chart.png",
        image_path="data/raw/sample_chart.png",
    )
    assert session.session_id == "test_123"
    assert session.status == SessionStatus.IDLE
    assert session.question_count == 0
    assert session.has_pdf is False
    assert session.interpretation is None


def test_cache_manager_clearing():
    """Verifies CacheManager correctly flushes in-memory and disk caches."""
    cache = CacheManager(cache_dir="data/test_cache")
    cache.set("key_1", "value_1")
    cache.set("key_2", 100)
    assert cache.get("key_1") == "value_1"

    cache.clear_all()
    assert cache.get("key_1") is None
    assert cache.get("key_2") is None


def test_session_manager_lifecycle(tmp_path):
    """Verifies creation, active state tracking, and reopening of isolated sessions."""
    manager = AnalysisSessionManager(storage_dir=tmp_path)
    session1 = manager.create_session(
        image_path="data/raw/sample_chart.png",
        file_name="sample_chart.png",
        target_language="fr",
    )
    assert session1.session_id.startswith("session_")
    assert manager.get_active_session().session_id == session1.session_id

    # Create second session
    session2 = manager.create_session(
        image_path="data/raw/sample_chart2.png",
        file_name="sample_chart2.png",
        target_language="en",
    )
    assert manager.get_active_session().session_id == session2.session_id
    assert session1.session_id != session2.session_id

    # Verify history
    history = manager.get_session_history()
    assert len(history) == 2

    # Reopen session 1
    reopened = manager.reopen_session(session1.session_id)
    assert reopened.session_id == session1.session_id
    assert manager.get_active_session().session_id == session1.session_id


def test_api_session_endpoints(client):
    """Verifies REST endpoints for creating new session, retrieving active session, and listing history."""
    login_res = client.post("/api/auth/login", json={"email": "demo@graphein.ai", "password": "password123"})
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Create session via REST API
    res = client.post("/api/session/new", data={"image_filename": "sample_chart.png", "target_language": "fr"}, headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert "session_id" in data
    session_id = data["session_id"]
    assert data["status"] == "ANALYZED"

    # 2. Get active session
    res_active = client.get("/api/session/active", headers=headers)
    assert res_active.status_code == 200
    active_data = res_active.json()
    assert active_data["session_id"] == session_id

    # 3. Explicit interpretation generation endpoint
    res_interp = client.post("/api/session/interpret", data={"target_language": "fr"}, headers=headers)
    assert res_interp.status_code == 200
    interp_data = res_interp.json()
    assert "interpretation" in interp_data
    assert len(interp_data["interpretation"]) > 20

    # 4. Re-extract session
    res_reextract = client.post("/api/session/reextract", data={"target_language": "fr"}, headers=headers)
    assert res_reextract.status_code == 200
    reext_data = res_reextract.json()
    assert reext_data["message"] == "Ré-extraction effectuée avec succès."

    # 5. History endpoint
    res_hist = client.get("/api/session/history", headers=headers)
    assert res_hist.status_code == 200
    history_list = res_hist.json()
    assert len(history_list) >= 1
    assert history_list[0]["session_id"] == session_id
