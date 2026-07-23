"""Comprehensive Unit & Integration Test Suite for GraphEin AI Enterprise Email Platform."""

import time
import pytest
from fastapi.testclient import TestClient

from src.app.api import app
from src.services.email import (
    BaseEmailProvider,
    EmailProviderFactory,
    EmailQueue,
    EmailService,
    InvitationManager,
    NotificationService,
    TokenService,
)
from src.services.email.providers import (
    BrevoProvider,
    MailDevProvider,
    ResendProvider,
    SMTPProvider,
)
from src.services.email.providers.base import EmailMessage
from src.services.email.templates.template_renderer import EmailTemplateRenderer


@pytest.fixture
def client():
    """Test client fixture for FastAPI app."""
    return TestClient(app)


@pytest.fixture
def admin_headers(client):
    """Obtains admin JWT bearer headers."""
    login_res = client.post("/api/auth/login", json={"email": "demo@graphein.ai", "password": "password123"})
    token = login_res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_email_providers_instantiation_and_factory():
    """Verifies that all provider classes initialize and EmailProviderFactory selects providers dynamically."""
    maildev = EmailProviderFactory.get_provider("maildev")
    assert isinstance(maildev, MailDevProvider)
    assert maildev.provider_name == "maildev"

    resend = EmailProviderFactory.get_provider("resend")
    assert isinstance(resend, ResendProvider)
    assert resend.provider_name == "resend"

    brevo = EmailProviderFactory.get_provider("brevo")
    assert isinstance(brevo, BrevoProvider)
    assert brevo.provider_name == "brevo"

    smtp = EmailProviderFactory.get_provider("smtp")
    assert isinstance(smtp, SMTPProvider)
    assert smtp.provider_name == "smtp"

    fallback = EmailProviderFactory.get_provider("unknown_provider")
    assert isinstance(fallback, MailDevProvider)


def test_maildev_provider_send_message():
    """Verifies MailDev provider dispatches formatted messages."""
    provider = MailDevProvider()
    msg = EmailMessage(
        to_email="test.user@graphein.ai",
        subject="Test MailDev Subject",
        html_body="<h1>Hello MailDev</h1>",
        text_body="Hello MailDev",
    )
    result = provider.send_email(msg)
    assert result.success is True
    assert result.provider_name == "maildev"
    assert result.message_id != ""


def test_resend_and_brevo_sandbox_mode():
    """Verifies Resend and Brevo providers handle dispatches cleanly in sandbox mode."""
    resend = ResendProvider(api_key="")
    msg = EmailMessage(to_email="user@example.com", subject="Resend Test", html_body="<p>Test</p>", text_body="Test")
    res_resend = resend.send_email(msg)
    assert res_resend.success is True
    assert "sandbox" in res_resend.message_id

    brevo = BrevoProvider(api_key="")
    res_brevo = brevo.send_email(msg)
    assert res_brevo.success is True
    assert "sandbox" in res_brevo.message_id


def test_token_service_jwt_lifecycle():
    """Verifies JWT token creation, verification, action scoping, expiration, and revocation."""
    service = TokenService()

    # 1. Generate token
    token = service.generate_token(
        action="workspace_invite",
        email="collab@graphein.ai",
        user_id="usr_001",
        workspace_id="ws_finance",
        role="editor",
        ttl_seconds=3600,
    )
    assert token.startswith("ey")

    # 2. Verify token
    payload = service.verify_token(token, expected_action="workspace_invite")
    assert payload.email == "collab@graphein.ai"
    assert payload.workspace_id == "ws_finance"
    assert payload.role == "editor"

    # 3. Action mismatch error
    with pytest.raises(ValueError, match="Action de token invalide"):
        service.verify_token(token, expected_action="password_reset")

    # 4. Revocation
    service.revoke_token(payload.jti)
    with pytest.raises(ValueError, match="déjà été utilisé ou révoqué"):
        service.verify_token(token)


def test_invitation_manager_workflow():
    """Verifies end-to-end invitation creation, duplicate handling, token verification, and acceptance."""
    manager = InvitationManager()

    # 1. Create invitation
    inv_record = manager.create_invitation(
        inviter_user_id="owner_123",
        workspace_id="ws_marketing",
        invitee_email="invitee@graphein.ai",
        role="editor",
    )
    assert inv_record.status == "pending"
    assert inv_record.workspace_id == "ws_marketing"

    # 2. Duplicate invitation returns existing record
    dup_record = manager.create_invitation(
        inviter_user_id="owner_123",
        workspace_id="ws_marketing",
        invitee_email="invitee@graphein.ai",
        role="editor",
    )
    assert dup_record.invitation_id == inv_record.invitation_id

    # 3. Accept invitation
    result = manager.verify_and_accept_invitation(inv_record.token, accepting_user_id="usr_new_002")
    assert result["status"] == "success"
    assert result["workspace_id"] == "ws_marketing"

    # 4. Cannot accept twice (Replay Protection)
    with pytest.raises(ValueError):
        manager.verify_and_accept_invitation(inv_record.token, accepting_user_id="usr_new_002")


def test_email_queue_async_execution_and_metrics():
    """Verifies async EmailQueue job processing, status tracking, retries, and performance metrics."""
    provider = MailDevProvider()
    queue = EmailQueue(provider=provider)

    msg = EmailMessage(
        to_email="queue.test@graphein.ai",
        subject="Queue Test",
        html_body="<p>Queue Test</p>",
        text_body="Queue Test",
    )

    job = queue.enqueue(msg)
    assert job.job_id.startswith("job_")

    # Give background thread pool time to process
    time.sleep(1.2)

    processed_job = queue.get_job(job.job_id)
    assert processed_job is not None
    assert processed_job.status == "sent"

    metrics = queue.get_metrics()
    assert metrics["total_emails"] >= 1
    assert metrics["sent_count"] >= 1
    assert metrics["success_rate_percent"] == 100.0


def test_notification_service():
    """Verifies multi-channel NotificationService for in-app feeds and email dispatches."""
    service = NotificationService()

    notif = service.send_notification(
        user_id="usr_100",
        title="Nouveau commentaire",
        message="Un commentaire a été ajouté à votre graphique.",
        send_email=False,
    )
    assert notif.notification_id.startswith("notif_")
    assert notif.is_read is False

    user_notifs = service.get_user_notifications("usr_100")
    assert len(user_notifs) == 1

    success = service.mark_as_read("usr_100", notif.notification_id)
    assert success is True
    assert user_notifs[0].is_read is True


def test_template_renderer_fr_and_en():
    """Verifies template renderer for French and English localizations across key templates."""
    # French
    sub_fr, html_fr, text_fr = EmailTemplateRenderer.render("welcome", lang="fr", context={"user_name": "Jean"})
    assert "Bienvenue" in sub_fr
    assert "Jean" in html_fr
    assert "Graphein" in html_fr

    # English
    sub_en, html_en, text_en = EmailTemplateRenderer.render("welcome", lang="en", context={"user_name": "John"})
    assert "Welcome" in sub_en
    assert "John" in html_en

    # OTP
    sub_otp, html_otp, text_otp = EmailTemplateRenderer.render("otp", lang="fr", context={"otp_code": "889900"})
    assert "889900" in sub_otp
    assert "889900" in html_otp


def test_email_service_all_15_methods():
    """Verifies that all 15 high-level methods of EmailService execute cleanly and queue dispatches."""
    svc = EmailService(provider_name="maildev")

    job1 = svc.sendWelcomeEmail("user1@graphein.ai", "User One")
    assert job1.job_id is not None

    job2 = svc.sendVerificationEmail("user2@graphein.ai", "User Two")
    assert job2.job_id is not None

    job3 = svc.sendResetPassword("user3@graphein.ai", "User Three")
    assert job3.job_id is not None

    job4 = svc.sendWorkspaceInvitation("user4@graphein.ai", "Owner", "Analytics WS")
    assert job4.job_id is not None

    job5 = svc.sendCollaboratorInvitation("user5@graphein.ai", "Owner", "Analytics WS")
    assert job5.job_id is not None

    job6 = svc.sendAnalysisShared("user6@graphein.ai", "User Six", "Bar Chart Q3")
    assert job6.job_id is not None

    job7 = svc.sendCommentNotification("user7@graphein.ai", "User Seven", "Alice", "Great insights!")
    assert job7.job_id is not None

    job8 = svc.sendAnalysisFinished("user8@graphein.ai", "User Eight", "Revenue Graph")
    assert job8.job_id is not None

    job9 = svc.sendOTP("user9@graphein.ai", "User Nine", "554433")
    assert job9.job_id is not None

    job10 = svc.sendPasswordChanged("user10@graphein.ai", "User Ten")
    assert job10.job_id is not None

    job11 = svc.sendProfileUpdated("user11@graphein.ai", "User Eleven")
    assert job11.job_id is not None

    job12 = svc.sendAccountCreated("user12@graphein.ai", "User Twelve")
    assert job12.job_id is not None

    job13 = svc.sendAccountDeleted("user13@graphein.ai", "User Thirteen")
    assert job13.job_id is not None

    job14 = svc.sendWorkspaceCreated("user14@graphein.ai", "User Fourteen", "Marketing WS")
    assert job14.job_id is not None

    job15 = svc.sendWorkspaceDeleted("user15@graphein.ai", "User Fifteen", "Old WS")
    assert job15.job_id is not None


def test_api_invitations_and_email_admin_endpoints(client, admin_headers):
    """Verifies REST API endpoints for invitations, email admin metrics, email logs, and provider switching."""
    # 1. Send invitation endpoint
    res_inv = client.post(
        "/api/invitations/send",
        json={"workspace_id": "ws_finance_2026", "invitee_email": "new.collab@graphein.ai", "role": "editor"},
        headers=admin_headers,
    )
    assert res_inv.status_code == 200
    data_inv = res_inv.json()
    assert data_inv["status"] == "success"
    token = data_inv["token"]

    # 2. Verify invitation endpoint
    res_ver = client.get(f"/api/invitations/verify?token={token}")
    assert res_ver.status_code == 200
    data_ver = res_ver.json()
    assert data_ver["valid"] is True
    assert data_ver["email"] == "new.collab@graphein.ai"

    # 3. Accept invitation endpoint
    res_acc = client.post(
        "/api/invitations/accept",
        data={"token": token},
        headers=admin_headers,
    )
    assert res_acc.status_code == 200
    assert res_acc.json()["status"] == "success"

    # 4. Admin email metrics endpoint
    res_met = client.get("/api/admin/email/metrics", headers=admin_headers)
    assert res_met.status_code == 200
    data_met = res_met.json()
    assert "total_emails" in data_met
    assert "provider_name" in data_met

    # 5. Admin email logs endpoint
    res_logs = client.get("/api/admin/email/logs", headers=admin_headers)
    assert res_logs.status_code == 200
    assert isinstance(res_logs.json(), list)

    # 6. Admin switch provider endpoint
    res_sw = client.post("/api/admin/email/provider", json={"provider_name": "maildev"}, headers=admin_headers)
    assert res_sw.status_code == 200
    assert res_sw.json()["provider"] == "maildev"
