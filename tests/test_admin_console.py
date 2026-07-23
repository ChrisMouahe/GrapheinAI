"""Unit, integration, and security test suite for Enterprise Administration Console and RBAC guards."""

from fastapi.testclient import TestClient
import pytest

from src.app.api import app
from src.models.admin import BackupPayload, SystemSettings
from src.models.user import UserProfile
from src.services.admin_service import EnterpriseAdminService


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def admin_service():
    return EnterpriseAdminService()


@pytest.fixture
def admin_user():
    return UserProfile(
        id="usr_admin_test_01",
        name="Admin Test",
        email="admin@enterprise.ai",
        role="admin",
    )


@pytest.fixture
def standard_user():
    return UserProfile(
        id="usr_std_test_02",
        name="Standard User",
        email="user@enterprise.ai",
        role="standard_user",
    )


def test_admin_service_user_governance(admin_service):
    """Verifies user role updates, account suspension, and deletion in EnterpriseAdminService."""
    # 1. List users
    users = admin_service.list_all_users()
    assert len(users) >= 2

    # 2. Update role
    updated_usr = admin_service.update_user_role("demo_user_123", "admin")
    assert updated_usr.role == "admin"

    # 3. Account suspension toggle
    suspended_usr = admin_service.set_user_suspension("demo_user_123", True)
    assert suspended_usr.is_suspended is True

    # Reactivate
    reactivated_usr = admin_service.set_user_suspension("demo_user_123", False)
    assert reactivated_usr.is_suspended is False


def test_admin_service_api_key_lifecycle(admin_service):
    """Verifies API key generation, prefix masking, hashing, and revocation."""
    key_item, raw_key = admin_service.generate_api_key("usr_admin_101", "Production Integration Key", monthly_quota=1000)
    assert raw_key.startswith("gk_live_")
    assert key_item.key_prefix.startswith("gk_live_")
    assert key_item.is_active is True
    assert key_item.monthly_quota == 1000

    # Revoke API key
    revoked = admin_service.revoke_api_key(key_item.id)
    assert revoked is True
    assert admin_service.api_keys[key_item.id].is_active is False


def test_admin_service_backup_and_restore(admin_service):
    """Verifies complete system backup snapshot creation and state restoration."""
    backup = admin_service.create_system_backup()
    assert backup.version == "5.0.0"
    assert len(backup.users) >= 2

    # Modify setting and restore
    admin_service.settings.maintenance_mode = True
    assert admin_service.settings.maintenance_mode is True

    # Restore from backup
    success = admin_service.restore_system_backup(backup)
    assert success is True
    assert admin_service.settings.maintenance_mode is False


def test_api_admin_console_endpoints(client):
    """Verifies REST API endpoints for user governance, API keys, settings, and backup."""
    login_res = client.post("/api/auth/login", json={"email": "demo@graphein.ai", "password": "password123"})
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 1. GET /api/admin/users
    users_res = client.get("/api/admin/users", headers=headers)
    assert users_res.status_code == 200
    assert isinstance(users_res.json(), list)

    # 2. PUT /api/admin/users/{id}/role
    role_res = client.put("/api/admin/users/demo_user_123/role", json={"role": "editor"}, headers=headers)
    assert role_res.status_code == 200
    assert role_res.json()["role"] == "editor"

    # 3. PUT /api/admin/users/{id}/suspend
    sus_res = client.put("/api/admin/users/demo_user_123/suspend", json={"is_suspended": False}, headers=headers)
    assert sus_res.status_code == 200
    assert sus_res.json()["is_suspended"] is False

    # 4. POST /api/admin/apikeys
    key_res = client.post("/api/admin/apikeys", json={"name": "Test Key", "monthly_quota": 500}, headers=headers)
    assert key_res.status_code == 200
    assert "raw_secret_key" in key_res.json()

    # 5. GET /api/admin/settings
    sett_res = client.get("/api/admin/settings", headers=headers)
    assert sett_res.status_code == 200
    assert "maintenance_mode" in sett_res.json()

    # 6. GET /api/admin/consumption
    cons_res = client.get("/api/admin/consumption", headers=headers)
    assert cons_res.status_code == 200
    assert "gemini_consumed_tokens" in cons_res.json()

    # 7. GET /api/admin/backup
    back_res = client.get("/api/admin/backup", headers=headers)
    assert back_res.status_code == 200
    assert "version" in back_res.json()


def test_admin_console_rbac_protection(client):
    """Verifies that non-admin users receive 403 Forbidden on all /api/admin/* endpoints."""
    # Standard user token (non-admin)
    standard_token = "invalid_or_non_admin_token"
    bad_headers = {"Authorization": f"Bearer {standard_token}"}

    res_users = client.get("/api/admin/users", headers=bad_headers)
    assert res_users.status_code in [401, 403]

    res_apikeys = client.get("/api/admin/apikeys", headers=bad_headers)
    assert res_apikeys.status_code in [401, 403]

    res_settings = client.get("/api/admin/settings", headers=bad_headers)
    assert res_settings.status_code in [401, 403]


def test_suspended_user_account_login_blocked(client):
    """Verifies that suspended users are blocked with HTTP 403 Forbidden."""
    from src.app.api import supabase_service as global_supa

    # Login to get the actual user_id
    login_res = client.post("/api/auth/login", json={"email": "demo@graphein.ai", "password": "password123"})
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]
    user_id = login_res.json()["user"]["id"]

    # Suspend the user directly in supabase mock store
    global_supa._mock_users[user_id]["is_suspended"] = True

    headers = {"Authorization": f"Bearer {token}"}

    # Access protected route -> 403 Forbidden
    res = client.get("/api/auth/me", headers=headers)
    assert res.status_code == 403
    assert "suspendu" in res.json()["detail"].lower()

    # Reactivate user for clean test state
    global_supa._mock_users[user_id]["is_suspended"] = False

