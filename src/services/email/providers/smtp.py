"""Generic Enterprise SMTP Email Provider for GraphEin AI."""

import os
import smtplib
import time
import uuid
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from src.services.email.providers.base import BaseEmailProvider, EmailDispatchResult, EmailMessage

logger = logging.getLogger(__name__)


class SMTPProvider(BaseEmailProvider):
    """Generic SMTP provider supporting TLS/SSL authentication and custom ports."""

    def __init__(
        self,
        host: str | None = None,
        port: int | None = None,
        username: str | None = None,
        password: str | None = None,
        use_tls: bool = True,
        from_email: str | None = None,
        from_name: str | None = None,
    ) -> None:
        super().__init__(provider_name="smtp")
        self.host = host or os.getenv("SMTP_HOST", "smtp.gmail.com")
        self.port = port or int(os.getenv("SMTP_PORT", "587"))
        self.username = username or os.getenv("SMTP_USER", "")
        self.password = password or os.getenv("SMTP_PASSWORD", "")
        self.use_tls = use_tls
        self.from_email = from_email or os.getenv("EMAIL_FROM", "no-reply@graphein.ai")
        self.from_name = from_name or os.getenv("EMAIL_NAME", "GraphEin AI Enterprise")

    def send_email(self, message: EmailMessage) -> EmailDispatchResult:
        """Dispatches an email via generic SMTP connection."""
        start_time = time.time()
        msg_id = f"smtp_{uuid.uuid4().hex[:14]}"
        sender_addr = message.from_email or self.from_email
        sender_label = message.from_name or self.from_name

        mime_msg = MIMEMultipart("alternative")
        mime_msg["Subject"] = message.subject
        mime_msg["From"] = f"{sender_label} <{sender_addr}>"
        mime_msg["To"] = message.to_email
        mime_msg["Message-ID"] = f"<{msg_id}@{self.host}>"
        if message.reply_to:
            mime_msg["Reply-To"] = message.reply_to

        mime_msg.attach(MIMEText(message.text_body, "plain", "utf-8"))
        mime_msg.attach(MIMEText(message.html_body, "html", "utf-8"))

        try:
            if self.port == 465:
                server = smtplib.SMTP_SSL(self.host, self.port, timeout=10)
            else:
                server = smtplib.SMTP(self.host, self.port, timeout=10)
                if self.use_tls:
                    server.starttls()

            if self.username and self.password:
                server.login(self.username, self.password)

            server.sendmail(sender_addr, [message.to_email], mime_msg.as_string())
            server.quit()

            latency = (time.time() - start_time) * 1000
            logger.info(f"[SMTP] Dispatched email '{message.subject}' to {message.to_email} ({latency:.1f}ms)")
            return EmailDispatchResult(
                success=True,
                message_id=msg_id,
                provider_name=self.provider_name,
                latency_ms=round(latency, 2),
            )
        except Exception as e:
            latency = (time.time() - start_time) * 1000
            logger.error(f"[SMTP] Dispatch failed: {e}")
            return EmailDispatchResult(
                success=False,
                message_id="",
                provider_name=self.provider_name,
                error=str(e),
                latency_ms=round(latency, 2),
            )

    def verify_connection(self) -> bool:
        """Verifies SMTP server accessibility."""
        try:
            with smtplib.SMTP(self.host, self.port, timeout=3) as server:
                if self.use_tls:
                    server.starttls()
                if self.username and self.password:
                    server.login(self.username, self.password)
            return True
        except Exception:
            return False
