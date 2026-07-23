"""Central EmailService module for GraphEin AI Enterprise Platform.

Orchestrates template rendering, token signing, async queueing, and multi-provider dispatches.
"""

import os
import logging
from typing import Any

from src.services.email.providers.base import EmailMessage
from src.services.email.providers.factory import EmailProviderFactory
from src.services.email.queue.email_queue import EmailQueue, QueuedEmailJob
from src.services.email.templates.template_renderer import EmailTemplateRenderer
from src.services.email.tokens.invitation_manager import InvitationManager
from src.services.email.tokens.token_service import TokenService

logger = logging.getLogger(__name__)


class EmailService:
    """Centralized Email Infrastructure manager handling all transactional & notification emails for GraphEin AI."""

    def __init__(
        self,
        provider_name: str | None = None,
        token_service: TokenService | None = None,
        invitation_manager: InvitationManager | None = None,
        queue: EmailQueue | None = None,
    ) -> None:
        self.provider = EmailProviderFactory.get_provider(provider_name)
        self.token_service = token_service or TokenService()
        self.invitation_manager = invitation_manager or InvitationManager(self.token_service)
        self.queue = queue or EmailQueue(provider=self.provider)
        self.app_base_url = os.getenv("APP_BASE_URL", "http://localhost:8088")

    def set_provider(self, provider_name: str) -> None:
        """Dynamically switches email provider (e.g., 'maildev', 'resend', 'brevo', 'smtp')."""
        self.provider = EmailProviderFactory.get_provider(provider_name)
        self.queue.set_provider(self.provider)
        logger.info(f"[EmailService] Dynamically switched active provider to '{self.provider.provider_name}'")

    def _dispatch(self, template_name: str, to_email: str, lang: str = "fr", context: dict[str, Any] | None = None) -> QueuedEmailJob:
        """Internal helper to render and queue an email dispatch."""
        subject, html_body, text_body = EmailTemplateRenderer.render(template_name=template_name, lang=lang, context=context)
        msg = EmailMessage(
            to_email=to_email,
            subject=subject,
            html_body=html_body,
            text_body=text_body,
        )
        return self.queue.enqueue(msg)

    # 1. Welcome Email
    def sendWelcomeEmail(self, to_email: str, user_name: str, company: str = "Graphein Corp", role: str = "Standard User", lang: str = "fr") -> QueuedEmailJob:
        ctx = {"user_name": user_name, "company": company, "role": role, "action_url": f"{self.app_base_url}"}
        return self._dispatch("welcome", to_email, lang=lang, context=ctx)

    # 2. Email Verification
    def sendVerificationEmail(self, to_email: str, user_name: str, verification_token: str | None = None, lang: str = "fr") -> QueuedEmailJob:
        tok = verification_token or self.token_service.generate_token("email_verify", email=to_email)
        action_url = f"{self.app_base_url}/verify-email?token={tok}"
        ctx = {"user_name": user_name, "action_url": action_url}
        return self._dispatch("verify_email", to_email, lang=lang, context=ctx)

    # 3. Password Reset
    def sendResetPassword(self, to_email: str, user_name: str, reset_token: str | None = None, lang: str = "fr") -> QueuedEmailJob:
        tok = reset_token or self.token_service.generate_token("password_reset", email=to_email, ttl_seconds=3600)
        action_url = f"{self.app_base_url}/reset-password?token={tok}"
        ctx = {"user_name": user_name, "action_url": action_url}
        return self._dispatch("reset_password", to_email, lang=lang, context=ctx)

    # 4. Workspace Invitation
    def sendWorkspaceInvitation(self, to_email: str, inviter_name: str, workspace_name: str, invitation_token: str | None = None, role: str = "editor", lang: str = "fr") -> QueuedEmailJob:
        tok = invitation_token or self.token_service.generate_token("workspace_invite", email=to_email, role=role)
        action_url = f"{self.app_base_url}/accept-invite?token={tok}"
        ctx = {"inviter_name": inviter_name, "workspace_name": workspace_name, "role": role, "action_url": action_url}
        return self._dispatch("workspace_invitation", to_email, lang=lang, context=ctx)

    # 5. Collaborator Invitation
    def sendCollaboratorInvitation(self, to_email: str, inviter_name: str, workspace_name: str, invitation_token: str | None = None, role: str = "editor", lang: str = "fr") -> QueuedEmailJob:
        return self.sendWorkspaceInvitation(to_email, inviter_name, workspace_name, invitation_token, role, lang)

    # 6. Analysis Shared Notification
    def sendAnalysisShared(self, to_email: str, user_name: str, chart_title: str, action_url: str | None = None, lang: str = "fr") -> QueuedEmailJob:
        url = action_url or f"{self.app_base_url}"
        ctx = {"user_name": user_name, "chart_title": chart_title, "action_url": url}
        return self._dispatch("analysis_shared", to_email, lang=lang, context=ctx)

    # 7. Comment Notification
    def sendCommentNotification(self, to_email: str, user_name: str, commenter_name: str, comment_text: str, chart_title: str = "Chart", workspace_name: str = "Workspace", action_url: str | None = None, lang: str = "fr") -> QueuedEmailJob:
        url = action_url or f"{self.app_base_url}"
        ctx = {"user_name": user_name, "commenter_name": commenter_name, "message": comment_text, "chart_title": chart_title, "workspace_name": workspace_name, "action_url": url}
        return self._dispatch("notification", to_email, lang=lang, context=ctx)

    # 8. Analysis Finished Notification
    def sendAnalysisFinished(self, to_email: str, user_name: str, chart_title: str, confidence: str = "98%", latency: str = "1.2s", action_url: str | None = None, lang: str = "fr") -> QueuedEmailJob:
        url = action_url or f"{self.app_base_url}"
        ctx = {"user_name": user_name, "chart_title": chart_title, "confidence": confidence, "latency": latency, "action_url": url}
        return self._dispatch("analysis_finished", to_email, lang=lang, context=ctx)

    # 9. OTP Security Code
    def sendOTP(self, to_email: str, user_name: str, otp_code: str, lang: str = "fr") -> QueuedEmailJob:
        ctx = {"user_name": user_name, "otp_code": otp_code}
        return self._dispatch("otp", to_email, lang=lang, context=ctx)

    # 10. Password Changed Notification
    def sendPasswordChanged(self, to_email: str, user_name: str, lang: str = "fr") -> QueuedEmailJob:
        ctx = {"user_name": user_name, "message": "Votre mot de passe a été modifié avec succès."}
        return self._dispatch("notification", to_email, lang=lang, context=ctx)

    # 11. Profile Updated Notification
    def sendProfileUpdated(self, to_email: str, user_name: str, lang: str = "fr") -> QueuedEmailJob:
        ctx = {"user_name": user_name}
        return self._dispatch("profile_updated", to_email, lang=lang, context=ctx)

    # 12. Account Created Notification
    def sendAccountCreated(self, to_email: str, user_name: str, lang: str = "fr") -> QueuedEmailJob:
        ctx = {"user_name": user_name}
        return self._dispatch("account_created", to_email, lang=lang, context=ctx)

    # 13. Account Deleted Notification
    def sendAccountDeleted(self, to_email: str, user_name: str, lang: str = "fr") -> QueuedEmailJob:
        ctx = {"user_name": user_name}
        return self._dispatch("account_deleted", to_email, lang=lang, context=ctx)

    # 14. Workspace Created Notification
    def sendWorkspaceCreated(self, to_email: str, user_name: str, workspace_name: str, lang: str = "fr") -> QueuedEmailJob:
        ctx = {"user_name": user_name, "workspace_name": workspace_name}
        return self._dispatch("workspace_created", to_email, lang=lang, context=ctx)

    # 15. Workspace Deleted Notification
    def sendWorkspaceDeleted(self, to_email: str, user_name: str, workspace_name: str, lang: str = "fr") -> QueuedEmailJob:
        ctx = {"user_name": user_name, "workspace_name": workspace_name}
        return self._dispatch("workspace_deleted", to_email, lang=lang, context=ctx)
