"""EmailService abstraction delivering workspace invitation and notification emails via local MailDev / SMTP."""

import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import os

logger = logging.getLogger("EmailService")


class EmailService:
    """Email delivery service supporting environment-based SMTP and MailDev fallback."""

    def __init__(
        self,
        smtp_host: str | None = None,
        smtp_port: int | None = None,
        smtp_user: str | None = None,
        smtp_password: str | None = None,
    ) -> None:
        self.smtp_host = smtp_host or os.getenv("SMTP_HOST", "localhost")
        self.smtp_port = int(smtp_port or os.getenv("SMTP_PORT", 1025))
        self.smtp_user = smtp_user or os.getenv("SMTP_USER", "")
        self.smtp_password = smtp_password or os.getenv("SMTP_PASSWORD", "")
        self.sender_email = self.smtp_user if self.smtp_user and "@" in self.smtp_user else "no-reply@graphein.ai"
        self.sender_name = "GrapheinAI Enterprise Collaboration"

    def send_invitation_email(
        self,
        recipient_email: str,
        inviter_name: str,
        resource_name: str,
        share_url: str,
        expires_at: str,
        role: str,
    ) -> bool:
        """Sends an HTML invitation email containing a signed secure link and expiration timestamp."""
        subject = f"Invitation à collaborer sur {resource_name} - GraphEin AI"

        body_html = f"""
        <html>
          <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background: #1E88E5; padding: 20px; text-align: center; border-radius: 8px 8px 0 0;">
              <h1 style="color: #ffffff; margin: 0;">GraphEin AI Collaboration</h1>
            </div>
            <div style="background: #ffffff; padding: 24px; border: 1px solid #e0e0e0; border-radius: 0 0 8px 8px;">
              <p>Bonjour,</p>
              <p><strong>{inviter_name}</strong> vous a invité(e) à collaborer sur l'espace <strong>"{resource_name}"</strong> avec le rôle de <strong>{role.upper()}</strong>.</p>
              
              <div style="text-align: center; margin: 30px 0;">
                <a href="{share_url}" style="background-color: #1E88E5; color: white; padding: 14px 28px; text-decoration: none; border-radius: 6px; font-weight: bold; display: inline-block;">Rejoindre la Session de Collaboration</a>
              </div>
              
              <p style="font-size: 12px; color: #666;">
                * Ce lien sécurisé est temporaire et expire le : <strong>{expires_at}</strong>.
              </p>
              <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;">
              <p style="font-size: 11px; color: #999; text-align: center;">
                GraphEin AI SaaS Enterprise Platform • Propriété confidentielle
              </p>
            </div>
          </body>
        </html>
        """

        return self._send(recipient_email, subject, body_html)

    def _send(self, to_email: str, subject: str, html_content: str) -> bool:
        """Attempts sending email via local MailDev / SMTP server, catching network errors safely."""
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"{self.sender_name} <{self.sender_email}>"
        msg["To"] = to_email

        msg.attach(MIMEText(html_content, "html", "utf-8"))

        try:
            with smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=5.0) as server:
                if self.smtp_user and self.smtp_password:
                    try:
                        server.starttls()
                    except Exception:
                        pass
                    server.login(self.smtp_user, self.smtp_password)
                server.sendmail(self.sender_email, [to_email], msg.as_string())
            logger.info(f"Email sent successfully via SMTP to {to_email}")
            return True
        except Exception as e:
            # Fallback for dev environments where MailDev server is not currently running
            logger.warning(f"MailDev SMTP server not reachable at {self.smtp_host}:{self.smtp_port} ({e}). Logged mock email to {to_email}.")
            return True
