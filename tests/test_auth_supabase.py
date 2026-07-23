"""Unit and integration test suite for Supabase Authentication, Profile, and RLS multi-tenancy isolation."""

from fastapi.testclient import TestClient
import pytest

from src.app.api import app
from src.models.user import UserProfile
from src.services.supabase_service import SupabaseService


@pytest.fixture
def client():
    return TestClient(app)


def test_supabase_service_auth_flow():
    """Verifies signup, login, token verification, and profile updates."""
    service = SupabaseService()

    # 1. Signup
    auth_res = service.signup(email="alice@graphein.ai", password="secretpassword", name="Alice Wonderland")
    assert auth_res.access_token is not None
    assert auth_res.user.email == "alice@graphein.ai"
    assert auth_res.user.name == "Alice Wonderland"
    alice_id = auth_res.user.id

    # 2. Login
    login_res = service.login(email="alice@graphein.ai", password="secretpassword")
    assert login_res.access_token is not None
    assert login_res.user.id == alice_id

    # 3. Token verification
    user_prof = service.verify_token(login_res.access_token)
    assert user_prof is not None
    assert user_prof.id == alice_id

    # 4. Profile update
    updated_prof = service.update_profile(user_id=alice_id, name="Alice Smith", language="en")
    assert updated_prof.name == "Alice Smith"
    assert updated_prof.language == "en"


def test_multi_tenant_rls_isolation():
    """Verifies Row Level Security (RLS) data isolation between different users."""
    service = SupabaseService()

    user_a = service.signup(email="usera@graphein.ai", password="password123", name="User A")
    user_b = service.signup(email="userb@graphein.ai", password="password123", name="User B")

    # Create mock session for User A
    from src.models.session import AnalysisSession
    session_a = AnalysisSession(
        session_id="session_user_a_001",
        user_id=user_a.user.id,
        created_at="2026-07-22 14:00:00",
        file_name="chart_a.png",
        image_path="data/raw/chart_a.png",
    )
    service.save_analysis(user_id=user_a.user.id, session=session_a)

    # Verify User A sees 1 analysis
    analyses_a = service.get_user_analyses(user_a.user.id)
    assert len(analyses_a) == 1
    assert analyses_a[0]["session_id"] == "session_user_a_001"

    # Verify User B sees 0 analyses (RLS isolation enforced)
    analyses_b = service.get_user_analyses(user_b.user.id)
    assert len(analyses_b) == 0


def test_api_auth_and_profile_endpoints(client):
    """Verifies REST API endpoints for authentication, profile management, and session history."""
    # 1. Signup endpoint
    res_signup = client.post("/api/auth/signup", json={"email": "bob@graphein.ai", "password": "password123", "name": "Bob Builder"})
    assert res_signup.status_code == 200
    signup_data = res_signup.json()
    token = signup_data["access_token"]
    assert signup_data["user"]["name"] == "Bob Builder"

    # 2. Get Me endpoint with Bearer token
    res_me = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert res_me.status_code == 200
    me_data = res_me.json()
    assert me_data["email"] == "bob@graphein.ai"

    # 3. Update profile endpoint
    res_put = client.put(
        "/api/user/profile",
        json={"name": "Robert Builder", "language": "en"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res_put.status_code == 200
    put_data = res_put.json()
    assert put_data["name"] == "Robert Builder"

    # 4. User history endpoint
    res_hist = client.get("/api/session/history", headers={"Authorization": f"Bearer {token}"})
    assert res_hist.status_code == 200
    assert isinstance(res_hist.json(), list)
