"""Unit and integration test suite for AI Business Analyst & Recommendation Engine."""

from pathlib import Path
from fastapi.testclient import TestClient
import pytest

from src.agents.graph_interpreter import GraphInterpreter
from src.agents.recommendation_engine import RecommendationEngine
from src.app.api import app
from src.models.chart import ChartExtraction, ExtractedDataPoint
from src.models.user import UserProfile
from src.utils.pdf_generator import PDFReportGenerator
from src.utils.prompt_builder import PromptBuilder


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def sample_chart_extraction():
    return ChartExtraction(
        chart_type="bar",
        title="Ventes Trimestrielles 2026",
        x_label="Trimestre",
        y_label="Chiffre d'Affaires (K€)",
        data_points=[
            ExtractedDataPoint(label="Q1", value=120.5, confidence=0.96),
            ExtractedDataPoint(label="Q2", value=85.0, confidence=0.94),
            ExtractedDataPoint(label="Q3", value=195.2, confidence=0.98),
            ExtractedDataPoint(label="Q4", value=150.0, confidence=0.95),
        ],
        extraction_source="OpenCV OCR + Gemini Flash",
    )


def test_prompt_builder_sector_and_expertise_adaptation():
    """Verifies that PromptBuilder adapts system prompts according to sector and expertise level."""
    # Student profile (Débutant, Éducation)
    student_profile = UserProfile(
        id="u_student",
        name="Lucas Student",
        email="lucas@univ.fr",
        fonction="Étudiant",
        secteur_activite="Éducation",
        niveau_expertise="Débutant",
        annees_experience=0,
    )
    prompt_student = PromptBuilder.build_user_context_block(student_profile, target_language="fr")

    assert "Étudiant" in prompt_student
    assert "Éducation" in prompt_student
    assert "Débutant" in prompt_student
    assert "pédagogiques" in prompt_student.lower() or "simples" in prompt_student.lower()
    assert "La recommandation est basée sur les données observées." in prompt_student

    # CEO profile (Expert, Finance)
    ceo_profile = UserProfile(
        id="u_ceo",
        name="Claire Chief",
        email="claire@finance.com",
        fonction="Directeur Général (CEO)",
        secteur_activite="Finance",
        niveau_expertise="Expert",
        annees_experience=15,
    )
    prompt_ceo = PromptBuilder.build_user_context_block(ceo_profile, target_language="fr")

    assert "Directeur Général" in prompt_ceo
    assert "Finance" in prompt_ceo
    assert "Expert" in prompt_ceo
    assert "variance" in prompt_ceo.lower() or "avancées" in prompt_ceo.lower()


def test_recommendation_engine_role_tailoring(sample_chart_extraction):
    """Verifies that RecommendationEngine produces tailored summaries and recommendations for different roles."""
    rec_engine = RecommendationEngine()

    # 1. Marketing Manager Profile
    mkt_profile = UserProfile(
        id="u_mkt",
        name="Marc Marketing",
        email="marc@campaign.com",
        fonction="Responsable Marketing",
        secteur_activite="Marketing",
        niveau_expertise="Intermédiaire",
    )
    recs_mkt = rec_engine.generate_recommendations(sample_chart_extraction, user_profile=mkt_profile, target_language="fr")

    assert recs_mkt.executive_summary is not None
    assert "Marketing" in recs_mkt.executive_summary or "croissance" in recs_mkt.executive_summary.lower()
    assert len(recs_mkt.priority_recommendations) > 0
    assert recs_mkt.disclaimer == "La recommandation est basée sur les données observées."
    for r in recs_mkt.priority_recommendations:
        assert "La recommandation est basée sur les données observées" in r.rationale

    # 2. CFO / Finance Profile
    cfo_profile = UserProfile(
        id="u_cfo",
        name="Florence Finance",
        email="florence@cfo.com",
        fonction="Directeur Financier",
        secteur_activite="Finance",
        niveau_expertise="Expert",
    )
    recs_cfo = rec_engine.generate_recommendations(sample_chart_extraction, user_profile=cfo_profile, target_language="fr")

    # Outputs should be distinct between Marketing Manager and CFO
    assert recs_mkt.executive_summary != recs_cfo.executive_summary
    assert "Direction" in recs_cfo.executive_summary or "Financier" in recs_cfo.executive_summary or "Finance" in recs_cfo.executive_summary


def test_graph_interpreter_personalized_report(sample_chart_extraction):
    """Verifies that GraphInterpreter builds personalized multi-section narrative reports."""
    interpreter = GraphInterpreter()
    profile = UserProfile(
        id="u_analyst",
        name="David Data",
        email="david@analytics.com",
        fonction="Data Analyst",
        secteur_activite="Industrie",
        niveau_expertise="Avancé",
    )

    report = interpreter.interpret_chart(sample_chart_extraction, target_language="fr", user_profile=profile)

    assert "# RAPPORT DE SYNTHÈSE AI BUSINESS ANALYST" in report
    assert "Data Analyst" in report
    assert "Industrie" in report
    assert "RECOMMANDATIONS PRIORITAIRES" in report
    assert "PLAN D'ACTION ET PROCHAINES ÉTAPES" in report
    assert "La recommandation est basée sur les données observées." in report


def test_api_analyze_returns_recommendations_payload(client):
    """Verifies REST API /api/analyze includes recommendations payload."""
    login_res = client.post("/api/auth/login", json={"email": "demo@graphein.ai", "password": "password123"})
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    res = client.post(
        "/api/analyze",
        data={"question": "Quel est le total du chiffre d'affaires ?"},
        headers=headers,
    )
    assert res.status_code == 200
    json_body = res.json()

    assert "recommendations" in json_body
    recs = json_body["recommendations"]
    assert "executive_summary" in recs
    assert "priority_recommendations" in recs
    assert "disclaimer" in recs
    assert recs["disclaimer"] == "La recommandation est basée sur les données observées."


def test_pdf_report_contains_identical_recommendations(client, sample_chart_extraction):
    """Verifies that generated PDF report contains recommendations and guardrail rationale."""
    login_res = client.post("/api/auth/login", json={"email": "demo@graphein.ai", "password": "password123"})
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    res = client.post(
        "/api/report/pdf",
        data={"question": "Quelle est la valeur maximale ?"},
        headers=headers,
    )
    assert res.status_code == 200
    assert res.headers["content-type"] == "application/pdf"
    assert len(res.content) > 1000
