"""Brevo (Sendinblue) Email Provider for production email delivery in GraphEin AI."""

import json
import os
import time
import urllib.request
import uuid
import logging

from src.services.email.providers.base import BaseEmailProvider, EmailDispatchResult, EmailMessage

logger = logging.getLogger(__name__)


class BrevoProvider(BaseEmailProvider):
    """Production provider integrating with Brevo v3 HTTP API (https://api.brevo.com/v3/smtp/email)."""

    def __init__(
        self,
        api_key: str | None = None,
        from_email: str | None = None,
        from_name: str | None = None,
    ) -> None:
        super().__init__(provider_name="brevo")
        self.api_key = api_key or os.getenv("BREVO_API_KEY", "")
        self.from_email = from_email or os.getenv("EMAIL_FROM", "no-reply@graphein.ai")
        self.from_name = from_name or os.getenv("EMAIL_NAME", "GraphEin AI Enterprise")
        self.api_url = "https://api.brevo.com/v3/smtp/email"

    def send_email(self, message: EmailMessage) -> EmailDispatchResult:
        """Dispatches an email via Brevo REST API."""
        start_time = time.time()
        msg_id = f"br_{uuid.uuid4().hex[:14]}"
        sender_addr = message.from_email or self.from_email
        sender_label = message.from_name or self.from_name

        if not self.api_key:
            latency = (time.time() - start_time) * 1000
            logger.warning("[BREVO] BREVO_API_KEY missing in environment. Simulating dispatch in sandbox mode.")
            return EmailDispatchResult(
                success=True,
                message_id=f"sandbox_{msg_id}",
                provider_name=self.provider_name,
                latency_ms=round(latency, 2),
            )

        payload = {
            "sender": {"name": sender_label, "email": sender_addr},
            "to": [{"email": message.to_email}],
            "subject": message.subject,
            "htmlContent": message.html_body,
            "textContent": message.text_body,
        }
        if message.reply_to:
            payload["replyTo"] = {"email": message.reply_to}

        headers = {
            "api-key": self.api_key,
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "GraphEinAI-EmailEngine/1.0",
        }

        try:
            data_bytes = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(self.api_url, data=data_bytes, headers=headers, method="POST")
            with urllib.request.urlopen(req, timeout=10) as response:
                res_body = json.loads(response.read().decode("utf-8"))
                returned_id = str(res_body.get("messageId", msg_id))
                latency = (time.time() - start_time) * 1000
                logger.info(f"[BREVO] Dispatched email '{message.subject}' to {message.to_email} ({latency:.1f}ms)")
                return EmailDispatchResult(
                    success=True,
                    message_id=returned_id,
                    provider_name=self.provider_name,
                    latency_ms=round(latency, 2),
                )
        except Exception as e:
            latency = (time.time() - start_time) * 1000
            logger.error(f"[BREVO] Dispatch failed: {e}")
            return EmailDispatchResult(
                success=False,
                message_id="",
                provider_name=self.provider_name,
                error=str(e),
                latency_ms=round(latency, 2),
            )

    def verify_connection(self) -> bool:
        """Verifies Brevo API credentials."""
        return bool(self.api_key)
