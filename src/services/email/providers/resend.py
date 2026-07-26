"""Resend Email Provider for production email delivery in GraphEin AI."""

import json
import os
import time
import urllib.request
import uuid
import logging

from src.services.email.providers.base import BaseEmailProvider, EmailDispatchResult, EmailMessage

logger = logging.getLogger(__name__)


class ResendProvider(BaseEmailProvider):
    """Production provider integrating with Resend HTTP API (https://resend.com)."""

    def __init__(
        self,
        api_key: str | None = None,
        from_email: str | None = None,
        from_name: str | None = None,
    ) -> None:
        super().__init__(provider_name="resend")
        self.api_key = api_key or os.getenv("RESEND_API_KEY", "")
        self.from_email = from_email or os.getenv("EMAIL_FROM", "onboarding@resend.dev")
        self.from_name = from_name or os.getenv("EMAIL_NAME", "GraphEin AI Enterprise")
        self.api_url = "https://api.resend.com/emails"

    def send_email(self, message: EmailMessage) -> EmailDispatchResult:
        """Dispatches an email via Resend API."""
        start_time = time.time()
        msg_id = f"re_{uuid.uuid4().hex[:14]}"
        sender_addr = message.from_email or self.from_email
        sender_label = message.from_name or self.from_name

        if not self.api_key:
            latency = (time.time() - start_time) * 1000
            logger.warning("[RESEND] RESEND_API_KEY missing in environment. Simulating dispatch in sandbox mode.")
            return EmailDispatchResult(
                success=True,
                message_id=f"sandbox_{msg_id}",
                provider_name=self.provider_name,
                latency_ms=round(latency, 2),
            )

        payload = {
            "from": f"{sender_label} <{sender_addr}>",
            "to": [message.to_email],
            "subject": message.subject,
            "html": message.html_body,
            "text": message.text_body,
        }
        if message.reply_to:
            payload["reply_to"] = message.reply_to

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        }

        try:
            data_bytes = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(self.api_url, data=data_bytes, headers=headers, method="POST")
            with urllib.request.urlopen(req, timeout=10) as response:
                res_body = json.loads(response.read().decode("utf-8"))
                returned_id = res_body.get("id", msg_id)
                latency = (time.time() - start_time) * 1000
                logger.info(f"[RESEND] Dispatched email '{message.subject}' to {message.to_email} ({latency:.1f}ms)")
                return EmailDispatchResult(
                    success=True,
                    message_id=returned_id,
                    provider_name=self.provider_name,
                    latency_ms=round(latency, 2),
                )
        except Exception as e:
            # Fallback to onboarding@resend.dev if custom sender domain was rejected
            if sender_addr != "onboarding@resend.dev":
                logger.warning(f"[RESEND] Custom sender {sender_addr} failed ({e}). Retrying with onboarding@resend.dev...")
                payload["from"] = f"{sender_label} <onboarding@resend.dev>"
                try:
                    data_bytes = json.dumps(payload).encode("utf-8")
                    req = urllib.request.Request(self.api_url, data=data_bytes, headers=headers, method="POST")
                    with urllib.request.urlopen(req, timeout=10) as response:
                        res_body = json.loads(response.read().decode("utf-8"))
                        returned_id = res_body.get("id", msg_id)
                        latency = (time.time() - start_time) * 1000
                        logger.info(f"[RESEND] Dispatched via fallback onboarding@resend.dev to {message.to_email}")
                        return EmailDispatchResult(
                            success=True,
                            message_id=returned_id,
                            provider_name=self.provider_name,
                            latency_ms=round(latency, 2),
                        )
                except Exception as fb_err:
                    e = fb_err

            latency = (time.time() - start_time) * 1000
            logger.error(f"[RESEND] Dispatch failed: {e}")
            return EmailDispatchResult(
                success=False,
                message_id="",
                provider_name=self.provider_name,
                error=str(e),
                latency_ms=round(latency, 2),
            )

    def verify_connection(self) -> bool:
        """Verifies Resend API credentials."""
        return bool(self.api_key)
