"""Unit and integration test suite for Enterprise Identity, Authentication, Route Guards, RBAC, and AI Personalization."""

from pathlib import Path
from fastapi.testclient import TestClient
import pytest

from src.agents.reasoning_agent import ReasoningAgent
from src.app.api import app
from src.models.user import SignupRequest, UserProfile
from src.services.supabase_service import SupabaseService


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def supabase_svc():
    return SupabaseService()


def test_enterprise_user_profile_model():
    """Verifies UserProfile model contains all required enterprise SaaS fields."""
    profile = UserProfile(
        id="test_uuid_123",
        nom="Martin",
        prenom="Sophie",
        name="Sophie Martin",
        email="sophie.martin@finance.com",
        entreprise="Global Capital",
        secteur_activite="Finance",
        secteur_autre="",
        fonction="Financial Analyst",
        niveau_expertise="Expert",
        annees_experience=8,
        langue="fr",
        pays="France",
        role="standard_user",
    )
    assert profile.nom == "Martin"
    assert profile.prenom == "Sophie"
    assert profile.entreprise == "Global Capital"
    assert profile.secteur_activite == "Finance"
    assert profile.niveau_expertise == "Expert"
    assert profile.annees_experience == 8
    assert profile.role == "standard_user"


def test_supabase_service_enterprise_signup_and_login(supabase_svc):
    """Verifies signup and login with enterprise profile fields."""
    signup_req = SignupRequest(
        nom="Dupont",
        prenom="Alex",
        email="alex.dupont@tech.io",
        password="securePassword123",
        password_confirm="securePassword123",
        terms_accepted=True,
        entreprise="Tech Analytics",
        secteur_activite="Autre",
        secteur_autre="Biotechnologies",
        fonction="Data Scientist",
        niveau_expertise="Avancé",
        annees_experience=5,
        pays="France",
        language="fr",
    )

    # Execute signup
    signup_res = supabase_svc.signup(signup_req)
    assert signup_res.access_token is not None
    assert signup_res.user.email == "alex.dupont@tech.io"
    assert signup_res.user.secteur_activite == "Autre"
    assert signup_res.user.secteur_autre == "Biotechnologies"
    assert signup_res.user.niveau_expertise == "Avancé"

    # Execute login
    login_res = supabase_svc.login("alex.dupont@tech.io", "securePassword123")
    assert login_res.access_token is not None
    assert login_res.user.id == signup_res.user.id


def test_route_guards_block_unauthenticated_requests(client):
    """Verifies that protected routes return 401 Unauthorized without Bearer token."""
    protected_endpoints = [
        ("GET", "/api/auth/me"),
        ("GET", "/api/session/active"),
        ("GET", "/api/session/history"),
        ("POST", "/api/session/reextract"),
        ("POST", "/api/session/interpret"),
    ]

    for method, path in protected_endpoints:
        if method == "GET":
            res = client.get(path)
        else:
            res = client.post(path)

        assert res.status_code == 401, f"Endpoint {path} must return 401 Unauthorized when unauthenticated"
        assert "Accès non autorisé" in res.json().get("detail", "") or "required" in res.json().get("detail", "").lower()


def test_authenticated_endpoints_with_bearer_token(client):
    """Verifies that authenticated requests with valid Bearer token succeed."""
    # Login as demo user
    login_res = client.post("/api/auth/login", json={"email": "demo@graphein.ai", "password": "password123"})
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]

    headers = {"Authorization": f"Bearer {token}"}

    # Test GET /api/auth/me
    me_res = client.get("/api/auth/me", headers=headers)
    assert me_res.status_code == 200
    assert me_res.json()["email"] == "demo@graphein.ai"

    # Test GET /api/session/history
    hist_res = client.get("/api/session/history", headers=headers)
    assert hist_res.status_code == 200
    assert isinstance(hist_res.json(), list)


def test_role_based_access_control_rbac(client):
    """Verifies Admin role permissions on /api/admin/users and restriction for standard users."""
    # 1. Signup a standard user
    signup_req = {
        "nom": "User",
        "prenom": "Standard",
        "email": "standard@graphein.ai",
        "password": "Password123",
        "password_confirm": "Password123",
        "terms_accepted": True,
        "entreprise": "Company A",
        "secteur_activite": "Marketing",
        "fonction": "Marketer",
        "niveau_expertise": "Débutant",
        "annees_experience": 1,
        "pays": "France",
        "language": "fr",
    }
    signup_res = client.post("/api/auth/signup", json=signup_req)
    assert signup_res.status_code == 200
    user_token = signup_res.json()["access_token"]

    # Standard user attempts to access /api/admin/users -> 403 Forbidden
    res_forbidden = client.get("/api/admin/users", headers={"Authorization": f"Bearer {user_token}"})
    assert res_forbidden.status_code == 403
    assert "Privilèges Administrateur requis" in res_forbidden.json()["detail"]

    # 2. Login as Demo Admin user -> 200 OK
    login_res = client.post("/api/auth/login", json={"email": "demo@graphein.ai", "password": "password123"})
    admin_token = login_res.json()["access_token"]

    res_admin = client.get("/api/admin/users", headers={"Authorization": f"Bearer {admin_token}"})
    assert res_admin.status_code == 200
    assert isinstance(res_admin.json(), list)
    assert len(res_admin.json()) >= 1


def test_ai_personalization_context_injection():
    """Verifies that user profile metrics are injected into Gemini Flash VLM prompt instructions."""
    profile = UserProfile(
        id="u_perso_123",
        nom="Curie",
        prenom="Marie",
        name="Marie Curie",
        email="marie.curie@science.fr",
        entreprise="Institut du Radium",
        secteur_activite="Santé",
        fonction="Chercheuse",
        niveau_expertise="Expert",
        annees_experience=15,
        langue="fr",
        role="standard_user",
    )

    reasoner = ReasoningAgent()
    prompt = reasoner.build_prompt(
        question="Quelle est la valeur maximale du graphique ?",
        retrieved_examples=[],
        chart_type="bar",
        target_language="fr",
        user_profile=profile,
    )

    assert "### CONTEXTE ET PERSONNALISATION UTILISATEUR ###" in prompt
    assert "Marie Curie" in prompt
    assert "Institut du Radium" in prompt
    assert "Santé" in prompt
    assert "Expert" in prompt
    assert "15 ans" in prompt
    assert "CONSIGNE D'ADAPTATION DE L'IA" in prompt


def test_logout_session_termination(client):
    """Verifies logout invalidates access token and flushes user session context."""
    login_res = client.post("/api/auth/login", json={"email": "demo@graphein.ai", "password": "password123"})
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    logout_res = client.post("/api/auth/logout", headers=headers)
    assert logout_res.status_code == 200
    assert logout_res.json()["status"] == "logged_out"

    # Token should now be invalid
    invalid_res = client.get("/api/auth/me", headers=headers)
    assert invalid_res.status_code == 401
