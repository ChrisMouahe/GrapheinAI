"""Integration test suite verifying user experience polish, profile editing, email dispatch, and tailored recommendations."""

import pytest
from fastapi.testclient import TestClient

from src.app.api import app, supabase_service, session_manager
from src.models.user import UserProfile
from src.agents.recommendation_engine import RecommendationEngine
from src.models.chart import ChartExtraction, ExtractedDataPoint


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def auth_headers(client):
    res = client.post(
        "/api/auth/login",
        json={"email": "demo@graphein.ai", "password": "password123"},
    )
    assert res.status_code == 200
    token = res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_update_profile_endpoint(client, auth_headers):
    """Verifies profile update endpoint PUT /api/auth/me."""
    update_data = {
        "entreprise": "Acme Finance Corp",
        "fonction": "Directeur Financier",
        "secteur_activite": "Finance",
        "niveau_expertise": "Expert (Directeur/Executive)",
        "annees_experience": 12,
    }
    res = client.put("/api/auth/me", json=update_data, headers=auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["entreprise"] == "Acme Finance Corp"
    assert data["fonction"] == "Directeur Financier"
    assert data["secteur_activite"] == "Finance"


def test_send_report_email_endpoint(client, auth_headers):
    """Verifies PDF report email dispatch endpoint POST /api/report/send-email."""
    payload = {
        "recipient_email": "partner@client.com",
        "question": "Quel est le trimestre le plus performant ?",
    }
    res = client.post("/api/report/send-email", json=payload, headers=auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "sent"
    assert "partner@client.com" in data["message"]


def test_recommendation_engine_tailored_to_profile():
    """Verifies RecommendationEngine generates insights tailored to user function & sector."""
    engine = RecommendationEngine()
    extraction = ChartExtraction(
        chart_type="bar",
        title="Ventes Trimestrielles 2026",
        data_points=[
            ExtractedDataPoint(label="T1", value=150.0),
            ExtractedDataPoint(label="T2", value=280.0),
            ExtractedDataPoint(label="T3", value=210.0),
            ExtractedDataPoint(label="T4", value=390.0),
        ],
    )
    user_fin = UserProfile(
        id="usr_fin",
        email="cfo@fin.com",
        name="Alex Dupont",
        nom="Dupont",
        prenom="Alex",
        entreprise="FinBank",
        fonction="Directeur Financier",
        secteur_activite="Finance",
        niveau_expertise="Expert (Directeur/Executive)",
        annees_experience=15,
    )

    recs = engine.generate_recommendations(extraction=extraction, user_profile=user_fin, target_language="fr")
    assert "Directeur" in recs.executive_summary or "Finance" in recs.executive_summary
    assert len(recs.priority_recommendations) > 0
    assert recs.disclaimer is not None


def test_dashboard_history_for_empty_user(client, auth_headers):
    """Verifies sessions history list for clean state."""
    res = client.get("/api/session/history", headers=auth_headers)
    assert res.status_code == 200
    assert isinstance(res.json(), list)
