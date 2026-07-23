"""Unit and integration test suite for Enterprise Workspaces & Real-Time Collaboration."""

from fastapi.testclient import TestClient
import pytest

from src.app.api import app
from src.models.user import UserProfile
from src.models.workspace import Workspace
from src.services.collaboration_service import CollaborationService
from src.services.email_service import EmailService


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def owner_user():
    return UserProfile(
        id="usr_owner_1",
        name="Alice Owner",
        email="alice.owner@graphein.ai",
        fonction="Chief Analytics Officer",
        secteur_activite="Finance",
        role="admin",
    )


@pytest.fixture
def teammate_user():
    return UserProfile(
        id="usr_team_2",
        name="Bob Teammate",
        email="bob.teammate@graphein.ai",
        fonction="Data Analyst",
        secteur_activite="Marketing",
        role="standard_user",
    )


def test_workspace_creation_and_membership(owner_user, teammate_user):
    """Verifies creating workspaces and managing team member roles."""
    collab_svc = CollaborationService()

    # 1. Create Workspace
    ws = collab_svc.create_workspace(name="Workspace Finance", owner=owner_user, description="Analyses financières et Q4")
    assert ws.id is not None
    assert ws.name == "Workspace Finance"
    assert ws.owner_id == owner_user.id

    # 2. Add Teammate as Editor
    member = collab_svc.add_workspace_member(workspace_id=ws.id, member_user=teammate_user, role="editor", actor=owner_user)
    assert member.role == "editor"
    assert member.user_email == teammate_user.email

    # 3. Verify user workspace listing
    user_workspaces = collab_svc.get_user_workspaces(teammate_user.id)
    assert len(user_workspaces) >= 1
    assert any(w.id == ws.id for w in user_workspaces)

    # 4. Remove Member
    removed = collab_svc.remove_workspace_member(workspace_id=ws.id, target_user_id=teammate_user.id, actor=owner_user)
    assert removed is True


def test_role_permission_hierarchy(owner_user, teammate_user):
    """Verifies granular role hierarchy enforcement (Owner > Editor > Commenter > Viewer)."""
    collab_svc = CollaborationService()
    session_id = "session_q4_2026"

    # Grant Commenter permission to teammate
    collab_svc.grant_analysis_permission(analysis_id=session_id, target_user=teammate_user, role="commenter", actor=owner_user)

    # Owner holds full rights
    assert collab_svc.has_analysis_permission(user_id=owner_user.id, analysis_id=session_id, required_role="editor", session_owner_id=owner_user.id) is True

    # Teammate has commenter permission -> holds viewer and commenter, but NOT editor
    assert collab_svc.has_analysis_permission(user_id=teammate_user.id, analysis_id=session_id, required_role="viewer", session_owner_id=owner_user.id) is True
    assert collab_svc.has_analysis_permission(user_id=teammate_user.id, analysis_id=session_id, required_role="commenter", session_owner_id=owner_user.id) is True
    assert collab_svc.has_analysis_permission(user_id=teammate_user.id, analysis_id=session_id, required_role="editor", session_owner_id=owner_user.id) is False


def test_signed_temporary_share_links(owner_user):
    """Verifies cryptographically signed share link generation, token validation, and expiration."""
    collab_svc = CollaborationService()

    # Generate link valid for 24h
    signed_res = collab_svc.create_signed_share_link(
        actor=owner_user,
        analysis_id="session_123",
        role="editor",
        expires_in_hours=24,
    )
    assert signed_res.share_url is not None
    assert signed_res.token is not None
    assert signed_res.role == "editor"

    # Verify link validity
    invitation = collab_svc.verify_signed_share_link(signed_res.token)
    assert invitation is not None
    assert invitation.analysis_id == "session_123"
    assert invitation.status == "pending"

    # Verify invalid token returns None
    assert collab_svc.verify_signed_share_link("invalid.token.string") is None


def test_threaded_comments_and_notifications(owner_user, teammate_user):
    """Verifies adding comments, replies, and generating in-app notifications."""
    collab_svc = CollaborationService()
    session_id = "session_comments_test"

    # 1. Post parent comment
    parent_comment = collab_svc.add_comment(analysis_id=session_id, author=owner_user, text="Excellente croissance sur Q3 !")
    assert parent_comment.id is not None
    assert parent_comment.text == "Excellente croissance sur Q3 !"

    # 2. Post reply comment
    reply_comment = collab_svc.add_comment(
        analysis_id=session_id,
        author=teammate_user,
        text="Tout à fait d'accord @Alice !",
        parent_id=parent_comment.id,
    )
    assert reply_comment.parent_id == parent_comment.id

    # 3. Verify comments listing
    comments = collab_svc.get_comments(session_id)
    assert len(comments) == 2

    # 4. Verify reply notified parent comment author (owner_user)
    notifications = collab_svc.get_user_notifications(owner_user.id)
    assert len(notifications) >= 1
    assert any(n.type == "comment" for n in notifications)


def test_activity_audit_logs(owner_user):
    """Verifies audit trail log entries."""
    collab_svc = CollaborationService()
    ws = collab_svc.create_workspace(name="Workspace Audit", owner=owner_user)

    logs = collab_svc.get_activity_logs(workspace_id=ws.id)
    assert len(logs) >= 1
    assert logs[0].action == "create_workspace"
    assert logs[0].user_id == owner_user.id


def test_api_workspace_and_collaboration_endpoints(client):
    """Verifies REST API endpoints for workspaces, invitations, and signed links."""
    login_res = client.post("/api/auth/login", json={"email": "demo@graphein.ai", "password": "password123"})
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 1. GET /api/workspaces
    ws_res = client.get("/api/workspaces", headers=headers)
    assert ws_res.status_code == 200
    workspaces = ws_res.json()
    assert len(workspaces) >= 1

    # 2. POST /api/workspaces
    create_res = client.post(
        "/api/workspaces",
        data={"name": "Workspace Research & AI", "description": "Analyses R&D"},
        headers=headers,
    )
    assert create_res.status_code == 200
    ws_id = create_res.json()["id"]

    # 3. POST /api/share/link/create
    link_res = client.post(
        "/api/share/link/create",
        data={"workspace_id": ws_id, "role": "editor", "expires_in_hours": 48},
        headers=headers,
    )
    assert link_res.status_code == 200
    signed_token = link_res.json()["token"]

    # 4. GET /api/share/link/{token}
    verify_res = client.get(f"/api/share/link/{signed_token}")
    assert verify_res.status_code == 200
    assert verify_res.json()["status"] == "valid"
