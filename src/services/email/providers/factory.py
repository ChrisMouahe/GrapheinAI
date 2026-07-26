"""Email Provider Factory for dynamic provider instantiation in GraphEin AI."""

import os
import logging
from src.services.email.providers.base import BaseEmailProvider
from src.services.email.providers.brevo import BrevoProvider
from src.services.email.providers.maildev import MailDevProvider
from src.services.email.providers.resend import ResendProvider
from src.services.email.providers.smtp import SMTPProvider

logger = logging.getLogger(__name__)


class EmailProviderFactory:
    """Factory creating email provider instances dynamically based on environment configuration."""

    @staticmethod
    def get_provider(provider_name: str | None = None) -> BaseEmailProvider:
        """Instantiates and returns the configured email provider.

        Supports: 'maildev', 'resend', 'brevo', 'smtp'.
        """
        target = (provider_name or os.getenv("EMAIL_PROVIDER", "maildev")).strip().lower()

        if target == "maildev":
            logger.debug("[EmailProviderFactory] Selected MailDev local development provider")
            return MailDevProvider()
        elif target == "resend":
            logger.debug("[EmailProviderFactory] Selected Resend production API provider")
            return ResendProvider()
        elif target == "brevo":
            logger.debug("[EmailProviderFactory] Selected Brevo production API provider")
            return BrevoProvider()
        elif target == "smtp":
            logger.debug("[EmailProviderFactory] Selected Generic SMTP provider")
            return SMTPProvider()
        else:
            logger.warning(f"[EmailProviderFactory] Unknown provider '{target}'. Defaulting to MailDev.")
            return MailDevProvider()
