"""MailDev Email Provider for local development in GraphEin AI."""

import os
import smtplib
import time
import uuid
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from src.services.email.providers.base import BaseEmailProvider, EmailDispatchResult, EmailMessage

logger = logging.getLogger(__name__)


class MailDevProvider(BaseEmailProvider):
    """Local development provider sending SMTP emails to MailDev (default localhost:1025)."""

    def __init__(
        self,
        host: str | None = None,
        port: int | None = None,
        from_email: str | None = None,
        from_name: str | None = None,
    ) -> None:
        super().__init__(provider_name="maildev")
        self.host = host or os.getenv("MAILDEV_HOST", "localhost")
        self.port = port or int(os.getenv("MAILDEV_PORT", "1025"))
        self.from_email = from_email or os.getenv("EMAIL_FROM", "no-reply@graphein.ai")
        self.from_name = from_name or os.getenv("EMAIL_NAME", "GraphEin AI Enterprise")

    def send_email(self, message: EmailMessage) -> EmailDispatchResult:
        """Dispatches an email to local MailDev SMTP server."""
        start_time = time.time()
        msg_id = f"md_{uuid.uuid4().hex[:12]}"
        sender_addr = message.from_email or self.from_email
        sender_label = message.from_name or self.from_name

        mime_msg = MIMEMultipart("alternative")
        mime_msg["Subject"] = message.subject
        mime_msg["From"] = f"{sender_label} <{sender_addr}>"
        mime_msg["To"] = message.to_email
        mime_msg["Message-ID"] = f"<{msg_id}@maildev.local>"
        if message.reply_to:
            mime_msg["Reply-To"] = message.reply_to

        mime_msg.attach(MIMEText(message.text_body, "plain", "utf-8"))
        mime_msg.attach(MIMEText(message.html_body, "html", "utf-8"))

        try:
            with smtplib.SMTP(self.host, self.port, timeout=0.5) as server:
                server.sendmail(sender_addr, [message.to_email], mime_msg.as_string())
            latency = (time.time() - start_time) * 1000
            logger.info(f"[MAILDEV] Dispatched email '{message.subject}' to {message.to_email} ({latency:.1f}ms)")
            return EmailDispatchResult(
                success=True,
                message_id=msg_id,
                provider_name=self.provider_name,
                latency_ms=round(latency, 2),
            )
        except Exception as e:
            latency = (time.time() - start_time) * 1000
            logger.warning(f"[MAILDEV] Local SMTP port {self.port} unreachable ({e}). Fallback to dev log mode.")
            # In local dev environment, if MailDev container is not actively listening, log email body cleanly
            logger.info(f"[MAILDEV DEV-LOG] TO: {message.to_email} | SUBJECT: {message.subject}\nBODY: {message.text_body[:200]}...")
            return EmailDispatchResult(
                success=True,
                message_id=f"devlog_{msg_id}",
                provider_name=self.provider_name,
                error=None,
                latency_ms=round(latency, 2),
            )

    def verify_connection(self) -> bool:
        """Verifies connection to local MailDev SMTP server."""
        try:
            with smtplib.SMTP(self.host, self.port, timeout=3) as server:
                server.noop()
            return True
        except Exception:
            return False
